# scripts/run_pipeline.py
import sys
import os
from datetime import datetime

# ВРЪЩАМЕ ТОЗИ КОД: Той гарантира, че Python намира папка src
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# --- Импортираме всички наши нови "Лего" блокчета ---
from config import ASSETS_TO_TRACK
from src.database.database_manager import DatabaseManager
from src.data_ingestion.rss_client import fetch_rss_articles
from src.data_ingestion.newsapi_client import NewsApiClient
from src.data_ingestion.coingecko_client import CoinGeckoClient
from src.analysis.ai_analyzer import AIAnalyzer

# --- Константи, които можем лесно да променяме ---
GENERAL_NEWS_KEYWORDS = ['crypto', 'bitcoin', 'ethereum', 'solana', 'ripple', 'blockchain']
ECONOMIC_NEWS_KEYWORDS = ['inflation', 'interest rate', 'GDP', 'FOMC', 'unemployment']

def run_news_pipeline(db_manager, news_api_client):
    """Изпълнява целия процес по събиране и запазване на новини."""
    print("\n--- 📰 STEP 1: COLLECTING NEWS ---")
    rss_articles = fetch_rss_articles()
    general_articles = news_api_client.fetch_general_news(GENERAL_NEWS_KEYWORDS)
    economic_articles = news_api_client.fetch_economic_news(ECONOMIC_NEWS_KEYWORDS)

    all_articles = rss_articles + general_articles + economic_articles

    # Премахваме дубликати по URL
    unique_articles = list({article['url']: article for article in all_articles if article.get('url')}.values())

    if unique_articles:
        rows_saved = db_manager.save_articles(unique_articles)
        print(f"💾 Found {len(unique_articles)} unique articles. Saved {rows_saved} new ones to the database.")

def run_ai_analysis_pipeline(db_manager, ai_analyzer):
    """Изпълнява процеса по анализ на нови статии."""
    print("\n--- 🧠 STEP 2: RUNNING AI ANALYSIS ---")
    unprocessed_articles = db_manager.get_unprocessed_articles(limit=5)

    if not unprocessed_articles:
        print("No new articles to analyze.")
        return

    print(f"Found {len(unprocessed_articles)} unprocessed articles. Starting AI analysis...")
    for article in unprocessed_articles:
        is_economic = article.get('category') == 'economic_event'
        analysis = ai_analyzer.analyze_article_title(article['title'], is_economic=is_economic)

        if analysis:
            db_manager.update_article_analysis(article['id'], analysis)
            print(f"   -> ✅ AI analysis for article #{article['id']} saved.")

def run_market_data_pipeline(db_manager, coingecko_client):
    """Изпълнява процеса по събиране на пазарни данни."""
    print("\n--- 📈 STEP 3: COLLECTING MARKET DATA ---")
    for asset_name, asset_id in ASSETS_TO_TRACK.items():
        print(f"Processing market data for '{asset_name}'...")

        last_date_str = db_manager.get_latest_market_data_date(asset_id)
        days_to_fetch = 30

        if last_date_str:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
            days_diff = (datetime.now() - last_date).days
            if days_diff > 0:
                days_to_fetch = days_diff
                print(f"   -> Last data is from {days_diff} days ago. Fetching new data.")
            else:
                print("   -> Market data is up to date. Skipping.")
                continue
        else:
            print(f"   -> No existing data. Fetching initial {days_to_fetch} days of data.")

        market_data = coingecko_client.fetch_historical_data(asset_id, days=days_to_fetch)
        if market_data:
            rows_saved = db_manager.save_market_data(market_data)
            print(f"   -> 💾 Saved {rows_saved} new market data records.")

def main():
    """Главната функция, която дирижира целия процес."""
    print("🚀🚀🚀 ORBITRON REFACTORED - STARTING FULL PIPELINE 🚀🚀🚀")

    db_manager = DatabaseManager()
    news_api_client = NewsApiClient()
    coingecko_client = CoinGeckoClient()
    ai_analyzer = AIAnalyzer()

    run_news_pipeline(db_manager, news_api_client)
    run_ai_analysis_pipeline(db_manager, ai_analyzer)
    run_market_data_pipeline(db_manager, coingecko_client)

    print("\n🏁🏁🏁 PIPELINE FINISHED SUCCESSFULLY! 🏁🏁🏁")

if __name__ == "__main__":
    main()