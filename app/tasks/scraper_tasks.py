from app.celery_app import celery_app
from app.scraper.scraper import InstagramScraper
from app.config.config_loader import Config


config = Config()

@celery_app.task(name="app.tasks.scraper_tasks.run_scraper") # Додаєму задачу
def run_scraper():
    profile_url = "https://www.instagram.com/nasa/"
    username = config.get("instagram", "login")
    password = config.get("instagram", "pass")
    limit = config.get("instagram", "scraper_limit")
    cookies_file = config.get("paths", "cookies_file")
    scraper = InstagramScraper(profile_url, username, password, cookies_file=cookies_file, headless=True)
    try:
        scraper.scrape_posts(limit)
    except Exception as e:
        print(f"Помилка при скрапінгу: {e}")
    finally:
        scraper.close()
