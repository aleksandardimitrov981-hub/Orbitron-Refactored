# src/data_ingestion/rss_client.py
import feedparser
from typing import List, Dict, Any

# Списъкът с емисии вече може да се управлява оттук
RSS_FEEDS = [
    "https://www.investing.com/rss/news_301.rss",    # Cryptocurrency News
    "https://www.investing.com/rss/news_1.rss",      # Forex News
    "https://www.investing.com/rss/news_95.rss",     # Economic Indicators News
]

def fetch_rss_articles() -> List[Dict[str, Any]]:
    """
    Извлича статии от дефинирания списък с RSS емисии.
    Връща списък от речници, всеки представляващ една статия.
    """
    all_articles = []
    print(f"📰 Fetching articles from {len(RSS_FEEDS)} RSS feeds...")

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)

            # Проверка за грешки при парсването
            if feed.bozo:
                raise Exception(feed.bozo_exception)

            feed_title = feed.feed.get('title', url)
            for entry in feed.entries:
                article = {
                    'source': feed_title,
                    'title': entry.get('title', 'No Title Provided'),
                    'url': entry.get('link'),
                    'published_at': entry.get('published', 'N/A')
                }
                # Добавяме статията само ако има URL адрес
                if article['url']:
                    all_articles.append(article)

            print(f"   -> Found {len(feed.entries)} articles from {feed_title}")

        except Exception as e:
            print(f"   -> ❌ Error fetching from {url}: {e}")

    print(f"✅ Total articles fetched from RSS: {len(all_articles)}")
    return all_articles

if __name__ == '__main__':
    # Тестов код, който се изпълнява само ако стартираме файла директно
    print("--- Testing RSS Client ---")
    articles = fetch_rss_articles()
    if articles:
        print(f"\nSuccessfully fetched {len(articles)} articles.")
        print("Example article:")
        print(articles[0])
    else:
        print("\nNo articles were fetched.")