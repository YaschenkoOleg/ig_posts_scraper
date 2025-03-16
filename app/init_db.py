# D:\P\ig_posts\app\init_db.py
# Створює таблицю з постами
import logging
from app.core.database import engine, Base
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

def wait_for_db():
    while True:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database is ready!")
                break
        except OperationalError:
            logger.warning("Database not available, retrying in 5 seconds...")
            time.sleep(5)

def create_tables():
    wait_for_db()
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created!")

create_tables()
