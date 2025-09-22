# scripts/test_kucoin.py
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.data_ingestion.kucoin_client import KucoinHandler
from datetime import datetime, timedelta

def run_test():
    print("--- 🧪 Testing KuCoin Integration (Market Data Only) ---")
    kucoin = KucoinHandler()
    
    if kucoin.market_client:
        print("\n--- Testing Historical Data ---")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        btc_data = kucoin.get_historical_data(
            'BTC-USDT', 
            start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d')
        )
        if btc_data:
            print("✅ Successfully fetched historical data for BTC-USDT.")
            print("Last record:", btc_data[-1])
        else:
            print("⚠️ Failed to fetch historical data.")
    else:
        print("\n❌ KuCoin client failed to initialize.")

if __name__ == "__main__":
    run_test()