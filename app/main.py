from fastapi import FastAPI
from app.api.post_router import router as post_router
from app.core.database import engine, Base

app = FastAPI()

# Створюємо таблицю, якщо її немає
Base.metadata.create_all(bind=engine)

app.include_router(post_router)
