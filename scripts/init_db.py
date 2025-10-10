import sys
import os
import logging

# --- ДОБАВЯМЕ ТОЗИ БЛОК КОД В НАЧАЛОТО ---
# Този код гарантира, че Python намира папка src,
# като добавя главната директория на проекта към пътя за търсене.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# --- КРАЙ НА ДОБАВЕНИЯ БЛОК ---

from src.database.database_manager import DatabaseManager

# Настройваме логър за скрипта
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Дефинираме SQL командите за всички таблици в един стринг
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    title TEXT,
    url TEXT UNIQUE,
    published_at TEXT,
    category TEXT,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    summary TEXT,
    sentiment TEXT,
    reasoning TEXT,
    investment_factors TEXT
);

CREATE TABLE IF NOT EXISTS market_data (
    asset_id TEXT NOT NULL,
    date TEXT NOT NULL,
    price REAL,
    market_cap REAL,
    total_volume REAL,
    PRIMARY KEY (asset_id, date)
);

CREATE TABLE IF NOT EXISTS historical_prices (
    asset_symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    PRIMARY KEY (asset_symbol, timestamp)
);

CREATE TABLE IF NOT EXISTS chain_tvl_data (
    chain TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    tvl REAL NOT NULL,
    PRIMARY KEY (chain, timestamp)
);

-- ЕТО Я И НОВАТА ТАБЛИЦА ЗА FOREX ДАННИ --
CREATE TABLE IF NOT EXISTS forex_data (
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    adjusted_close REAL,
    volume INTEGER,
    PRIMARY KEY (symbol, date)
);
"""

def initialize_database():
    """
    Основна функция за инициализация на базата данни.
    Създава инстанция на DatabaseManager и изпълнява SQL скрипта.
    """
    logging.info("Инициализиране на базата данни...")
    try:
        db_manager = DatabaseManager()
        db_manager.execute_script(CREATE_TABLES_SQL)
        logging.info("✅ Базата данни е инициализирана. Таблиците са създадени или вече съществуват.")
    except Exception as e:
        logging.error(f"❌ Възникна грешка при инициализация на базата данни: {e}")

if __name__ == "__main__":
    initialize_database()