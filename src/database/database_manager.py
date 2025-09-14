# src/database/database_manager.py

import sqlite3
import logging # Променяме print() с logging за по-добър контрол върху съобщенията
from typing import List, Dict, Any
from contextlib import contextmanager # Внасяме необходимия декоратор
from config import DATABASE_PATH

# Настройваме базов logger, който ще записва съобщения с дата и час
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def dict_factory(cursor, row):
    """Преобразува резултатите от заявките в речници."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class DatabaseManager:
    """Управлява цялата комуникация с SQLite базата данни."""
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    # --- НОВ МЕТОД: Контекстен мениджър ---
    @contextmanager
    def managed_connection(self):
        """
        Това е сърцето на нашия "ремонт". Този метод прави следното:
        1. Отваря връзка към базата данни.
        2. Предоставя я на 'with' блока, който го извиква (чрез 'yield').
        3. Ако блокът завърши без грешки, той записва промените (conn.commit()).
        4. Ако възникне грешка, той отменя промените (conn.rollback()).
        5. Във всеки случай, накрая затваря връзката (conn.close()).
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = dict_factory
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise  # Повдигаме грешката, за да може извикващият код да знае за нея
        finally:
            if conn:
                conn.close()

    # --- РЕФАКТОРИРАНИ МЕТОДИ ---
    # Сега всички методи са много по-кратки и чисти.

    def execute_script(self, script_sql: str):
        """Изпълнява SQL скрипт (например за създаване на таблици)."""
        try:
            with self.managed_connection() as conn:
                conn.executescript(script_sql)
            logging.info("✅ SQL script executed successfully.")
        except sqlite3.Error as e:
            # Грешката вече е логната в managed_connection, тук можем да добавим контекст
            logging.error(f"❌ Failed to execute SQL script: {e}")

    def save_articles(self, articles: List[Dict[str, Any]]):
        sql = "INSERT OR IGNORE INTO articles (source, title, url, published_at, category) VALUES (:source, :title, :url, :published_at, :category)"
        data_to_insert = [
            {'source': a.get('source'), 'title': a.get('title'), 'url': a.get('url'),
             'published_at': a.get('published_at'), 'category': a.get('category')}
            for a in articles if a.get('url')
        ]
        try:
            with self.managed_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, data_to_insert)
                return cursor.rowcount
        except sqlite3.Error:
            return 0 # Връщаме 0 при грешка

    def get_unprocessed_articles(self, limit: int = 5) -> List[Dict[str, Any]]:
        sql = "SELECT id, title, category FROM articles WHERE summary IS NULL ORDER BY fetched_at DESC LIMIT ?"
        try:
            with self.managed_connection() as conn:
                return conn.execute(sql, (limit,)).fetchall()
        except sqlite3.Error:
            return []

    def update_article_analysis(self, article_id: int, analysis: Dict[str, Any]):
        sql = "UPDATE articles SET summary = :summary, sentiment = :sentiment, reasoning = :reasoning, investment_factors = :investment_factors WHERE id = :id"
        analysis['id'] = article_id
        try:
            with self.managed_connection() as conn:
                conn.execute(sql, analysis)
        except sqlite3.Error as e:
            logging.error(f"❌ Failed to update article #{article_id}: {e}")

    def save_market_data(self, market_data: List[Dict[str, Any]]):
        sql = "INSERT OR REPLACE INTO market_data (asset_id, date, price, market_cap, total_volume) VALUES (:asset_id, :date, :price, :market_cap, :total_volume)"
        try:
            with self.managed_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, market_data)
                return cursor.rowcount
        except sqlite3.Error:
            return 0

    def get_latest_market_data_date(self, asset_id: str) -> str or None:
        sql = "SELECT MAX(date) AS latest_date FROM market_data WHERE asset_id = ?"
        try:
            with self.managed_connection() as conn:
                result = conn.execute(sql, (asset_id,)).fetchone()
                return result['latest_date'] if result and result['latest_date'] else None
        except sqlite3.Error:
            return None

    # --- МЕТОДИ ЗА ДАШБОРДА (също рефакторирани) ---

    def get_all_analyzed_articles(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM articles WHERE sentiment IS NOT NULL ORDER BY published_at DESC"
        try:
            with self.managed_connection() as conn:
                return conn.execute(sql).fetchall()
        except sqlite3.Error:
            return []

    def get_all_market_data(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM market_data ORDER BY date ASC"
        try:
            with self.managed_connection() as conn:
                return conn.execute(sql).fetchall()
        except sqlite3.Error:
            return []