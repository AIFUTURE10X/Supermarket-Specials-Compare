# Supermarket Specials Compare

## Quick Start
Run `start-dev.bat` to start both frontend and backend servers:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Project Structure
- `frontend/` - React + Vite + TailwindCSS app
- `backend/` - FastAPI Python backend with SQLite database

## Browser Testing Guidelines
- Prefer `browser_take_screenshot` over `browser_snapshot` to reduce context usage
- Only use `browser_snapshot` when you need to interact with elements (clicking, typing, etc.)
- Screenshots are ~1k tokens, snapshots are ~10k tokens

## Database
- SQLite database at `backend/specials.db`
- Contains specials from Woolworths, Coles, ALDI, and IGA
- Current counts (as of Jan 2026): ~1051 total specials (386 Woolworths, 217 Coles, 346 ALDI, 102 IGA)

## IGA Image Fetching
- Script: `backend/fetch_iga_images.py` - searches IGA Shop API to find images for IGA products
- IGA Shop API: `https://www.igashop.com.au/api/storefront/stores/{STORE_ID}/search?q={query}&take=10`
- Store ID for Erskine Park: `32600`
- Image URL pattern: `https://cdn.metcash.media/image/upload/f_auto,c_limit,w_750,q_auto/igashop/images/{barcode}_0.jpg`
- Run with: `cd backend && python fetch_iga_images.py`

## Useful Database Queries
```python
# Check products without images
import sqlite3
conn = sqlite3.connect('backend/specials.db')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM specials WHERE store_id = (SELECT id FROM stores WHERE slug = 'iga') AND (image_url IS NULL OR image_url = '')")
print(cur.fetchone()[0])
```

## Session Notes
- All IGA products now have images (102 products as of Jan 17, 2026)
- Products without available images in IGA Shop were removed from the database
