import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Claude API
    CLAUDE_API_KEY = os.getenv("CLAUDE_API")
    CLAUDE_MODEL = "claude-sonnet-4-6"  #"claude-sonnet-4-5-20250929"
    CLAUDE_BETAS = ["context-1m-2025-08-07", "context-management-2025-06-27"]

    # Storage paths
    BASE_DIR = Path(__file__).parent
    STORAGE_DIR = BASE_DIR / "storage"
    USER_FILES_DIR = STORAGE_DIR / "user_files"
    RESPONSES_DIR = STORAGE_DIR / "responses"

    # File upload settings
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'.json', '.txt', '.xml', '.pdf', '.csv', '.xlsx', '.xls'}

    # Flask settings
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    @classmethod
    def init_directories(cls):
        """Создает необходимые директории при запуске"""
        cls.USER_FILES_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
