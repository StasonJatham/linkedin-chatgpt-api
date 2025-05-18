from pathlib import Path
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
from datetime import datetime
import httpx
import mimetypes
from pathlib import Path
from urllib.parse import urlparse
import uuid

IMAGE_DIR = Path("./tmp/downloads")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
SEVER_URL = "http://localhost:8000"

def download_image(url: str, save_dir: Path = IMAGE_DIR) -> Path:
    """
    Lädt ein Bild über eine URL herunter, erkennt den MIME-Typ,
    und speichert es mit korrekter Dateiendung.

    Args:
        url (str): Bild-URL
        save_dir (Path): Zielverzeichnis (default: aktuelles Verzeichnis)

    Returns:
        Path: Pfad zur gespeicherten Datei
    """
    try:
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            response = client.get(url)
            response.raise_for_status()

            # MIME-Typ erkennen, z. B. image/png
            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            extension = mimetypes.guess_extension(content_type) or ".bin"

            # Dateinamen aus URL oder fallback
            unique_name = f"{uuid.uuid4().hex}{extension}"
            file_path = save_dir / unique_name

            # Datei speichern
            with open(file_path, "wb") as f:
                f.write(response.content)

            return file_path
    except Exception as e:
        raise RuntimeError(f"Fehler beim Herunterladen des Bildes: {e}")


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

def is_generating():
    """Used to check when done with image generation"""
    return driver.execute_script("""return document.querySelector('.loading-shimmer') !== null;""")


def get_new_chat(model:str="gpt-4o",tmp:bool=True):
    # https://chatgpt.com/?model=o4-mini
    # https://chatgpt.com/?model=o4-mini-high
    # https://chatgpt.com/?model=gpt-4-5
    # https://chatgpt.com/?model=gpt-4-1
    # https://chatgpt.com/?model=gpt-4-1-mini

    temporary_str = "&temporary-chat=true" if tmp else ""
    driver.get(f"https://chatgpt.com/?model={model}{temporary_str}")


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


def wait_for_image(timeout=180):
    start = time.time()
    has_started = False
    log("⏳ Warte auf Start der Bildgenerirung...")

    while time.time() - start < timeout:
        typing = is_generating()

        if typing and not has_started:
            log("🟢 ChatGPT beginnt zu generieren...")
            has_started = True

        if has_started and not typing:
            log("✅ Image ist vollständig.")
            return

        time.sleep(0.4)

    log("⚠️ Timeout: Antwort hat nicht wie erwartet geendet.")


def send_message(message: str, mode:str="default"):
    set_message(message)
    time.sleep(0.5)
    submit_message()
    if mode == "image_gen":
        wait_for_image()
    else:
        wait_for_response()

def get_all_messages():
    # document.querySelectorAll('div[data-message-author-role="assistant"]')
    """Gibt alle ChatGPT-Antworten zurück"""
    return driver.execute_script("""
        return Array.from(
            document.querySelectorAll('div[data-message-author-role="assistant"]')
        ).map(e => e.innerText.trim()).filter(Boolean);
    """)

def get_all_images():
    return driver.execute_script("""
        return [...document.querySelectorAll("img")].map(e => e.src);
    """)

def get_last_image():
    images = get_all_images()
    return images[-1] if images else "Kein Image gefunden."

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

@app.get("/image/{filename}")
def serve_image(filename: str):
    file_path = IMAGE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    return FileResponse(file_path, media_type=mime_type)

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
            send_message(data.message, mode=mode)
            result = get_last_message()
            return MessageOut(**data.model_dump(), result=result, mode=mode)

        elif data.image_gen:
            mode="image_gen"
            activate_image_gen()
            send_message(data.message, mode="image_gen")
            image_url = get_last_image()
            print(image_url)
            
            if image_url:
                try:
                    image_path = download_image(image_url, save_dir=IMAGE_DIR)
                    image_filename = image_path.name
                    image_link = f"{SEVER_URL}/image/{image_filename}"
                    result = image_link
                except Exception as e:
                    result = f"Bild konnte nicht geladen werden: {e}"
            else:
                result = "Kein Bild gefunden"

            return MessageOut(**data.model_dump(), result=result, mode=mode)

        elif data.deep_research:
            mode = "deep_research"
            # activate_deep_research() – später
        else:
            mode = "default"
            send_message(data.message, mode=mode)
            result = get_last_message()
            return MessageOut(**data.model_dump(), result=result, mode=mode)

    except Exception as e:
        result = f"Fehler: {e}"

    return MessageOut(**data.model_dump(), result=result, mode=mode)