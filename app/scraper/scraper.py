import pickle
import os
import logging
from typing import List, Tuple, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from app.services.post_service import PostService
from app.core.database import get_db
from app.config.config_loader import Config

config = Config()

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class InstagramSelectors:
    # Контейнер для CSS-селекторів та XPath для Instagram
    COOKIE_MODAL = "div._abdc"
    COOKIE_ALLOW_BUTTON = "button._a9--._ap36._a9_0:not(._a9_1)"
    LOGIN_USERNAME = (By.NAME, "username")
    LOGIN_PASSWORD = (By.NAME, "password")
    POST_GRID = "a._a6hd:has(._aagu)"
    COMMENT_COUNT = "li.x972fbf span.html-span"
    POST_DIALOG = "div[role='dialog']"
    LIKES_MODAL = "section.x12nagc.x182iqb8.x1pi30zi.x1swvt13 div.x9f619 a span.x193iq5w span"
    POST_DATE = (By.TAG_NAME, "time")
    TAGS = "a[href^='/explore/tags/']"
    DESCRIPTION = "div.xt0psk2 h1"
    NEXT_BUTTON_XPATH = "//div[contains(@class, '_aaqg') and contains(@class, '_aaqh')]//button"
    SAVE_DATA_MODAL_BUTTON = ".x1i10hfl.x1qjc9v5[role='button']"


class ElementWaits:
    # Утиліта для очікування елементів на сторінці
    def __init__(self, driver: webdriver.Chrome, timeout: int = 15) -> None:
        self.driver = driver
        self.default_timeout = timeout

    def wait(self, condition, locator, timeout: Optional[int] = None) -> Any:
        current_timeout = timeout if timeout is not None else self.default_timeout
        return WebDriverWait(self.driver, current_timeout).until(condition(locator))

    def wait_for_visibility(self, locator, timeout: Optional[int] = None) -> WebElement:
        return self.wait(EC.visibility_of_element_located, locator, timeout)

    def wait_for_clickable(self, locator, timeout: Optional[int] = None) -> WebElement:
        return self.wait(EC.element_to_be_clickable, locator, timeout)


class InstagramDataExtractor:
    # Клас для вилучення даних з елементів поста
    def __init__(self, driver: webdriver.Chrome, waits: ElementWaits) -> None:
        self.driver = driver
        self.waits = waits

    def extract_comment_count_hover(self, post: WebElement) -> str:
        # Вилучає кількість коментарів при наведенні на пост
        try:
            ActionChains(self.driver).move_to_element(post).perform()
            comment_elements = post.find_elements(By.CSS_SELECTOR, InstagramSelectors.COMMENT_COUNT)
            return comment_elements[1].text if len(comment_elements) > 1 else "0"
        except Exception as e:
            logger.exception("Помилка вилучення коментарів")
            return "Помилка вилучення коментарів"

    def extract_likes(self) -> str:
        # Вилучає кількість лайків з модального вікна поста
        try:
            likes_element = self.waits.wait_for_visibility((By.CSS_SELECTOR, InstagramSelectors.LIKES_MODAL))
            return likes_element.text
        except Exception as e:
            logger.exception("Помилка вилучення лайків")
            return "Помилка вилучення лайків"

    def extract_date(self) -> str:
        # Вилучає дату поста
        try:
            time_element = self.waits.wait_for_visibility(InstagramSelectors.POST_DATE)
            date_attr = time_element.get_attribute("datetime")
            return date_attr if date_attr else time_element.text
        except Exception as e:
            logger.exception("Помилка вилучення дати")
            return "Дата не знайдена"

    def extract_tags(self) -> List[str]:
        # Вилучає теги з поста
        try:
            tags_elements = self.driver.find_elements(By.CSS_SELECTOR, InstagramSelectors.TAGS)
            return [tag.text.lstrip("#") for tag in tags_elements]
        except Exception as e:
            logger.exception("Помилка вилучення тегів")
            return []

    def extract_description(self) -> str:
        # Вилучає опис поста
        try:
            description_element = self.waits.wait_for_visibility((By.CSS_SELECTOR, InstagramSelectors.DESCRIPTION))
            return description_element.text
        except Exception as e:
            logger.exception("Помилка вилучення опису")
            return "Опис не знайдено"

    def process_modal_post(self) -> Dict[str, Any]:
        # Збирає дані з модального вікна поста
        return {
            "likes": self.extract_likes(),
            "description": self.extract_description(),
            "tags": self.extract_tags(),
            "date": self.extract_date()
        }


