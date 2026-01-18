# Trolley Saver (Supermarket Specials Compare)

## Quick Start
Run `start-dev.bat` to start both frontend and backend servers:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## Project Structure
- `frontend/` - React + Vite + TailwindCSS app
- `backend/` - FastAPI Python backend

## Deployment
- **Backend**: Railway (https://trolleysaver-production.up.railway.app)
  - PostgreSQL database (persistent)
  - Auto-deploys on push to main branch
- **Frontend**: Vercel (https://trolleysaver-au.vercel.app)
  - Auto-deploys on push to main branch
  - Uses `VITE_API_BASE_URL` env var for API endpoint

## Database
- **Production**: PostgreSQL on Railway (data persists across deployments)
- **Local**: SQLite at `backend/specials.db`
- Contains specials from Woolworths, Coles, ALDI, and IGA
- Current counts (as of Jan 18, 2026): ~1943 total specials

## API Endpoints
- `GET /api/stores` - List all stores
- `GET /api/specials` - List specials with filtering
- `GET /api/specials/stats` - Get specials statistics
- `GET /api/staples` - Fresh food staples from specials
- `GET /api/staples/categories` - Staples category list
- `GET /api/compare/fresh-foods` - Price comparison across stores
- `POST /api/import-specials` - Import specials (JSON array)

## Importing Specials to Production
```bash
cd backend
curl -X POST "https://trolleysaver-production.up.railway.app/api/import-specials" \
  -H "Content-Type: application/json" \
  -d @specials_export.json
```

Note: For large imports (2000+ records), split into chunks of 100 to avoid timeouts.

## IGA Image Fetching
- Script: `backend/fetch_iga_images.py`
- IGA Shop API: `https://www.igashop.com.au/api/storefront/stores/{STORE_ID}/search?q={query}&take=10`
- Store ID for Erskine Park: `32600`
- Run with: `cd backend && python fetch_iga_images.py`

## Browser Testing Guidelines
- Prefer `browser_take_screenshot` over `browser_snapshot` to reduce context usage
- Only use `browser_snapshot` when you need to interact with elements
- Screenshots are ~1k tokens, snapshots are ~10k tokens

## Key Files
- `backend/app/database.py` - DB setup, seeds stores and categories on startup
- `backend/app/routers/staples.py` - Staples page API (uses specials with keyword matching)
- `backend/app/routers/compare.py` - Compare page API (fresh food price comparison)
- `backend/app/routers/admin.py` - Import endpoints
- `frontend/src/App.tsx` - React router setup
