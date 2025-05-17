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

# === Webdriver Setup beim Serverstart ===
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-extensions")
options.add_argument("--no-default-browser-check")
options.add_argument("--no-first-run")
options.add_argument(f"--user-data-dir={str(Path('./tmp/profile').resolve())}")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://chatgpt.com/")
input("⏳ Bitte logge dich ein und drücke [Enter]...")

# === Helper ===
def get_input_box():
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    for textarea in textareas:
        if textarea.is_displayed():
            return textarea
    return None


# -> msg
# document.querySelector("#prompt-textarea > p").innerHTML = "Hallo"

# -> submit
# document.querySelector("#composer-submit-button").click()

# -> check if typing
# document.querySelector(".streaming-animation")


# - messages
# document.querySelectorAll('div[data-message-author-role="assistant"]')

# last msg 
# [...document.querySelectorAll('div[data-message-author-role="assistant"]')].pop();

# websearch
# document.querySelector('button[data-testid="composer-button-search"]').click()
# is active ? document.querySelector('button[data-testid="composer-button-search"]').ariaPressed


# gen image
# document.querySelector('button[data-testid="composer-button-create-image"]').click()

# is active ? document.querySelector('button[data-testid="composer-button-create-image"]').ariaPressed

def send_message(message: str):
    box = get_input_box()
    if box:
        box.click()
        box.clear()
        box.send_keys(message + Keys.ENTER)
        while True:
            try:
                driver.find_element(By.CLASS_NAME, "result-streaming")
                time.sleep(0.1)
            except:
                break


def get_last_message():
    elements = driver.find_elements(By.CSS_SELECTOR, ".flex.flex-col.items-center > div")
    if len(elements) < 2:
        return "Keine Antwort gefunden."
    return elements[-2].text

# === FastAPI ===
app = FastAPI()

class MessageIn(BaseModel):
    message: str

class MessageOut(BaseModel):
    result: str

@app.post("/chat", response_model=MessageOut)
def chat(data: MessageIn):
    try:
        print(f"📥 Neue Anfrage: {data.message}")
        send_message(data.message)
        result = get_last_message()
    except Exception as e:
        result = f"Fehler: {e}"
    return {"result": result}
