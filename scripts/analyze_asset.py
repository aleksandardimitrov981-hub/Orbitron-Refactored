# scripts/analyze_asset.py
import sys
import os
from datetime import datetime

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from config import ASSETS_TO_TRACK
from src.database.database_manager import DatabaseManager
from src.data_ingestion.newsapi_client import NewsApiClient
from src.data_ingestion.coingecko_client import CoinGeckoClient
from src.analysis.ai_analyzer import AIAnalyzer

def run_targeted_pipeline(asset_name: str):
    if asset_name.lower() not in ASSETS_TO_TRACK:
        print(f"❌ Грешка: Активът '{asset_name}' не е намерен.")
        print("Налични активи:", ", ".join(ASSETS_TO_TRACK.keys()))
        return

    asset_id = ASSETS_TO_TRACK[asset_name.lower()]
    print(f"🚀🚀🚀 STARTING TARGETED ANALYSIS FOR: {asset_name.upper()} 🚀🚀🚀")

    db_manager = DatabaseManager()
    news_api_client = NewsApiClient()
    coingecko_client = CoinGeckoClient()
    ai_analyzer = AIAnalyzer()

    print("\n--- 📰 STEP 1: COLLECTING NEWS ---")
    targeted_keywords = ['crypto', 'blockchain', asset_name, asset_id]
    news_articles = news_api_client.fetch_general_news(targeted_keywords)
    if news_articles:
        rows_saved = db_manager.save_articles(news_articles)
        print(f"💾 Found {len(news_articles)} articles. Saved {rows_saved} new ones.")

    print("\n--- 🧠 STEP 2: RUNNING AI ANALYSIS ---")
    unprocessed_articles = db_manager.get_unprocessed_articles(limit=10)
    if unprocessed_articles:
        print(f"Found {len(unprocessed_articles)} articles. Analyzing...")
        for article in unprocessed_articles:
            analysis = ai_analyzer.analyze_article_title(article['title'])
            if analysis:
                db_manager.update_article_analysis(article['id'], analysis)
                print(f"   -> ✅ AI analysis for article #{article['id']} saved.")
    else:
        print("No new articles to analyze.")

    print("\n--- 📈 STEP 3: COLLECTING MARKET DATA ---")
    last_date_str = db_manager.get_latest_market_data_date(asset_id)
    days_to_fetch = 30
    if last_date_str:
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
        days_diff = (datetime.now() - last_date).days
        days_to_fetch = days_diff if days_diff > 0 else 1
    
    print(f"Fetching last {days_to_fetch} days of market data for '{asset_name}'...")
    market_data = coingecko_client.fetch_historical_data(asset_id, days=days_to_fetch)
    if market_data:
        rows_saved = db_manager.save_market_data(market_data)
        print(f"   -> 💾 Saved {rows_saved} new market data records.")

    print(f"\n🏁🏁🏁 TARGETED ANALYSIS FOR {asset_name.upper()} FINISHED! 🏁🏁🏁")

if __name__ == "__main__":
    print("Available assets for analysis:")
    print(" - " + "\n - ".join(ASSETS_TO_TRACK.keys()))
    target_asset = input("\nEnter the name of the asset you want to analyze: ")
    if target_asset:
        run_targeted_pipeline(target_asset)
    else:
        print("No asset entered. Exiting.")