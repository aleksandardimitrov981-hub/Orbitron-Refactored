import sys
import os
from datetime import datetime, timedelta

# Този блок гарантира, че Python намира папка src
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# --- ИМПОРТИ ---
from config import ASSETS_TO_TRACK
from src.database.database_manager import DatabaseManager
from src.data_ingestion.rss_client import fetch_rss_articles
from src.data_ingestion.newsapi_client import NewsApiClient
from src.data_ingestion.coingecko_client import CoinGeckoClient
from src.analysis.ai_analyzer import AIAnalyzer
from src.data_ingestion.kucoin_client import KucoinHandler
# --- ДОБАВЯМЕ ИМПОРТ ЗА DEFI LLAMA ---
from src.data_ingestion.defillama_client import DefiLlamaHandler

# --- КОНСТАНТИ ---
ECONOMIC_NEWS_KEYWORDS = ['inflation', 'interest rate', 'GDP', 'FOMC', 'unemployment']


# --- ДЕФИНИЦИИ НА ФУНКЦИИТЕ ---

def run_news_pipeline(db_manager: DatabaseManager, news_api_client: NewsApiClient):
    """Изпълнява целия процес по събиране и запазване на новини."""
    print("\n--- 📰 STEP 1: COLLECTING NEWS ---")
    # ... (кодът тук остава същият) ...
    rss_articles = fetch_rss_articles()
    asset_articles = news_api_client.fetch_asset_news()
    economic_articles = news_api_client.fetch_economic_news(ECONOMIC_NEWS_KEYWORDS)
    all_articles = rss_articles + asset_articles + economic_articles
    unique_articles = list({article['url']: article for article in all_articles if article.get('url')}.values())
    if unique_articles:
        rows_saved = db_manager.save_articles(unique_articles)
        print(f"💾 Found {len(unique_articles)} unique articles. Saved {rows_saved} new ones to the database.")

def run_ai_analysis_pipeline(db_manager: DatabaseManager, ai_analyzer: AIAnalyzer):
    """Изпълнява процеса по анализ на нови статии."""
    print("\n--- 🧠 STEP 2: RUNNING AI ANALYSIS ---")
    # ... (кодът тук остава същият) ...
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
    """Изпълнява процеса по събиране на пазарни данни от CoinGecko."""
    print("\n--- 📈 STEP 3: COLLECTING COINGECKO MARKET DATA ---")
    for asset_name, asset_id in ASSETS_TO_TRACK.items():
        print(f"Processing market data for '{asset_name}'...")

        last_date_str = db_manager.get_latest_market_data_date(asset_id)
        days_to_fetch = 30  # Стойност по подразбиране

        if last_date_str:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
            days_diff = (datetime.now() - last_date).days
            if days_diff > 0:
                days_to_fetch = days_diff
                print(f"   -> Last data is from {days_diff} days ago. Fetching new data.")
            else:
                print("   -> Market data is up to date. Skipping.")
                continue # Пропускаме останалата част от цикъла за този актив
        else:
            print(f"   -> No existing data. Fetching initial {days_to_fetch} days of data.")

        # --- ТОВА Е КОРЕКЦИЯТА ---
        # Тези два реда са преместени НАВЪТРЕ, за да са част от for цикъла.
        market_data = coingecko_client.fetch_historical_data(asset_id, days=days_to_fetch)
        if market_data:
            rows_saved = db_manager.save_market_data(market_data)
            print(f"   -> 💾 Saved {rows_saved} new market data records.")

def run_kucoin_historical_data_pipeline(db_manager: DatabaseManager, kucoin_handler: KucoinHandler):
    """Изпълнява процеса по събиране на исторически данни (свещи) от KuCoin."""
    print("\n--- 💹 STEP 4: COLLECTING KUCOIN HISTORICAL DATA ---")
    # ... (кодът тук остава същият) ...
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

# --- НОВА PIPELINE ФУНКЦИЯ: За DefiLlama данни ---
def run_defillama_pipeline(db_manager: DatabaseManager, defillama_handler: DefiLlamaHandler):
    """
    Изпълнява процеса по събиране на on-chain TVL данни от DefiLlama.
    """
    print("\n--- 🔗 STEP 5: COLLECTING DEFI LLAMA ON-CHAIN DATA ---")
    
    # Дефинираме кои мрежи искаме да следим
    chains_to_track = ["Ethereum", "Solana", "Arbitrum", "Polygon"]
    
    # 1. Извличаме данните от DefiLlama
    tvl_data = defillama_handler.get_chains_tvl(chains_to_track)
    
    # 2. Проверяваме и записваме в базата данни
    if tvl_data:
        print(f"  -> Fetched TVL data for {len(tvl_data)} chains. Saving to database...")
        db_manager.save_chain_tvl_data(tvl_data)
    else:
        print(f"  -> No TVL data received from DefiLlama. Skipping.")

def main():
    """Главната функция, която дирижира целия процес."""
    print("🚀🚀🚀 ORBITRON AI - STARTING FULL PIPELINE 🚀🚀🚀")

    # --- ОБНОВЕНА ИНИЦИАЛИЗАЦИЯ ---
    db_manager = DatabaseManager()
    news_api_client = NewsApiClient()
    coingecko_client = CoinGeckoClient()
    ai_analyzer = AIAnalyzer()
    kucoin_handler = KucoinHandler()
    defillama_handler = DefiLlamaHandler() # Добавяме DefiLlama

    # --- ИЗПЪЛНЕНИЕ НА ВСИЧКИ СТЪПКИ ---
    run_news_pipeline(db_manager, news_api_client)
    run_ai_analysis_pipeline(db_manager, ai_analyzer)
    run_market_data_pipeline(db_manager, coingecko_client)
    run_kucoin_historical_data_pipeline(db_manager, kucoin_handler)
    run_defillama_pipeline(db_manager, defillama_handler) # Добавяме новата стъпка

    print("\n🏁🏁🏁 PIPELINE FINISHED SUCCESSFULLY! 🏁🏁🏁")


if __name__ == "__main__":
    main()