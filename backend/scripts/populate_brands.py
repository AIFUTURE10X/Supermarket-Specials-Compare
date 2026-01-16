"""
Populate Brands Script

Extracts and populates brand names from product names for all existing specials.
This enables the "Same Brand Across Stores" comparison feature to work properly.

Run with: python -m scripts.populate_brands
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import Special
from app.services.brand_extractor import extract_brand_from_name, extract_size_from_name


def populate_brands(dry_run: bool = False):
    """
    Populate brand and size fields for all specials.

    Args:
        dry_run: If True, only preview changes without saving
    """
    print("Populating brand data for all products...")
    print("=" * 60)

    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Get all specials
        specials = db.query(Special).all()
        total = len(specials)
        print(f"Found {total} specials to process")
        print("-" * 60)

        # Stats tracking
        stats = {
            "brand_extracted": 0,
            "brand_already_set": 0,
            "brand_not_found": 0,
            "size_extracted": 0,
            "size_already_set": 0,
            "brands_found": {},
        }

        for i, special in enumerate(specials, 1):
            # Extract brand
            if special.brand:
                stats["brand_already_set"] += 1
            else:
                brand = extract_brand_from_name(special.name)
                if brand:
                    stats["brand_extracted"] += 1
                    stats["brands_found"][brand] = stats["brands_found"].get(brand, 0) + 1
                    if not dry_run:
                        special.brand = brand
                else:
                    stats["brand_not_found"] += 1

            # Extract size if not set
            if not special.size:
                size = extract_size_from_name(special.name)
                if size:
                    stats["size_extracted"] += 1
                    if not dry_run:
                        special.size = size
            else:
                stats["size_already_set"] += 1

            # Progress indicator
            if i % 200 == 0:
                print(f"  Processed {i}/{total} products...")

        if not dry_run:
            db.commit()
            print("-" * 60)
            print("\nBrand population complete!")
        else:
            print("-" * 60)
            print("\n[DRY RUN] No changes made to database")

        print(f"\nStatistics:")
        print(f"  Total processed: {total}")
        print(f"  Brand extracted: {stats['brand_extracted']}")
        print(f"  Brand already set: {stats['brand_already_set']}")
        print(f"  Brand not found: {stats['brand_not_found']}")
        print(f"  Size extracted: {stats['size_extracted']}")
        print(f"  Size already set: {stats['size_already_set']}")

        # Show top brands found
        if stats["brands_found"]:
            print(f"\nTop 20 brands found:")
            sorted_brands = sorted(stats["brands_found"].items(), key=lambda x: -x[1])
            for brand, count in sorted_brands[:20]:
                print(f"  {brand}: {count}")

        # Show sample products without brand
        if stats["brand_not_found"] > 0:
            print(f"\nSample products without brand (first 10):")
            no_brand = db.query(Special).filter(Special.brand.is_(None)).limit(10).all()
            for special in no_brand:
                print(f"  - {special.name[:60]}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def show_brand_stats():
    """Show current brand statistics without making changes."""
    print("Current brand statistics...")
    print("=" * 60)

    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        total = db.query(Special).count()
        with_brand = db.query(Special).filter(Special.brand.isnot(None)).count()
        with_size = db.query(Special).filter(Special.size.isnot(None)).count()

        print(f"Total products: {total}")
        print(f"Products with brand: {with_brand} ({100*with_brand/total:.1f}%)")
        print(f"Products with size: {with_size} ({100*with_size/total:.1f}%)")

        if with_brand > 0:
            print("\nExisting brands in database:")
            brands = db.query(Special.brand).filter(Special.brand.isnot(None)).distinct().all()
            for (brand,) in brands[:20]:
                count = db.query(Special).filter(Special.brand == brand).count()
                print(f"  {brand}: {count}")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Populate brand data for products")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without saving")
    parser.add_argument("--stats", action="store_true", help="Show current statistics only")
    args = parser.parse_args()

    if args.stats:
        show_brand_stats()
    else:
        populate_brands(dry_run=args.dry_run)
