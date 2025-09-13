# /Orbitron-Refactored/config.py
import os
from dotenv import load_dotenv

# Зарежда променливите от .env файла, за да са достъпни
load_dotenv()

# --- API Ключове (вече се четат сигурно от .env файла) ---
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# --- Пътища ---
# __file__ е текущият файл (config.py)
# os.path.dirname() взима папката, в която се намира
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