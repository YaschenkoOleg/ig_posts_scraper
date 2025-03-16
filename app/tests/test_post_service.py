# app/tests/test_post_service.py
from app.services.post_service import PostService
from app.core.database import get_db
from app.models.post import Post
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_post_service():
    # Получаем сессию БД
    db = next(get_db())
    
    try:
        # Тестовые данные
        test_post = {
            "post_id": "instagram_post_123",
            "comments": "15",
            "likes": "255",
            "description": "Test description",
            "tags": ["test", "demo"]
        }

        # Тест создания поста
        logger.info("1. Тестирование создания поста...")
        created_post = PostService.create_post(db, test_post)
        logger.info(f"Создан пост: ID {created_post.id}, Instagram ID {created_post.post_id}")

        # Тест получения поста
        logger.info("\n2. Тестирование получения поста...")
        fetched_post = PostService.get_post_by_id(db, test_post["post_id"])
        logger.info(f"Получен пост: {fetched_post.description}")

        # Тест обновления поста
        logger.info("\n3. Тестирование обновления поста...")
        updated_data = {"likes": "300", "description": "Updated description"}
        updated_post = PostService.update_post(db, test_post["post_id"], updated_data)
        logger.info(f"Обновлены поля: likes={updated_post.likes}, description={updated_post.description}")

        # Тест удаления поста
        #logger.info("\n4. Тестирование удаления поста...")
        #delete_result = PostService.delete_post(db, test_post["post_id"])
        #logger.info(f"Результат удаления: {'Успешно' if delete_result else 'Неудачно'}")
#
        ## Проверка, что пост удалён
        #logger.info("\n5. Проверка что пост удалён...")
        #deleted_post = PostService.get_post_by_id(db, test_post["post_id"])
        #logger.info(f"Пост в базе: {'Найден' if deleted_post else 'Не найден'}")

    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка теста: {str(e)}")
    finally:
        db.close()
        logger.info("\nТест завершён. Сессия БД закрыта.")

if __name__ == "__main__":
    test_post_service()