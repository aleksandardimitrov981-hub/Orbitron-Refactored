# src/data_ingestion/kucoin_client.py
from datetime import datetime
from kucoin.client import Market
from config import KUCOIN_API_KEY, KUCOIN_API_SECRET, KUCOIN_API_PASSPHRASE

class KucoinHandler:
    """
    Клас за работа с KuCoin API - само за ПУБЛИЧНИ данни (пазарни данни).
    """
    def __init__(self):
        try:
            # Вече използваме само Market клиента, който не изисква удостоверяване за повечето заявки
            self.market_client = Market(key=KUCOIN_API_KEY, secret=KUCOIN_API_SECRET, passphrase=KUCOIN_API_PASSPHRASE)
            print("✅ KuCoin Market Client initialized successfully.")
        except Exception as e:
            self.market_client = None
            print(f"❌ Error initializing KuCoin Market Client: {e}")

    def get_historical_data(self, symbol: str, start_date: str, end_date: str, kline_type: str = '1day'):
        """Извлича исторически данни (свещи) за даден символ."""
        if not self.market_client:
            return []
        try:
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            klines = self.market_client.get_kline(symbol, kline_type, start=start_ts, end=end_ts)
            
            print(f"Fetched {len(klines)} k-line records for {symbol}.")
            processed_klines = []
            for k in klines:
                processed_klines.append({
                    'timestamp': int(k[0]),
                    'open': float(k[1]),
                    'close': float(k[2]),
                    'high': float(k[3]),
                    'low': float(k[4]),
                    'volume': float(k[5])
                })
            return processed_klines
        except Exception as e:
            print(f"❌ Error fetching historical data for {symbol}: {e}")
            return []