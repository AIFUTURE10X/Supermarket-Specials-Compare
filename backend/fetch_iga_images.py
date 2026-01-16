"""Fetch IGA product images by searching IGA Shop API for missing products."""
import sys
import time
import httpx
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import Store, Special


# IGA Shop API configuration
IGA_STORE_ID = "32600"  # Erskine Park store
IGA_SEARCH_URL = f"https://www.igashop.com.au/api/storefront/stores/{IGA_STORE_ID}/search"


def search_iga_product(product_name: str, client: httpx.Client) -> dict | None:
    """Search IGA Shop API for a product and return barcode/image info."""
    # Clean up product name for search
    # Remove common suffixes that might not match
    search_query = product_name
    for suffix in ['Selected Varieties', 'Selected Variety', 'Various']:
        search_query = search_query.replace(suffix, '').strip()

    # Use first few meaningful words
    words = search_query.split()[:5]
    query = ' '.join(words)

    try:
        params = {
            'q': query,
            'take': 10
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        response = client.get(IGA_SEARCH_URL, params=params, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])

            if items:
                # Try to find best match
                product_name_lower = product_name.lower()

                for item in items:
                    item_name = item.get('name', '').lower()
                    barcode = item.get('barcode')
                    image_data = item.get('image', {})
                    image_url = image_data.get('default') or image_data.get('cell')

                    if not barcode:
                        continue

                    # Check if product names are similar enough
                    # First 3 words should match
                    item_words = item_name.split()[:3]
                    product_words = product_name_lower.split()[:3]

                    if item_words == product_words or item_name in product_name_lower or product_name_lower in item_name:
                        return {
                            'barcode': barcode,
                            'name': item.get('name'),
                            'image_url': image_url,
                            'brand': item.get('brand')
                        }

                # If no good match, return first result
                first_item = items[0]
                barcode = first_item.get('barcode')
                image_data = first_item.get('image', {})

                if barcode:
                    return {
                        'barcode': barcode,
                        'name': first_item.get('name'),
                        'image_url': image_data.get('default') or image_data.get('cell'),
                        'brand': first_item.get('brand'),
                        'partial_match': True
                    }

    except Exception as e:
        print(f"  Error searching for '{query}': {e}")

    return None


def fetch_missing_iga_images():
    """Find IGA products without images and fetch them from IGA Shop API."""
    db = SessionLocal()

    store = db.query(Store).filter(Store.slug == 'iga').first()
    if not store:
        print('ERROR: IGA store not found')
        return

    # Get IGA products without images
    products_without_images = db.query(Special).filter(
        Special.store_id == store.id,
        (Special.image_url == None) | (Special.image_url == '')
    ).all()

    print(f'Found {len(products_without_images)} IGA products without images')

    if not products_without_images:
        print('All IGA products have images!')
        return

    updated = 0
    partial_matches = 0
    not_found = []

    # Track used barcodes to avoid duplicates
    used_barcodes = set()
    existing = db.query(Special.store_product_id).filter(
        Special.store_id == store.id,
        Special.store_product_id != None
    ).all()
    for (barcode,) in existing:
        if barcode:
            used_barcodes.add(barcode)

    with httpx.Client() as client:
        for i, product in enumerate(products_without_images):
            print(f'[{i+1}/{len(products_without_images)}] Searching for: {product.name[:50]}...')

            result = search_iga_product(product.name, client)

            if result and result.get('image_url'):
                product.image_url = result['image_url']
                updated += 1

                if result.get('partial_match'):
                    partial_matches += 1
                    print(f'  [PARTIAL] Found: {result["name"][:40]}')
                else:
                    print(f'  [OK] Found: {result["name"][:40]}')
            else:
                not_found.append(product.name)
                print(f'  [--] Not found')

            # Rate limiting - be nice to IGA's servers
            time.sleep(0.3)

    db.commit()
    db.close()

    print(f'\n=== Summary ===')
    print(f'Updated: {updated} products ({partial_matches} partial matches)')
    print(f'Not found: {len(not_found)} products')

    if not_found:
        print(f'\nProducts not found:')
        for name in not_found[:15]:
            print(f'  - {name}')
        if len(not_found) > 15:
            print(f'  ... and {len(not_found) - 15} more')


if __name__ == '__main__':
    fetch_missing_iga_images()
