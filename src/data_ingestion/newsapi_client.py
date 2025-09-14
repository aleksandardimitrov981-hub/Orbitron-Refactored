# src/data_ingestion/newsapi_client.py
import logging
from newsapi import NewsApiClient as ApiClient
from typing import List, Dict, Any
from config import NEWSAPI_API_KEY, ASSETS_TO_TRACK # <-- НОВ ИМПОРТ

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ECONOMIC_NEWS_SOURCES = 'bloomberg,reuters,the-wall-street-journal,financial-times'

class NewsApiClient:
    def __init__(self):
        if not NEWSAPI_API_KEY or "ТВОЯТ" in NEWSAPI_API_KEY:
            raise ValueError("NewsAPI ключът не е конфигуриран в .env файла.")
        self.api = ApiClient(api_key=NEWSAPI_API_KEY)
        logging.info("📰 NewsAPI Client initialized.")

    # --- НОВ МЕТОД: Целенасочено търсене за всеки актив ---
    def fetch_asset_news(self) -> List[Dict[str, Any]]:
        """
        Извлича новини за ВСЕКИ актив, дефиниран в ASSETS_TO_TRACK.
        Прави отделна заявка за всеки, за да гарантира релевантност.
        """
        logging.info("🔍 Fetching asset-specific news from NewsAPI...")
        all_articles = []
        # Използваме set, за да избегнем дубликати, ако една статия споменава два актива
        processed_urls = set()

        # Взимаме имената на активите от конфигурацията (напр. 'bitcoin', 'ethereum')
        asset_keywords = list(ASSETS_TO_TRACK.keys())

        for asset in asset_keywords:
            logging.info(f"    -> Searching for '{asset}'...")
            try:
                response = self.api.get_everything(
                    q=f'"{asset}"',  # Търсим за точното име на актива
                    language='en',
                    sort_by='publishedAt',
                    page_size=15  # 15 новини на актив са достатъчни
                )
                
                # Подаваме името на актива, за да "маркираме" новините
                articles = self._process_articles(
                    response.get('articles', []),
                    category=asset, # <-- ТУК Е КЛЮЧОВАТА ПРОМЯНА
                    processed_urls=processed_urls
                )
                all_articles.extend(articles)
                logging.info(f"        Found {len(articles)} new articles for {asset}.")

            except Exception as e:
                logging.error(f"    -> ❌ Error fetching news for {asset}: {e}")
        
        return all_articles

    # --- Този метод остава същият ---
    def fetch_economic_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Извлича силно фокусирани икономически новини от топ източници."""
        logging.info(f"📈 Searching NewsAPI for economic keywords: {keywords}")
        query_string = ' OR '.join(f'"{k}"' for k in keywords)
        try:
            response = self.api.get_everything(
                q=query_string, sources=ECONOMIC_NEWS_SOURCES,
                language='en', sort_by='relevancy', page_size=20
            )
            articles = self._process_articles(response.get('articles', []), category='economic_event')
            logging.info(f"   -> Found {len(articles)} economic news articles.")
            return articles
        except Exception as e:
            logging.error(f"   -> ❌ Error fetching economic news: {e}")
            return []

    # --- Леко подобрение в _process_articles ---
    def _process_articles(self, articles_data: List[Dict[str, Any]], category: str, processed_urls: set = None) -> List[Dict[str, Any]]:
        """Помощен метод за обработка на отговора от API-то."""
        processed = []
        for article in articles_data:
            url = article.get('url')
            # Проверяваме за дубликати, ако ни е подаден set
            if url and (processed_urls is None or url not in processed_urls):
                processed_article = {
                    'source': article.get('source', {}).get('name', 'N/A'),
                    'title': article.get('title'), 'url': url,
                    'published_at': article.get('publishedAt', 'N/A'),
                    'category': category  # Записваме категорията (напр. 'bitcoin')
                }
                
                if processed_article['title']:
                    processed.append(processed_article)
                    if processed_urls is not None:
                        processed_urls.add(url)
        return processed

# --- Обновяваме тестовия блок ---
if __name__ == '__main__':
    logging.info("--- Testing NewsAPI Client ---")
    try:
        client = NewsApiClient()
        asset_articles = client.fetch_asset_news()
        
        if asset_articles:
            logging.info(f"\nSuccessfully fetched {len(asset_articles)} asset-specific articles.")
            logging.info(f"Example article: {asset_articles[0]['title']} (Category: {asset_articles[0]['category']})")

    except ValueError as e:
        logging.error(e)