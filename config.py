import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


API_ID = int(_require("API_ID"))
API_HASH = _require("API_HASH")
BOT_TOKEN = _require("BOT_TOKEN")
SESSION_STRING = _require("SESSION_STRING")

ADMIN_IDS = {
    int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
}
LOG_CHAT_ID = os.getenv("LOG_CHAT_ID") or None

DOWNLOAD_DIR = "downloads"
MAX_QUEUE_SIZE = 25
