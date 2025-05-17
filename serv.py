from pathlib import Path
import time
from fastapi import FastAPI
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
from datetime import datetime

# === Logging Setup ===
LOG_TO_FILE = False
LOG_FILE_PATH = "chat_automation.log"
if LOG_TO_FILE:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s"
    )

def log(msg: str):
    logging.info(msg)


# === Webdriver Setup beim Serverstart ===
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-extensions")
options.add_argument("--no-default-browser-check")
options.add_argument("--no-first-run")
options.add_argument(f"--user-data-dir={str(Path('./tmp/profile').resolve())}")
options.add_argument("--log-level=3") 

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://chatgpt.com/")
input("⏳ Bitte logge dich ein und drücke [Enter]...")

class MessageIn(BaseModel):
    message: str
    web_search: bool = False
    image_gen: bool = False
    deep_research: bool = False

class MessageOut(MessageIn):
    result: str
    mode: str

# === Helper ===

def set_message(message: str):
    """Nur Text setzen, ohne zu senden"""
    log(f"📨 Sende Nachricht: {message}")
    driver.execute_script(
        "document.querySelector('#prompt-textarea > p').innerHTML = arguments[0];",
        message
    )

def submit_message():
    """Nachricht absenden"""
    submit_btn = driver.find_element(By.CSS_SELECTOR, "#composer-submit-button")
    submit_btn.click()

def is_typing():
    """Prüft, ob die ChatGPT-Antwort noch generiert wird (streaming-animation sichtbar)"""
    return driver.execute_script("""return document.querySelector('.streaming-animation') !== null;""")


def old_wait_for_response(timeout=40):
    """Wartet darauf, dass eine neue Antwort in get_all_messages() auftaucht"""
    start = time.time()
    initial_count = len(get_all_messages())

    while time.time() - start < timeout:
        messages = get_all_messages()
        if len(messages) > initial_count:
            return
        time.sleep(0.2)

    print("⚠️ Timeout: Es kam keine neue Antwort.")


def wait_for_response(timeout=40):
    start = time.time()
    has_started = False
    log("⏳ Warte auf Start der Antwort...")

    while time.time() - start < timeout:
        typing = is_typing()

        if typing and not has_started:
            log("🟢 ChatGPT beginnt zu tippen...")
            has_started = True

        if has_started and not typing:
            log("✅ Antwort ist vollständig.")
            return

        time.sleep(0.4)

    log("⚠️ Timeout: Antwort hat nicht wie erwartet geendet.")


def send_message(message: str):
    set_message(message)
    time.sleep(0.5)
    submit_message()
    wait_for_response()

def get_all_messages():
    # document.querySelectorAll('div[data-message-author-role="assistant"]')
    """Gibt alle ChatGPT-Antworten zurück"""
    return driver.execute_script("""
        return Array.from(
            document.querySelectorAll('div[data-message-author-role="assistant"]')
        ).map(e => e.innerText.trim()).filter(Boolean);
    """)

def get_last_message():
    messages = get_all_messages()
    return messages[-1] if messages else "Keine Antwort gefunden."

def activate_web_search():
    """Websuche aktivieren"""
    search_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-button-search"]')
    search_btn.click()

def is_web_search_active():
    btn = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-button-search"]')
    return btn.get_attribute("aria-pressed") == "true"

def activate_image_gen():
    """Bildgenerierung aktivieren"""
    img_btn = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-button-create-image"]')
    img_btn.click()

def is_image_gen_active():
    btn = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="composer-button-create-image"]')
    return btn.get_attribute("aria-pressed") == "true"

# === FastAPI ===
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat", response_model=MessageOut)
def chat(data: MessageIn):
    try:
        # Zuerst alles deaktivieren, falls aktiv
        if is_web_search_active():
            activate_web_search()
        if is_image_gen_active():
            activate_image_gen()
        # if is_deep_research_active():  # Wenn du sowas hast
        #     activate_deep_research()

        # Dann genau eins aktivieren
        if data.web_search:
            activate_web_search()
        elif data.image_gen:
            activate_image_gen()
        elif data.deep_research:
            # activate_deep_research()  # optional: Wenn du das UI-Element kennst
            pass

        if data.web_search:
            mode = "web_search"
            activate_web_search()
        elif data.image_gen:
            mode = "image_gen"
            activate_image_gen()
        elif data.deep_research:
            mode = "deep_research"
            # activate_deep_research() – später
        else:
            mode = "default"

        send_message(data.message)
        result = get_last_message()

    except Exception as e:
        result = f"Fehler: {e}"

    return MessageOut(**data.model_dump(), result=result, mode=mode)