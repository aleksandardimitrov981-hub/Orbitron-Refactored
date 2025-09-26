import logging
from datetime import datetime, timedelta
from newsapi import NewsApiClient as ApiClient
from typing import List, Dict, Any, Optional

# Импортираме нужните променливи от твоя config файл
from config import NEWSAPI_API_KEY, ASSETS_TO_TRACK 

# Настройваме логър
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Преместваме константата тук, за да е на едно място
ECONOMIC_NEWS_SOURCES = 'bloomberg,reuters,the-wall-street-journal,financial-times'

class NewsApiClient:
    def __init__(self):
        if not NEWSAPI_API_KEY:
            logging.error("❌ NewsAPI ключът не е конфигуриран!")
            raise ValueError("NewsAPI ключът не е конфигуриран в .env файла.")
        self.api = ApiClient(api_key=NEWSAPI_API_KEY)
        logging.info("📰 NewsAPI Client initialized successfully.")

    def _make_api_request(self, q: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Обединен помощен метод за извършване на заявки към NewsAPI.
        Това премахва дублирането на код.
        """
        try:
            logging.info(f"Fetching news from NewsAPI with query: '{q}'")
            response = self.api.get_everything(q=q, language='en', **kwargs)
            
            if response.get('status') == 'error':
                logging.error(f"❌ NewsAPI Error: {response.get('message')}")
                return []

            return response.get('articles', [])
        except Exception as e:
            logging.error(f"❌ An exception occurred during NewsAPI request: {e}")
            return []

    # --- ТОВА Е НОВИЯТ, ПО-УМЕН МЕТОД ---
    def fetch_asset_news(self) -> List[Dict[str, Any]]:
        """
        Автоматично извлича новини за всички активи, дефинирани в ASSETS_TO_TRACK.
        """
        all_asset_articles = []
        
        # Изчисляваме "от вчера до днес", за да са актуални новините
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        # ASSETS_TO_TRACK е речник, например {'bitcoin': 'btc-bitcoin', 'solana': 'sol-solana'}
        # Ние ще използваме ключовете ('bitcoin', 'solana') за търсене.
        for asset_name in ASSETS_TO_TRACK.keys():
            logging.info(f"Searching news for asset: {asset_name}...")
            # Търсим по име на актива + "crypto", за да филтрираме шума
            query = f'"{asset_name}" AND "crypto"'
            
            articles_data = self._make_api_request(
                q=query,
                sort_by='publishedAt',
                page_size=5,  # 5 новини за всеки актив са достатъчни
                from_param=yesterday,
                to=today
            )
            # Задаваме категория = името на актива
            processed = self._process_articles(articles_data, category=asset_name)
            all_asset_articles.extend(processed)
        
        logging.info(f"✅ Fetched a total of {len(all_asset_articles)} articles for tracked assets.")
        return all_asset_articles

    def fetch_economic_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        query_string = ' OR '.join(f'"{k}"' for k in keywords)
        articles_data = self._make_api_request(
            q=query_string,
            sources=ECONOMIC_NEWS_SOURCES,
            sort_by='relevancy',
            page_size=20
        )
        return self._process_articles(articles_data, category='economic_event')
    
    # Този метод е премахнат, защото fetch_asset_news го замества и е по-добър
    # def fetch_general_news(self, keywords: List[str]) -> List[Dict[str, Any]]: ...

    def _process_articles(self, articles_data: List[Dict[str, Any]], category: Optional[str] = None) -> List[Dict[str, Any]]:
        processed = []
        for article in articles_data:
            processed_article = {
                'source': article.get('source', {}).get('name', 'N/A'),
                'title': article.get('title'),
                'url': article.get('url'),
                'published_at': article.get('publishedAt', 'N/A'),
                # Добавяме категорията директно тук
                'category': category if category else 'general'
            }
            # Проверяваме за валидни заглавие, URL и премахваме "[Removed]" заглавия
            if all([processed_article['title'], 
                    processed_article['url'], 
                    processed_article['title'] != '[Removed]']):
                processed.append(processed_article)
        return processed