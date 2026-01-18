from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

# SQLite needs different config than PostgreSQL
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and seed default data."""
    Base.metadata.create_all(bind=engine)

    # Seed default stores if none exist
    from app.models import Store
    db = SessionLocal()
    try:
        if db.query(Store).count() == 0:
            print("Seeding default stores...")
            default_stores = [
                Store(name="Woolworths", slug="woolworths", logo_url="https://www.woolworths.com.au/static/wowlogo/logo.svg", website_url="https://www.woolworths.com.au", specials_day="wednesday"),
                Store(name="Coles", slug="coles", logo_url="https://www.coles.com.au/content/dam/coles/coles-logo.svg", website_url="https://www.coles.com.au", specials_day="wednesday"),
                Store(name="ALDI", slug="aldi", logo_url="https://www.aldi.com.au/static/aldi/logo.svg", website_url="https://www.aldi.com.au", specials_day="wednesday"),
                Store(name="IGA", slug="iga", logo_url="https://www.iga.com.au/sites/default/files/IGA_Logo.png", website_url="https://www.iga.com.au", specials_day="wednesday"),
            ]
            for store in default_stores:
                db.add(store)
            db.commit()
            print(f"Seeded {len(default_stores)} stores")
    finally:
        db.close()
