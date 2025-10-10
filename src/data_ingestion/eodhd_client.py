import os
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any

import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from config import EODHD_API_KEY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EODHDClient:
    """
    Клас за извличане на Forex данни от EOD Historical Data (EODHD) API.
    """
    BASE_URL = "https://eodhd.com/api/"

    def __init__(self):
        if not EODHD_API_KEY:
            logging.error("❌ EODHD API ключът не е конфигуриран!")
            raise ValueError("Моля, дефинирайте EODHD_API_KEY в .env и config.py файловете.")
        self.api_key = EODHD_API_KEY
        logging.info("📈 EODHD Client initialized successfully.")

    def get_forex_data(self, symbol: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
        """
        Извлича исторически дневни данни за Forex символ.
        """
        endpoint = f"{self.BASE_URL}eod/{symbol}"
        params = {
            'api_token': self.api_key,
            'fmt': 'json',
            'period': 'd',
            'from': from_date,
            'to': to_date
        }

        logging.info(f"Fetching Forex data from EODHD for {symbol}...")
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logging.warning(f"EODHD API (forex) did not return a list for {symbol}.")
                return []
            logging.info(f"✅ Successfully fetched {len(data)} daily records for {symbol}.")
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Error fetching Forex data for {symbol}: {e}")
            return []

if __name__ == '__main__':
    # Тестовият блок е обновен да тества само Forex данните
    client = EODHDClient()
    today = datetime.now()
    last_month = today - timedelta(days=30)
    from_date_str = last_month.strftime('%Y-%m-%d')
    to_date_str = today.strftime('%Y-%m-%d')
    
    print("\n--- Testing Forex Data (Dollar Index - DXY) ---")
    dxy_data = client.get_forex_data("DXY.INDX", from_date_str, to_date_str)
    if dxy_data:
        print(f"Found {len(dxy_data)} daily records for DXY. Last record:")
        print(f"  - {dxy_data[-1]}")