import logging
from datetime import datetime
from kucoin.client import Market
from config import KUCOIN_API_KEY, KUCOIN_API_SECRET, KUCOIN_API_PASSPHRASE
from typing import List, Dict, Any

# Конфигурираме логър за този модул
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KucoinHandler:
    """
    Клас за работа с KuCoin API - само за ПУБЛИЧНИ данни (пазарни данни).
    """
    def __init__(self):
        try:
            self.market_client = Market(key=KUCOIN_API_KEY, secret=KUCOIN_API_SECRET, passphrase=KUCOIN_API_PASSPHRASE)
            logging.info("✅ KuCoin Market Client initialized successfully.")
        except Exception as e:
            self.market_client = None
            logging.error(f"❌ Error initializing KuCoin Market Client: {e}")

    def get_historical_data(self, symbol: str, start_date: str, end_date: str, kline_type: str = '1day') -> List[Dict[str, Any]]:
        """Извлича исторически данни (свещи) за даден символ."""
        if not self.market_client:
            logging.error("KuCoin клиентът не е инициализиран. Заявката е прекратена.")
            return []
            
        try:
            logging.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}...")
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            klines = self.market_client.get_kline(symbol, kline_type, start=start_ts, end=end_ts)
            
            logging.info(f"✅ Fetched {len(klines)} k-line records for {symbol}.")
            
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
            logging.error(f"❌ Error fetching historical data for {symbol}: {e}")
            return []