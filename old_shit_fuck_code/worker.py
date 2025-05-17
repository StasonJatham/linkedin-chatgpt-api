from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from shared import ChatRequest, ChatResponse, input_queue, output_queue
import undetected_chromedriver as uc



def get_input_box(driver):
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    for textarea in textareas:
        if textarea.is_displayed():
            return textarea
    return None


def send_message(driver, message):
    box = get_input_box(driver)
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


def get_last_message(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, ".flex.flex-col.items-center > div")
    if len(elements) < 2:
        return "Keine Antwort gefunden."
    return elements[-2].text


def main():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument(f"--user-data-dir={str(Path('./tmp/profile').resolve())}")

    # Chrome mit Profil starten
    #driver = uc.Chrome(user_data_dir="./tmp/profile")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Stealth-JS wird in Selenium nicht direkt unterstützt – kannst du mit CDP oder Extension einbauen
    driver.get("https://chatgpt.com/c/6828b584-ab3c-8011-946a-590cf219323c")
    input("⏳ Bitte logge dich ein und drücke [Enter]...")

    print("✅ Eingeloggt. Warte auf Anfragen...")

    while True:
        req: ChatRequest = input_queue.get()
        print("We got a new request!")
        try:
            send_message(driver, req.message)
            result = get_last_message(driver)
        except Exception as e:
            result = f"Fehler: {e}"
        output_queue.put(ChatResponse(id=req.id, result=result))


if __name__ == "__main__":
    main()
