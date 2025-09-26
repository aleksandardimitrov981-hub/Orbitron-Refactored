import sqlite3
import logging
from typing import List, Dict, Any
from contextlib import contextmanager
from config import DATABASE_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def dict_factory(cursor, row):
    """Преобразува резултатите от заявките в речници."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class DatabaseManager:
    """Управлява цялата комуникация с SQLite базата данни."""
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    @contextmanager
    def managed_connection(self):
        # ... (този код остава абсолютно същият) ...
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
            raise
        finally:
            if conn:
                conn.close()

    # --- МЕТОДИ ЗА ЗАПИС И ИЗВЛИЧАНЕ ---
    # Всички методи до тук остават същите. 
    # Прескачам ги за краткост, за да стигнем до новия метод.
    # ... save_articles, get_unprocessed_articles, update_article_analysis, etc. ...

    def execute_script(self, script_sql: str):
        try:
            with self.managed_connection() as conn:
                conn.executescript(script_sql)
            logging.info("✅ SQL script executed successfully.")
        except sqlite3.Error as e:
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
            return 0

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

    def save_historical_prices(self, asset_symbol: str, klines: List[Dict[str, Any]]):
        sql = """
        INSERT OR REPLACE INTO historical_prices 
        (asset_symbol, timestamp, open, high, low, close, volume) 
        VALUES (:asset_symbol, :timestamp, :open, :high, :low, :close, :volume)
        """
        data_to_insert = []
        for kline in klines:
            record = kline.copy()
            record['asset_symbol'] = asset_symbol
            data_to_insert.append(record)
        try:
            with self.managed_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, data_to_insert)
                logging.info(f"✅ Успешно записани/обновени {cursor.rowcount} записа за {asset_symbol} в 'historical_prices'.")
                return cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"❌ Грешка при запис на исторически данни за {asset_symbol}: {e}")
            return 0

    # --- ТУК Е ДОБАВЕН НОВИЯТ МЕТОД ЗА DEFI LLAMA ---
    def save_chain_tvl_data(self, tvl_data: List[Dict[str, Any]]):
        """
        Записва или заменя TVL данни за различни блокчейн мрежи.
        """
        sql = """
        INSERT OR REPLACE INTO chain_tvl_data 
        (chain, timestamp, tvl) 
        VALUES (:chain, :timestamp, :tvl)
        """
        # Данните от DefiLlamaHandler вече са в правилния формат
        try:
            with self.managed_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, tvl_data)
                logging.info(f"✅ Успешно записани/обновени {cursor.rowcount} TVL записа.")
                return cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"❌ Грешка при запис на TVL данни: {e}")
            return 0

    def get_latest_market_data_date(self, asset_id: str) -> str or None:
        # ... (този код остава абсолютно същият) ...
        sql = "SELECT MAX(date) AS latest_date FROM market_data WHERE asset_id = ?"
        try:
            with self.managed_connection() as conn:
                result = conn.execute(sql, (asset_id,)).fetchone()
                return result['latest_date'] if result and result['latest_date'] else None
        except sqlite3.Error:
            return None
    
    # --- МЕТОДИ ЗА ДАШБОРДА ---
    def get_all_analyzed_articles(self) -> List[Dict[str, Any]]:
        # ... (този код остава абсолютно същият) ...
        sql = "SELECT * FROM articles WHERE sentiment IS NOT NULL ORDER BY published_at DESC"
        try:
            with self.managed_connection() as conn:
                return conn.execute(sql).fetchall()
        except sqlite3.Error:
            return []

    def get_all_market_data(self) -> List[Dict[str, Any]]:
        # ... (този код остава абсолютно същият) ...
        sql = "SELECT * FROM market_data ORDER BY date ASC"
        try:
            with self.managed_connection() as conn:
                return conn.execute(sql).fetchall()
        except sqlite3.Error:
            return []