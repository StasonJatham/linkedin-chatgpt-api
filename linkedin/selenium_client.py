from pathlib import Path
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.get("https://www.linkedin.com/feed/")
    # Hier könntest du automatisches Login einbauen oder
    # für das manuelle Login einen Hook / Callback definieren.
    return driver


class ChatGPTClient:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)  # max. 10 Sekunden warten
        # self.ensure_login()

    def is_logged_in(self) -> bool:
        """
        TODO: Hier prüfen, ob du wirklich eingeloggt bist.
        Z. B. nach dem Avatar-Button suchen:
          return bool(self.driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="user-menu-button"]'))
        """
        return False  # Platzhalter

    def ensure_login(self):
        # TODO: will ich auch noch stabiler bauen das nicht alles stehen muss.
        """Wenn nicht eingeloggt, warte auf manuelles Login via Konsole."""
        if not self.is_logged_in():
            print("+ Bitte logge dich im Browser-Fenster ein und drücke [Enter]…")
            input()
            if not self.is_logged_in():
                raise RuntimeError("Login fehlgeschlagen – bitte erneut einloggen.")

    def start_editor(self):
        self.driver.get(
            "https://www.linkedin.com/in/YOUR-USERNAME/overlay/create-post/"
        )
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']")
                )
            )
            editor = self._get_editor()
            self.driver.execute_script("return arguments[0].innerHTML;", editor)
        except TimeoutException:
            print("❌ Editor konnte nicht gefunden werden.")

    def _get_editor(self):
        return self.driver.find_element(
            By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']"
        )

    def remove_first_br(self):
        editor = self._get_editor()
        first_p = editor.find_elements(By.TAG_NAME, "p")
        if not first_p:
            print("⚠️ Kein <p>-Element im Editor gefunden.")
            return

        inner = first_p[0].get_attribute("innerHTML").strip()

        if inner == "<br>":
            self.driver.execute_script("""
                const editor = arguments[0];
                const firstP = editor.querySelector('p');
                if (firstP && firstP.innerHTML.trim() === '<br>') {
                    firstP.remove();
                }
            """, editor)
            print("Erstes <p><br></p> wurde entfernt.")
        else:
            print("Erstes <p> enthält mehr als nur <br> – keine Aktion.")
        
    def insert_simple_text(self, text="ist wie man einfachen text einfügt"):
        editor = self._get_editor()
        self.driver.execute_script(
            f"arguments[0].innerHTML += '<p>{text}</p>';", editor
        )

    def insert_newline(self):
        editor = self._get_editor()
        self.driver.execute_script(
            "arguments[0].innerHTML += '<p><br></p>';", editor
        )

    def get_cybersecurity_feed():
        # https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords=cybersecurity&sid=.WB
        # https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords=cybersecurity&origin=FACETED_SEARCH&sid=Wp1&sortBy=%22date_posted%22
        pass
    
    def insert_link(
        self,
        url="https://karl.fail/blog/caffeine-exploits-hacking-coffee-machines-with-social-engineering/",
    ):
        editor = self._get_editor()
        self.driver.execute_script(f"arguments[0].innerHTML += '<p>{url}</p>';", editor)

    def insert_hashtags(self, tags=["#hacking", "#meow"]):
        editor = self._get_editor()
        hashtag_html = " ".join(
            f'<strong class="ql-hashtag" data-test-ql-hashtag="true">{tag}</strong>'
            for tag in tags
        )
        self.driver.execute_script(
            f"arguments[0].innerHTML += '<p>{hashtag_html}</p>';", editor
        )

    def submit_post(self):
        time.sleep(1)
        self.driver.find_element(
            By.CSS_SELECTOR, "div.share-box_actions > button"
        ).click()

    def cancel_post(self):
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "button").click()

    def discard_draft(self):
        time.sleep(1)
        self.driver.find_element(
            By.CSS_SELECTOR, "button[data-control-name='share_draft_discard']"
        ).click()

    def close(self):
        self.driver.quit()

