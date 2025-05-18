from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # === Verzeichnisse & URLs ===
    image_dir: Path = Path("./tmp/downloads")
    server_url: str = "http://localhost:8000"
    chrome_user_data: Path = Path("./tmp/profile")
    chatgpt_url: str = "https://chatgpt.com/"

    # === HTTP / Timeout ===
    http_timeout: int = 15

    # === Logging ===
    log_to_file: bool = False
    log_file_path: Path = Path("chat_automation.log")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instanz, die du überall importierst:
settings = Settings()
