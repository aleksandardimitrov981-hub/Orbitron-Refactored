print("DEBUG: Файлът run_pipeline.py започва да се изпълнява...")

import sys
import os
from datetime import datetime, timedelta

print("DEBUG: Основните модули са импортирани.")

# Този блок гарантира, че Python намира папка src
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

print(f"DEBUG: Пътят към проекта '{project_root}' е добавен към sys.path.")

# --- ИМПОРТИ ---
try:
    from config import ASSETS_TO_TRACK
    from src.database.database_manager import DatabaseManager
    from src.data_ingestion.rss_client import fetch_rss_articles
    from src.data_ingestion.newsapi_client import NewsApiClient
    from src.data_ingestion.coingecko_client import CoinGeckoClient
    from src.analysis.ai_analyzer import AIAnalyzer
    from src.data_ingestion.kucoin_client import KucoinHandler
    from src.data_ingestion.defillama_client import DefiLlamaHandler
    from src.data_ingestion.eodhd_client import EODHDClient
    print("DEBUG: Всички модули от проекта са импортирани успешно.")
except ImportError as e:
    print(f"FATAL ERROR: Неуспешен импорт на модул от проекта: {e}")
    sys.exit(1)

# --- КОНСТАНТИ ---
ECONOMIC_NEWS_KEYWORDS = ['inflation', 'interest rate', 'GDP', 'FOMC', 'unemployment']

# ... (всички run_..._pipeline функции остават същите) ...
def run_news_pipeline(db_manager: DatabaseManager, news_api_client: NewsApiClient):
    print("\n--- 📰 STEP 1: COLLECTING NEWS ---")
    rss_articles = fetch_rss_articles()
    asset_articles = news_api_client.fetch_asset_news()
    economic_articles = news_api_client.fetch_economic_news(ECONOMIC_NEWS_KEYWORDS)
    all_articles = rss_articles + asset_articles + economic_articles
    unique_articles = list({article['url']: article for article in all_articles if article.get('url')}.values())
    if unique_articles:
        rows_saved = db_manager.save_articles(unique_articles)
        print(f"💾 Found {len(unique_articles)} unique articles. Saved {rows_saved} new ones to the database.")

def run_ai_analysis_pipeline(db_manager: DatabaseManager, ai_analyzer: AIAnalyzer):
    print("\n--- 🧠 STEP 2: RUNNING AI ANALYSIS ---")
    # ...
    unprocessed_articles = db_manager.get_unprocessed_articles(limit=30)
    if not unprocessed_articles:
        print("No new articles to analyze.")
        return
    print(f"Found {len(unprocessed_articles)} unprocessed articles. Starting AI analysis...")
    for article in unprocessed_articles:
        is_economic = article.get('category') == 'economic_event'
        analysis = ai_analyzer.analyze_article_title(article['title'], is_economic=is_economic)
        if analysis:
            db_manager.update_article_analysis(article['id'], analysis)
            print(f"   -> ✅ AI analysis for article #{article['id']} '{article['title'][:30]}...' saved.")


def run_market_data_pipeline(db_manager: DatabaseManager, coingecko_client: CoinGeckoClient):
    print("\n--- 📈 STEP 3: COLLECTING COINGECKO MARKET DATA ---")
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

def run_kucoin_historical_data_pipeline(db_manager: DatabaseManager, kucoin_handler: KucoinHandler):
    print("\n--- 💹 STEP 4: COLLECTING KUCOIN HISTORICAL DATA ---")
    kucoin_symbols = ['BTC-USDT', 'ETH-USDT'] 
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d')
    for symbol in kucoin_symbols:
        print(f"Processing KuCoin historical data for '{symbol}'...")
        historical_data = kucoin_handler.get_historical_data(symbol, start_date_str, end_date_str)
        if historical_data:
            print(f"  -> Fetched {len(historical_data)} records. Saving to database...")
            db_manager.save_historical_prices(symbol, historical_data)
        else:
            print(f"  -> No historical data received from KuCoin for {symbol}. Skipping.")

def run_defillama_pipeline(db_manager: DatabaseManager, defillama_handler: DefiLlamaHandler):
    print("\n--- 🔗 STEP 5: COLLECTING DEFI LLAMA ON-CHAIN DATA ---")
    chains_to_track = ["Ethereum", "Solana", "Arbitrum", "Polygon"]
    tvl_data = defillama_handler.get_chains_tvl(chains_to_track)
    if tvl_data:
        print(f"  -> Fetched TVL data for {len(tvl_data)} chains. Saving to database...")
        db_manager.save_chain_tvl_data(tvl_data)
    else:
        print(f"  -> No TVL data received from DefiLlama. Skipping.")

def run_forex_data_pipeline(db_manager: DatabaseManager, eodhd_client: EODHDClient):
    print("\n--- 💵 STEP 6: COLLECTING DXY FOREX DATA ---")
    symbol = "DXY.INDX"
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)
    from_date_str = from_date.strftime('%Y-%m-%d')
    to_date_str = to_date.strftime('%Y-%m-%d')
    forex_data = eodhd_client.get_forex_data(symbol, from_date_str, to_date_str)
    if forex_data:
        print(f"  -> Fetched {len(forex_data)} daily records for {symbol}. Saving to database...")
        db_manager.save_forex_data(symbol, forex_data)
    else:
        print(f"  -> No data received from EODHD for {symbol}. Skipping.")

def main():
    """Главната функция, която дирижира целия процес."""
    print("DEBUG: Функцията main() е извикана.")
    print("🚀🚀🚀 ORBITRON AI - STARTING FULL PIPELINE 🚀🚀🚀")

    # --- ОБНОВЕНА ИНИЦИАЛИЗАЦИЯ ---
    db_manager = DatabaseManager()
    news_api_client = NewsApiClient()
    coingecko_client = CoinGeckoClient()
    ai_analyzer = AIAnalyzer()
    kucoin_handler = KucoinHandler()
    defillama_handler = DefiLlamaHandler()
    eodhd_client = EODHDClient()

    print("DEBUG: Всички клиенти са инициализирани.")
    
    # --- ИЗПЪЛНЕНИЕ НА ВСИЧКИ СТЪПКИ ---
    run_news_pipeline(db_manager, news_api_client)
    run_ai_analysis_pipeline(db_manager, ai_analyzer)
    run_market_data_pipeline(db_manager, coingecko_client)
    run_kucoin_historical_data_pipeline(db_manager, kucoin_handler)
    run_defillama_pipeline(db_manager, defillama_handler)
    run_forex_data_pipeline(db_manager, eodhd_client)

    print("\n🏁🏁🏁 PIPELINE FINISHED SUCCESSFULLY! 🏁🏁🏁")


if __name__ == "__main__":
    print("DEBUG: Влизаме в if __name__ == '__main__': блока.")
    main()
else:
    print("DEBUG: Скриптът е импортиран, а не изпълнен директно.")