# /Orbitron-Refactored/config.py
import os
from dotenv import load_dotenv

# Зарежда променливите от .env файла, за да са достъпни
load_dotenv()

# --- API Ключове (вече се четат сигурно от .env файла) ---
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# --- ТУК Е ДОБАВКАТА ---
KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")
# -------------------------

# --- Пътища ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "orbitron_db.sqlite")

# --- AI Настройки ---
OLLAMA_MODEL = "llama3.2"

# --- Списък с активи за следене ---
ASSETS_TO_TRACK = {
    'bitcoin': 'bitcoin',
    'solana': 'solana',
    'ripple': 'ripple',
    'ethereum': 'ethereum',
    'pudgy-penguins': 'pudgy-penguins',
    'dogs-2': 'dogs-2'
}
# Добави този ред при другите API ключове в config.py
EODHD_API_KEY = os.getenv("EODHD_API_KEY")