class LoginPage:
    # Page Object для сторінки логіну
    def __init__(self, driver: webdriver.Chrome, waits: ElementWaits) -> None:
        self.driver = driver
        self.waits = waits

    def open(self) -> None:
        self.driver.get("https://www.instagram.com/accounts/login/")

    def handle_cookie_modal(self) -> None:
        # Обробляє модальне вікно cookie, якщо воно з'являється
        try:
            self.waits.wait_for_visibility((By.CSS_SELECTOR, InstagramSelectors.COOKIE_MODAL), timeout=5)
            allow_button = self.waits.wait_for_clickable((By.CSS_SELECTOR, InstagramSelectors.COOKIE_ALLOW_BUTTON), timeout=5)
            allow_button.click()
            logger.info("Оброблено модальне вікно cookie.")
        except Exception:
            logger.info("Модальне вікно cookie не знайдено, продовжуємо.")

    def login(self, username: str, password: str) -> None:
        # Виконує вхід у систему
        self.open()
        self.waits.wait_for_visibility(InstagramSelectors.LOGIN_USERNAME)
        self.handle_cookie_modal()
        username_field = self.driver.find_element(*InstagramSelectors.LOGIN_USERNAME)
        password_field = self.driver.find_element(*InstagramSelectors.LOGIN_PASSWORD)
        username_field.send_keys(username)
        password_field.send_keys(password + Keys.RETURN)
        # Очікування завершення входу
        self.waits.wait_for_visibility((By.CSS_SELECTOR, ".x1xgvd2v.x1o5hw5a.xaeubzz.x1cy8zhl"), timeout=20)


class ProfilePage:
    # Page Object для сторінки профілю
    def __init__(self, driver: webdriver.Chrome, waits: ElementWaits) -> None:
        self.driver = driver
        self.waits = waits

    def open(self, profile_url: str) -> None:
        self.driver.get(profile_url)
        try:
            close_button = self.waits.wait_for_clickable((By.CSS_SELECTOR, InstagramSelectors.SAVE_DATA_MODAL_BUTTON), timeout=10)
            close_button.click()
            logger.info("Закрито модальне вікно 'Зберегти дані'.")
        except Exception:
            logger.info("Модальне вікно 'Зберегти дані' не знайдено.")

    def get_posts(self) -> List[WebElement]:
        # Повертає список елементів постів з сітки профілю
        try:
            self.waits.wait_for_visibility((By.CSS_SELECTOR, InstagramSelectors.POST_GRID))
            return self.driver.find_elements(By.CSS_SELECTOR, InstagramSelectors.POST_GRID)
        except Exception as e:
            logger.exception("Помилка при отриманні постів")
            return []


class PostModalPage:
    # Page Object для модального вікна поста
    def __init__(self, driver: webdriver.Chrome, waits: ElementWaits):
        self.driver = driver
        self.waits = waits
        self.extractor = InstagramDataExtractor(driver, waits)

    def open_post(self, post: WebElement) -> None:
        # Відкриває пост у модальному вікні
        try:
            ActionChains(self.driver).move_to_element(post).pause(0.5).click(post).perform()
            self.waits.wait_for_visibility((By.CSS_SELECTOR, InstagramSelectors.DESCRIPTION))
        except Exception as e:
            logger.exception("Помилка при відкритті поста")
            raise

    def click_next_post(self) -> None:
        # Переходить до наступного поста
        try:
            next_button = self.waits.wait_for_clickable((By.XPATH, InstagramSelectors.NEXT_BUTTON_XPATH), timeout=20)
            ActionChains(self.driver).move_to_element(next_button).click().perform()
            self.waits.wait_for_visibility((By.CSS_SELECTOR, InstagramSelectors.DESCRIPTION), timeout=20)
        except Exception as e:
            logger.exception("Помилка переходу до наступного поста")
            raise

    def process_modal_post(self) -> Dict[str, Any]:
        # Збирає дані з модального вікна поста
        return self.extractor.process_modal_post()


