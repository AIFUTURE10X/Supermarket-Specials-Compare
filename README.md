# Supermarket Specials Compare

Compare weekly specials across Australian supermarkets - Woolworths, Coles, ALDI, and IGA.

## Features

- Browse specials from multiple stores in one place
- Smart categorization system (17 main categories, 100+ subcategories)
- Category-aware search (search "sauce" to find sauces, not tuna in sauce)
- Price comparison tools
- Filter by discount percentage, store, and category

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### Running the Application

```batch
start-dev.bat
```

This starts both servers:
- **Frontend**: http://localhost:3000 (React + Vite + TailwindCSS)
- **Backend**: http://localhost:8000 (FastAPI + SQLite)

### Manual Start

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
├── backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── models/    # SQLAlchemy models
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic (scrapers, categorizer)
│   │   └── schemas/   # Pydantic schemas
│   └── scripts/       # Database seeding scripts
├── frontend/          # React + Vite frontend
│   └── src/
│       ├── components/
│       └── pages/
└── docker/            # Docker setup (not currently used)
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Vite, TailwindCSS, TypeScript
- **Scraping**: Firecrawl API

## Note on Docker

The `docker/` folder contains an alternative setup using the [aus_grocery_price_database](https://github.com/tjhowse/aus_grocery_price_database) project. **This is not currently used.** The application runs directly with Python and Node.js as described above.
