
from pathlib import Path
import httpx
import mimetypes
import uuid
import logging
from config import settings
logger = logging.getLogger(__name__)



def download_image(
    url: str,
    save_dir: Path = settings.image_dir,
    timeout: int = 15
) -> Path:
    """
    Lädt ein Bild von der angegebenen URL herunter, ermittelt den MIME-Typ
    und speichert es mit der richtigen Dateiendung im Zielverzeichnis.

    Args:
        url (str): URL des Bildes
        save_dir (Path): Verzeichnis, in das das Bild gespeichert wird
        timeout (int): Timeout in Sekunden für den HTTP-Request

    Returns:
        Path: Pfad zur gespeicherten Bilddatei

    Raises:
        RuntimeError: bei Netzwerkfehlern oder fehlgeschlagenem Download
    """
    try:
        logger.info(f"Lade Bild herunter: {url}")
        save_dir.mkdir(parents=True, exist_ok=True)

        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            response = client.get(url)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            extension = mimetypes.guess_extension(content_type) or ".bin"

            filename = f"{uuid.uuid4().hex}{extension}"
            file_path = save_dir / filename

            with open(file_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Bild gespeichert unter: {file_path}")
            return file_path

    except Exception as e:
        msg = f"Fehler beim Herunterladen des Bildes von {url}: {e}"
        logger.error(msg)
        raise RuntimeError(msg)
