from datetime import time
import logging
import mimetypes
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import asyncio
from routers import jobs_router
from db import Job, SessionLocal, init_db
from config import settings
from models import MessageIn, MessageOut
from services.selenium_client import init_driver, ChatGPTClient
from services.image_downloader import download_image
import sys


# Verzeichnisse und Logging
IMAGE_DIR: Path = settings.image_dir
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


# Stelle sicher, dass stdout UTF-8 ist
sys.stdout.reconfigure(encoding='utf-8')

# Manuelles Logging-Setup mit UTF-8 StreamHandler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
console_handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

# Optional: Logging auch in Datei
if settings.log_to_file:
    file_handler = logging.FileHandler(settings.log_file_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # === Setup DB & Selenium ===
    init_db()
    driver = init_driver(settings.chrome_user_data)
    client = ChatGPTClient(driver)
    app.state.client = client

    # === Background-Task starten ===
    async def job_processor():
        while True:
            db = SessionLocal()
            try:
                pending = (
                    db.query(Job)
                      .filter(Job.status == "pending")
                      .order_by(Job.created_at)
                      .all()
                )
                for job in pending:
                    job.status = "running"
                    db.commit()

                    # tatsächliche Verarbeitung in Thread auslagern
                    def work():
                        # hier ist deine ursprüngliche /chat-Logik
                        print("image job")
                        if job.image_gen:
                            client.activate_image_gen()
                            if client.is_image_gen_active():
                                print("image is active")

                            client.send_message(job.message, mode="image_gen")
                            url = client.get_last_image()
                            if url:
                                path = download_image(
                                    url,
                                    save_dir=IMAGE_DIR,
                                    timeout=settings.http_timeout
                                )
                                job.result = f"{settings.server_url}/image/{path.name}"
                                job.mode = "image_gen"
                            if client.is_image_gen_active():
                                client.activate_image_gen()
                        else:
                            client.send_message(job.message, mode="default")
                            job.result = client.get_last_message()
                            job.mode = "default"
                        job.status = "done"
                        db.commit()

                    await asyncio.to_thread(work)

                await asyncio.sleep(1)  # Poll-Intervall
            finally:
                db.close()

    task = asyncio.create_task(job_processor())
    yield
    task.cancel()
    driver.quit()


# FastAPI-Instanz mit Lifespan
app = FastAPI(lifespan=lifespan)
app.include_router(jobs_router, prefix="", tags=["jobs"])

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
def chat_endpoint(data: MessageIn):
    """
    Empfängt eine Chat-Anfrage, aktiviert ggf. Web-Suche oder Bilderzeugung,
    sendet die Nachricht an ChatGPT und gibt das Ergebnis zurück.
    """
    client: ChatGPTClient = app.state.client
    # Defensive: alle Modi zurücksetzen
    if client.is_web_search_active():
        client.activate_web_search()
    if client.is_image_gen_active():
        client.activate_image_gen()

    mode = "default"
    try:
        if data.web_search:
            mode = "web_search"
            client.activate_web_search()
        elif data.image_gen:
            mode = "image_gen"
            client.activate_image_gen()
        elif data.deep_research:
            mode = "deep_research"
            # ggf. future feature

        # Nachricht senden und Antwort abholen
        if data.image_gen:
            client.send_message(data.message, mode=mode)
            image_url = client.get_last_image()
            if image_url:
                path = download_image(image_url, save_dir=IMAGE_DIR, timeout=settings.http_timeout)
                filename = path.name
                result = f"{settings.server_url}/image/{filename}"
            else:
                result = "Kein Bild gefunden"
        else:
            client.send_message(data.message, mode=mode)
            result = client.get_last_message()

    except Exception as e:
        logger.error(f"Fehler im Chat-Endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return MessageOut(**data.model_dump(), result=result, mode=mode)

