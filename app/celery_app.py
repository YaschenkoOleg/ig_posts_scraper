from celery import Celery
from app.config.config_loader import Config

config = Config()

def make_celery():

    broker_url = config.get('celery', 'broker_url')
    result_backend = config.get('celery', 'result_backend')
    app = Celery('ig_posts', broker=broker_url)
    app.conf.update(
        result_backend=result_backend,
        beat_schedule={
            "run-scraper-every-10-min": {
                "task": "app.tasks.scraper_tasks.run_scraper",
                "schedule": 600.0, # виконання кожнi 10 хвилин
            },
        },
    )
    return app

celery_app = make_celery()


import app.tasks.scraper_tasks
