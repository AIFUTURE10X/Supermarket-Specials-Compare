"""
Scheduler for automatic catalogue updates.

Runs weekly on Wednesday at 6:00 AM to fetch new specials.
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.catalogue_parser import run_all_parsers, get_all_parsers
from app.services.produce_importer import run_fresh_foods_import
from app.services.salefinder_scraper import run_salefinder_scrape, SaleFinderScraper
from app.services.image_fixer import run_image_fix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store last specials scrape results
last_specials_scrape = {
    "timestamp": None,
    "results": {}
}

# Store last fresh foods import results
last_fresh_foods_import = {
    "timestamp": None,
    "results": {}
}

# Store last SaleFinder scrape results
last_salefinder_scrape = {
    "timestamp": None,
    "results": {}
}

# Store last image fix results
last_image_fix = {
    "timestamp": None,
    "results": {}
}

# Global scheduler instance
scheduler = BackgroundScheduler()

# Store last run results
last_run_results = {
    "timestamp": None,
    "results": []
}


def run_specials_scrape():
    """Job function to scrape weekly specials using Firecrawl."""
    global last_specials_scrape
    import os

    # Only run if Firecrawl API key is configured
    if not os.getenv("FIRECRAWL_API_KEY"):
        logger.warning("FIRECRAWL_API_KEY not set, skipping specials scrape")
        return

    logger.info("Starting scheduled specials scrape...")
    start_time = datetime.now()

    try:
        from app.services.firecrawl_scraper import FirecrawlScraper
        scraper = FirecrawlScraper()

        # Clear expired specials first
        expired = scraper.clear_expired_specials()
        logger.info(f"Cleared {expired} expired specials")

        # Scrape all stores
        results = scraper.scrape_all_stores()

        last_specials_scrape = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "expired_cleared": expired,
            "results": results
        }

        for store, result in results.items():
            if result["status"] == "success":
                logger.info(f"Specials scrape - {store}: {result['items']} items")
            else:
                logger.error(f"Specials scrape - {store}: failed - {result.get('error')}")

        logger.info("Specials scrape completed")

    except Exception as e:
        logger.error(f"Error in specials scrape: {e}")
        last_specials_scrape = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": {},
            "error": str(e)
        }


def run_catalogue_update():
    """Job function to run all catalogue parsers."""
    global last_run_results

    logger.info("Starting scheduled catalogue update...")
    start_time = datetime.now()

    try:
        results = run_all_parsers()
        last_run_results = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": results
        }
        logger.info(f"Catalogue update completed. Results: {results}")
    except Exception as e:
        logger.error(f"Error in catalogue update: {e}")
        last_run_results = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": [],
            "error": str(e)
        }


def run_fresh_foods_update():
    """Job function to import fresh foods (produce and meat) prices."""
    global last_fresh_foods_import

    logger.info("Starting scheduled fresh foods import...")
    start_time = datetime.now()

    try:
        results = run_fresh_foods_import()
        last_fresh_foods_import = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": results
        }
        logger.info(f"Fresh foods import completed. Total: {results.get('total', 0)} products")
    except Exception as e:
        logger.error(f"Error in fresh foods import: {e}")
        last_fresh_foods_import = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": {},
            "error": str(e)
        }


def run_salefinder_update():
    """Job function to scrape specials using SaleFinder API."""
    global last_salefinder_scrape
    from app.config import get_settings

    settings = get_settings()
    if not settings.salefinder_enabled:
        logger.warning("SaleFinder is disabled in settings, skipping scrape")
        return

    logger.info("Starting scheduled SaleFinder scrape...")
    start_time = datetime.now()

    try:
        results = run_salefinder_scrape()
        last_salefinder_scrape = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": results
        }

        for store, result in results.items():
            if result.get("status") == "success":
                logger.info(f"SaleFinder - {store}: {result.get('items', 0)} items")
            else:
                logger.error(f"SaleFinder - {store}: failed - {result.get('error')}")

        logger.info("SaleFinder scrape completed")

    except Exception as e:
        logger.error(f"Error in SaleFinder scrape: {e}")
        last_salefinder_scrape = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": {},
            "error": str(e)
        }


def run_image_fix_update():
    """Job function to fix placeholder images after scraping."""
    global last_image_fix

    logger.info("Starting post-scrape image fix...")
    start_time = datetime.now()

    try:
        results = run_image_fix()
        last_image_fix = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": results
        }

        for store, result in results.items():
            if result.get("status") == "success":
                logger.info(f"Image fix - {store}: fixed {result.get('fixed', 0)} images")
            else:
                logger.error(f"Image fix - {store}: failed - {result.get('error')}")

        logger.info("Image fix completed")

    except Exception as e:
        logger.error(f"Error in image fix: {e}")
        last_image_fix = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": {},
            "error": str(e)
        }


def start_scheduler():
    """Start the background scheduler."""
    if scheduler.running:
        logger.info("Scheduler already running")
        return

    # Weekly update on Wednesday at 6:00 AM
    scheduler.add_job(
        run_catalogue_update,
        CronTrigger(day_of_week='wed', hour=6, minute=0),
        id='weekly_catalogue_update',
        name='Weekly Catalogue Update',
        replace_existing=True
    )

    # Also run on Saturday at 6:00 AM for ALDI's second Special Buys
    scheduler.add_job(
        run_catalogue_update,
        CronTrigger(day_of_week='sat', hour=6, minute=0),
        id='saturday_catalogue_update',
        name='Saturday Catalogue Update (ALDI)',
        replace_existing=True
    )

    # Firecrawl specials scrape on Wednesday at 5:00 AM (before catalogue update)
    scheduler.add_job(
        run_specials_scrape,
        CronTrigger(day_of_week='wed', hour=5, minute=0),
        id='weekly_specials_scrape',
        name='Weekly Specials Scrape (Firecrawl)',
        replace_existing=True
    )

    # Daily fresh foods import at 6:00 AM (produce and meat prices change frequently)
    scheduler.add_job(
        run_fresh_foods_update,
        CronTrigger(hour=6, minute=0),
        id='daily_fresh_foods_import',
        name='Daily Fresh Foods Import',
        replace_existing=True
    )

    # SaleFinder scrape on Wednesday at 5:30 AM (between Firecrawl and catalogue update)
    scheduler.add_job(
        run_salefinder_update,
        CronTrigger(day_of_week='wed', hour=5, minute=30),
        id='weekly_salefinder_scrape',
        name='Weekly SaleFinder Scrape',
        replace_existing=True
    )

    # Image fix on Wednesday at 5:45 AM (after SaleFinder scrape)
    scheduler.add_job(
        run_image_fix_update,
        CronTrigger(day_of_week='wed', hour=5, minute=45),
        id='weekly_image_fix',
        name='Weekly Image Fix',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started with jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  - {job.name}: {job.trigger}")


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def get_scheduler_status():
    """Get current scheduler status."""
    jobs = []
    if scheduler.running:
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "trigger": str(job.trigger),
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            })

    return {
        "running": scheduler.running,
        "jobs": jobs,
        "last_catalogue_run": last_run_results,
        "last_specials_scrape": last_specials_scrape,
        "last_fresh_foods_import": last_fresh_foods_import,
        "last_salefinder_scrape": last_salefinder_scrape,
        "last_image_fix": last_image_fix
    }


def trigger_manual_update(store_slug: str = None):
    """Trigger a manual catalogue update."""
    global last_run_results

    logger.info(f"Manual catalogue update triggered (store: {store_slug or 'all'})")
    start_time = datetime.now()

    try:
        if store_slug:
            # Run specific parser
            parsers = get_all_parsers()
            parser = next((p for p in parsers if p.store_slug == store_slug), None)
            if parser:
                result = parser.run()
                results = [result]
            else:
                return {"error": f"Unknown store: {store_slug}"}
        else:
            # Run all parsers
            results = run_all_parsers()

        last_run_results = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": results,
            "manual": True
        }

        return last_run_results

    except Exception as e:
        logger.error(f"Error in manual update: {e}")
        return {
            "timestamp": start_time.isoformat(),
            "error": str(e)
        }


def trigger_salefinder_update(store_slug: str = None):
    """Trigger a manual SaleFinder scrape."""
    global last_salefinder_scrape

    logger.info(f"Manual SaleFinder scrape triggered (store: {store_slug or 'all'})")
    start_time = datetime.now()

    try:
        scraper = SaleFinderScraper()

        if store_slug:
            # Scrape specific store
            result = scraper.scrape_store(store_slug)
            results = {store_slug: result}
        else:
            # Scrape all stores
            results = scraper.scrape_all_stores()

        last_salefinder_scrape = {
            "timestamp": start_time.isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "results": results,
            "manual": True
        }

        return last_salefinder_scrape

    except Exception as e:
        logger.error(f"Error in manual SaleFinder scrape: {e}")
        return {
            "timestamp": start_time.isoformat(),
            "error": str(e)
        }
