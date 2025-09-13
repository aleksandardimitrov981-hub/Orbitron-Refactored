# src/data_ingestion/coingecko_client.py
from pycoingecko import CoinGeckoAPI
from datetime import datetime
from typing import List, Dict, Any

class CoinGeckoClient:
    """
    Клас за извличане на пазарни данни от CoinGecko.
    """
    def __init__(self):
        self.api = CoinGeckoAPI()
        print("🦎 CoinGecko Client initialized.")

    def fetch_historical_data(self, asset_id: str, days: int) -> List[Dict[str, Any]]:
        """
        Извлича исторически данни (цена, капитализация, обем) за последните N дни.
        """
        print(f"🦎 Fetching historical data for '{asset_id}' for the last {days} days...")

        try:
            chart_data = self.api.get_coin_market_chart_by_id(
                id=asset_id,
                vs_currency='usd',
                days=days,
                interval='daily' # Изискваме дневни данни
            )

            # Обработваме данните, за да ги върнем в удобен формат
            processed_data = self._process_chart_data(asset_id, chart_data)

            print(f"   -> Successfully processed {len(processed_data)} records for '{asset_id}'.")
            return processed_data

        except Exception as e:
            print(f"   -> ❌ Error fetching data from CoinGecko for '{asset_id}': {e}")
            return []

    def _process_chart_data(self, asset_id: str, chart_data: dict) -> List[Dict[str, Any]]:
        """Помощен метод за комбиниране на списъците от CoinGecko."""
        processed = []
        prices = chart_data.get('prices', [])
        market_caps = chart_data.get('market_caps', [])
        total_volumes = chart_data.get('total_volumes', [])

        # Уверяваме се, че имаме данни във всички списъци
        if not all([prices, market_caps, total_volumes]):
            return []

        for i in range(len(prices)):
            # Времето идва в милисекунди, преобразуваме го
            timestamp_ms = prices[i][0]
            date = datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d')

            # Добавяме -1, ако някоя стойност липсва, за да не се чупи програмата
            daily_record = {
                'asset_id': asset_id,
                'date': date,
                'price': prices[i][1] if i < len(prices) else -1,
                'market_cap': market_caps[i][1] if i < len(market_caps) else -1,
                'total_volume': total_volumes[i][1] if i < len(total_volumes) else -1,
            }
            processed.append(daily_record)

        return processed

if __name__ == '__main__':
    print("--- Testing CoinGecko Client ---")
    client = CoinGeckoClient()
    # Тестваме с bitcoin за последните 5 дни
    btc_data = client.fetch_historical_data(asset_id='bitcoin', days=5)

    if btc_data:
        print(f"\nSuccessfully fetched {len(btc_data)} records.")
        print("Example record:")
        print(btc_data[-1]) # Показваме последния запис
    else:
        print("\nNo market data was fetched.")