class InstagramScraper:
    # Основний клас скрапера
    def __init__(self, profile_url: str, username: str, password: str,
                 cookies_file: str = "app/scraper/cookies.pkl", headless: bool = True) -> None:
        self.profile_url = profile_url
        self.username = username
        self.password = password
        self.cookies_file = cookies_file
        self.driver = self._init_driver(headless)
        self.waits = ElementWaits(self.driver)
        # Ініціалізація Page Object
        self.login_page = LoginPage(self.driver, self.waits)
        self.profile_page = ProfilePage(self.driver, self.waits)
        self.post_modal_page = PostModalPage(self.driver, self.waits)

    def _init_driver(self, headless: bool) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        if headless:
            options.add_argument("--headless=new")
        try:
            service = webdriver.ChromeService(service_args=['--verbose'])
            driver = webdriver.Chrome(options=options, service=service)
            return driver
        except Exception as e:
            logger.exception("Помилка ініціалізації Chrome")
            raise RuntimeError(f"Помилка ініціалізації Chrome: {e}")

    def load_cookies(self) -> None:
        # Завантажує cookies з файлу або виконує вхід, якщо файл не знайдено
        if not os.path.exists(self.cookies_file):
            logger.info("Файл cookies не знайдено, виконуємо вхід...")
            self.login_and_save_cookies()
        else:
            try:
                with open(self.cookies_file, "rb") as f:
                    cookies = pickle.load(f)
                self.driver.get("https://www.instagram.com/")
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                logger.info("Cookies успішно завантажено.")
            except Exception as e:
                logger.exception("Помилка завантаження cookies")
                self.login_and_save_cookies()

    def login_and_save_cookies(self) -> None:
        # Виконує вхід в Instagram та зберігає cookies у файл
        try:
            logger.info("Розпочинаємо процес входу...")
            self.login_page.login(self.username, self.password)
            with open(self.cookies_file, "wb") as f:
                pickle.dump(self.driver.get_cookies(), f)
            logger.info(f"Cookies збережено у файл: {self.cookies_file}")
        except Exception as e:
            logger.exception("Помилка при вході та збереженні cookies")
            raise

    def collect_grid_data(self, limit: int = 10) -> Tuple[Dict[str, Dict[str, Any]], List[WebElement], List[str]]:
        # Збирає дані з сітки постів до вказаного ліміту
        posts = self.profile_page.get_posts()[:limit]
        grid_data: Dict[str, Dict[str, Any]] = {}
        post_ids: List[str] = []
        for post in posts:
            link = post.get_attribute("href")
            path_part = link.split('?')[0].rstrip('/')
            post_id = path_part.split('/')[-1]
            post_ids.append(post_id)
            grid_data[post_id] = {
                "post_id": post_id,
                "comments": InstagramDataExtractor(self.driver, self.waits).extract_comment_count_hover(post)
            }
        return grid_data, posts, post_ids

    def scrape_posts(self, limit: int = 10) -> None:
        # Основний метод скрапінгу постів та збереження даних у БД
        db = next(get_db())
        try:
            self.load_cookies()
            self.profile_page.open(self.profile_url)
            grid_data, posts, post_ids = self.collect_grid_data(limit)
            if not posts or not post_ids:
                logger.error("Пости не знайдено для обробки")
                return

            # Обробка першого поста
            first_post_id = post_ids[0]
            self.post_modal_page.open_post(posts[0])
            modal_info = self.post_modal_page.process_modal_post()
            grid_data[first_post_id].update(modal_info)
            PostService.create_post(db, grid_data[first_post_id])

            # Обробка наступних постів
            for i in range(1, min(limit, len(post_ids))):
                current_post_id = post_ids[i]
                self.post_modal_page.click_next_post()
                modal_info = self.post_modal_page.process_modal_post()
                grid_data[current_post_id].update(modal_info)
                PostService.create_post(db, grid_data[current_post_id])
        except Exception as e:
            logger.exception("Критична помилка скрапінгу")
            db.rollback()
        finally:
            db.close()
            logger.info("З'єднання з БД закрито")

    def close(self) -> None:
        # Закриває браузер
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    profile_url = "https://www.instagram.com/nasa/"
    username = config.get("instagram", "login")
    password = config.get("instagram", "pass")
    limit = config.get("instagram", "scraper_limit")
    scraper = InstagramScraper(
        profile_url,
        username,
        password,
        cookies_file="app/scraper/cookies.pkl",
        headless=False
    )
    try:
        scraper.scrape_posts(limit)
    except Exception as e:
        logger.exception("Помилка при скрапінгу")
    finally:
        scraper.close()
        logger.info("Scraper закрито.")
