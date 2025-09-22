# src/data_ingestion/newsapi_client.py
from newsapi import NewsApiClient as ApiClient
from typing import List, Dict, Any
from config import NEWSAPI_API_KEY

ECONOMIC_NEWS_SOURCES = 'bloomberg,reuters,the-wall-street-journal,financial-times'

class NewsApiClient:
    def __init__(self):
        if not NEWSAPI_API_KEY:
            raise ValueError("NewsAPI ключът не е конфигуриран в .env файла.")
        self.api = ApiClient(api_key=NEWSAPI_API_KEY)

    def fetch_general_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        query_string = ' OR '.join(f'"{k}"' for k in keywords)
        try:
            response = self.api.get_everything(
                q=query_string,
                language='en',
                sort_by='publishedAt',
                page_size=20
            )
            return self._process_articles(response.get('articles', []))
        except Exception as e:
            print(f"   -> ❌ Error fetching general news from NewsAPI: {e}")
            return []

    def fetch_economic_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        query_string = ' OR '.join(f'"{k}"' for k in keywords)
        try:
            response = self.api.get_everything(
                q=query_string,
                sources=ECONOMIC_NEWS_SOURCES,
                language='en',
                sort_by='relevancy',
                page_size=20
            )
            return self._process_articles(response.get('articles', []), category='economic_event')
        except Exception as e:
            print(f"   -> ❌ Error fetching economic news from NewsAPI: {e}")
            return []

    def _process_articles(self, articles_data: List[Dict[str, Any]], category: str = None) -> List[Dict[str, Any]]:
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