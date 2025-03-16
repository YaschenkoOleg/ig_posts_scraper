import time
from fastapi import FastAPI
from app.api.post_router import router as post_router
from app.core.database import engine, Base
from app.tasks.scraper_tasks import run_scraper

app = FastAPI()

# Створюємо таблицю, якщо її немає
Base.metadata.create_all(bind=engine)

app.include_router(post_router)



@app.on_event("startup")
async def startup_event():
    # Запуск задачi скрапiнгу на етапi запуску контейнера
    time.sleep(10)
    run_scraper.apply_async()