# src/data_ingestion/newsapi_client.py
from newsapi import NewsApiClient as ApiClient
from typing import List, Dict, Any
# Импортваме сигурно API ключа от главния config файл
from config import NEWSAPI_API_KEY

# Списък с авторитетни източници за икономически новини
ECONOMIC_NEWS_SOURCES = 'bloomberg,reuters,the-wall-street-journal,financial-times'

class NewsApiClient:
    """
    Клас за извличане на новини от NewsAPI.
    """
    def __init__(self):
        if not NEWSAPI_API_KEY or "ТВОЯТ" in NEWSAPI_API_KEY:
            raise ValueError("NewsAPI ключът не е конфигуриран в .env файла.")

        self.api = ApiClient(api_key=NEWSAPI_API_KEY)
        print("📰 NewsAPI Client initialized.")

    def fetch_general_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Извлича новини по списък с ключови думи.
        """
        print(f"🔍 Searching NewsAPI for general keywords: {keywords}")
        query_string = ' OR '.join(f'"{k}"' for k in keywords)

        try:
            response = self.api.get_everything(
                q=query_string,
                language='en',
                sort_by='publishedAt',
                page_size=20 # Можем да го направим настройка в config.py по-късно
            )

            articles = self._process_articles(response.get('articles', []))
            print(f"   -> Found {len(articles)} general news articles.")
            return articles
        except Exception as e:
            print(f"   -> ❌ Error fetching general news from NewsAPI: {e}")
            return []

    def fetch_economic_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Извлича силно фокусирани икономически новини от топ източници.
        """
        print(f"📈 Searching NewsAPI for economic keywords: {keywords}")
        query_string = ' OR '.join(f'"{k}"' for k in keywords)

        try:
            response = self.api.get_everything(
                q=query_string,
                sources=ECONOMIC_NEWS_SOURCES,
                language='en',
                sort_by='relevancy',
                page_size=20
            )

            articles = self._process_articles(response.get('articles', []), category='economic_event')
            print(f"   -> Found {len(articles)} economic news articles.")
            return articles
        except Exception as e:
            print(f"   -> ❌ Error fetching economic news from NewsAPI: {e}")
            return []

    def _process_articles(self, articles_data: List[Dict[str, Any]], category: str = None) -> List[Dict[str, Any]]:
        """Помощен метод за обработка на отговора от API-то."""
        processed = []
        for article in articles_data:
            processed_article = {
                'source': article.get('source', {}).get('name', 'N/A'),
                'title': article.get('title'),
                'url': article.get('url'),
                'published_at': article.get('publishedAt', 'N/A')
            }
            if category:
                processed_article['category'] = category

            if processed_article['title'] and processed_article['url']:
                processed.append(processed_article)
        return processed


if __name__ == '__main__':
    print("--- Testing NewsAPI Client ---")
    try:
        client = NewsApiClient()
        general_keywords = ['bitcoin', 'crypto']
        economic_keywords = ['inflation', 'interest rate', 'GDP']

        general_articles = client.fetch_general_news(general_keywords)
        economic_articles = client.fetch_economic_news(economic_keywords)

        if general_articles:
            print(f"\nExample general article: {general_articles[0]['title']}")
        if economic_articles:
            print(f"Example economic article: {economic_articles[0]['title']}")

    except ValueError as e:
        print(e)