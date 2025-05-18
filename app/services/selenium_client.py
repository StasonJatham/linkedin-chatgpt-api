# app/services/selenium_client.py

from pathlib import Path
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

def init_driver(user_data_dir: Path) -> webdriver.Chrome:
    """Initialisiert und returniert einen Chrome WebDriver."""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument(f"--user-data-dir={str(user_data_dir.resolve())}")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get("https://chatgpt.com/")
    # Hier könntest du automatisches Login einbauen oder
    # für das manuelle Login einen Hook / Callback definieren.
    return driver

class ChatGPTClient:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.ensure_login()

    def is_logged_in(self) -> bool:
        """
        TODO: Hier prüfen, ob du wirklich eingeloggt bist.
        Z. B. nach dem Avatar-Button suchen:
          return bool(self.driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="user-menu-button"]'))
        """
        return True  # Platzhalter

    def ensure_login(self):
        # TODO: will ich auch noch stabiler bauen das nicht alles stehen muss.
        """Wenn nicht eingeloggt, warte auf manuelles Login via Konsole."""
        if not self.is_logged_in():
            print("⏳ Bitte logge dich im Browser-Fenster ein und drücke [Enter]…")
            input()
            if not self.is_logged_in():
                raise RuntimeError("Login fehlgeschlagen – bitte erneut einloggen.")
            
    def set_message(self, message: str):
        logger.info(f"📨 Sende Nachricht: {message}")
        self.driver.execute_script(
            "document.querySelector('#prompt-textarea > p').innerHTML = arguments[0];",
            message
        )

    def get_new_chat(self, model:str="gpt-4o",tmp:bool=True):
        # https://chatgpt.com/?model=o4-mini
        # https://chatgpt.com/?model=o4-mini-high
        # https://chatgpt.com/?model=gpt-4-5
        # https://chatgpt.com/?model=gpt-4-1
        # https://chatgpt.com/?model=gpt-4-1-mini

        temporary_str = "&temporary-chat=true" if tmp else ""
        self.driver.get(f"https://chatgpt.com/?model={model}{temporary_str}")

    def submit_message(self):
        btn = self.driver.find_element(By.CSS_SELECTOR, "#composer-submit-button")
        btn.click()

    def is_typing(self) -> bool:
        return self.driver.execute_script(
            "return document.querySelector('.streaming-animation') !== null;"
        )

    def is_generating(self) -> bool:
        return self.driver.execute_script(
            "return document.querySelector('.loading-shimmer') !== null;"
        )

    def wait_for_response(self, timeout: int = 40):
        start = time.time()
        has_started = False
        logger.info("⏳ Warte auf Start der Antwort...")
        while time.time() - start < timeout:
            if self.is_typing():
                if not has_started:
                    logger.info("🟢 ChatGPT beginnt zu tippen...")
                    has_started = True
            elif has_started:
                logger.info("✅ Antwort ist vollständig.")
                return
            time.sleep(0.4)
        logger.warning("⚠️ Timeout: Antwort hat nicht wie erwartet geendet.")

    def wait_for_image(self, timeout: int = 180):
        start = time.time()
        has_started = False
        logger.info("⏳ Warte auf Start der Bildgenerirung...")
        while time.time() - start < timeout:
            if self.is_generating():
                if not has_started:
                    logger.info("🟢 ChatGPT beginnt zu generieren...")
                    has_started = True
            elif has_started:
                logger.info("✅ Image ist vollständig.")
                return
            time.sleep(0.4)
        logger.warning("⚠️ Timeout: Bild-Generierung hat nicht wie erwartet geendet.")

    def send_message(self, message: str, mode: str = "default"):
        self.set_message(message)
        time.sleep(0.5)
        self.submit_message()
        if mode == "image_gen":
            self.wait_for_image()
        else:
            self.wait_for_response()

    def get_all_messages(self) -> list[str]:
        return self.driver.execute_script("""
            return Array.from(
                document.querySelectorAll('div[data-message-author-role="assistant"]')
            ).map(e => e.innerText.trim()).filter(Boolean);
        """)

    def get_last_message(self) -> str:
        msgs = self.get_all_messages()
        return msgs[-1] if msgs else ""

    def get_all_images(self) -> list[str]:
        return self.driver.execute_script("""
            return [...document.querySelectorAll("img")].map(e => e.src);
        """)

    def get_last_image(self) -> str:
        imgs = self.get_all_images()
        return imgs[-1] if imgs else ""

    def activate_web_search(self):
        btn = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-button-search"]')
        btn.click()

    def is_web_search_active(self) -> bool:
        btn = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-button-search"]')
        return btn.get_attribute("aria-pressed") == "true"

    def activate_image_gen(self):
        btn = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-button-create-image"]')
        btn.click()

    def is_image_gen_active(self) -> bool:
        btn = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-button-create-image"]')
        return btn.get_attribute("aria-pressed") == "true"
