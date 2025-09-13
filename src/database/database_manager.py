# src/database/database_manager.py
import sqlite3
from typing import List, Dict, Any
from config import DATABASE_PATH

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.setup_database()

    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = dict_factory
            return conn
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            return None

    def setup_database(self):
        create_articles_table = """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL, published_at TEXT NOT NULL,
            fetched_at TEXT DEFAULT (datetime('now', 'utc')), category TEXT,
            summary TEXT, sentiment TEXT, reasoning TEXT, investment_factors TEXT
        );"""
        create_market_data_table = """
        CREATE TABLE IF NOT EXISTS market_data (
            asset_id TEXT NOT NULL, date DATE NOT NULL, price REAL NOT NULL,
            market_cap REAL, total_volume REAL, PRIMARY KEY (asset_id, date)
        );"""
        create_economic_events_table = """
        CREATE TABLE IF NOT EXISTS economic_events (
            id TEXT PRIMARY KEY, event_date TEXT NOT NULL, country TEXT,
            event_name TEXT NOT NULL, importance INTEGER, actual TEXT,
            forecast TEXT, previous TEXT
        );"""
        conn = self._get_connection()
        if conn:
            try:
                with conn:
                    print("🔧 Checking and setting up database tables...")
                    conn.execute(create_articles_table)
                    conn.execute(create_market_data_table)
                    conn.execute(create_economic_events_table)
                print("✅ Database tables are ready.")
            except sqlite3.Error as e:
                print(f"❌ Database setup error: {e}")
            finally:
                conn.close()

    def save_articles(self, articles: List[Dict[str, Any]]):
        sql = "INSERT OR IGNORE INTO articles (source, title, url, published_at, category) VALUES (:source, :title, :url, :published_at, :category)"
        conn = self._get_connection()
        if conn:
            try:
                with conn:
                    data_to_insert = [
                        {
                            'source': article.get('source', 'N/A'), 'title': article.get('title', 'N/A'),
                            'url': article.get('url'), 'published_at': article.get('published_at', 'N/A'),
                            'category': article.get('category')
                        } for article in articles if article.get('url')
                    ]
                    cursor = conn.cursor()
                    cursor.executemany(sql, data_to_insert)
                    return cursor.rowcount
            except sqlite3.Error as e:
                print(f"❌ Error saving articles: {e}")
            finally:
                conn.close()
        return 0

    # --- ТУК БЯХА ЛИПСВАЩИТЕ МЕТОДИ ---
    def get_unprocessed_articles(self, limit: int = 5) -> List[Dict[str, Any]]:
        sql = "SELECT id, title, category FROM articles WHERE summary IS NULL ORDER BY fetched_at DESC LIMIT ?"
        conn = self._get_connection()
        if conn:
            try:
                with conn:
                    return conn.execute(sql, (limit,)).fetchall()
            except sqlite3.Error as e:
                print(f"❌ Error fetching unprocessed articles: {e}")
            finally:
                conn.close()
        return []

    def update_article_analysis(self, article_id: int, analysis: Dict[str, Any]):
        sql = "UPDATE articles SET summary = :summary, sentiment = :sentiment, reasoning = :reasoning, investment_factors = :investment_factors WHERE id = :id"
        conn = self._get_connection()
        if conn:
            try:
                with conn:
                    analysis['id'] = article_id
                    conn.execute(sql, analysis)
            except sqlite3.Error as e:
                print(f"❌ Error updating article #{article_id}: {e}")
            finally:
                conn.close()

    def save_market_data(self, market_data: List[Dict[str, Any]]):
        sql = "INSERT OR REPLACE INTO market_data (asset_id, date, price, market_cap, total_volume) VALUES (:asset_id, :date, :price, :market_cap, :total_volume)"
        conn = self._get_connection()
        if conn:
            try:
                with conn:
                    cursor = conn.cursor()
                    cursor.executemany(sql, market_data)
                    return cursor.rowcount
            except sqlite3.Error as e:
                print(f"❌ Error saving market data: {e}")
            finally:
                conn.close()
        return 0

    def get_latest_market_data_date(self, asset_id: str) -> str or None:
        sql = "SELECT MAX(date) AS latest_date FROM market_data WHERE asset_id = ?"
        conn = self._get_connection()
        if conn:
            try:
                with conn:
                    result = conn.execute(sql, (asset_id,)).fetchone()
                    return result['latest_date'] if result and result['latest_date'] else None
            except sqlite3.Error as e:
                print(f"❌ Error getting latest date for {asset_id}: {e}")
            finally:
                conn.close()
        return None