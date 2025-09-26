import logging
import time
from typing import List, Dict, Any
import pandas as pd
from defillama2 import DefiLlama 

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()] 
)

class DefiLlamaHandler:
    """
    Клас за извличане на on-chain данни от DefiLlama API.
    """
    def __init__(self):
        try:
            self.llama = DefiLlama()
            logging.info("🦙 DefiLlama Handler initialized successfully.")
        except Exception as e:
            self.llama = None
            logging.error(f"❌ Failed to initialize DefiLlama client: {e}", exc_info=True)

    def get_chains_tvl(self, chain_names: List[str]) -> List[Dict[str, Any]]:
        """
        Извлича Total Value Locked (TVL) за списък от зададени блокчейн мрежи.
        """
        if not self.llama:
            logging.error("DefiLlama client is not initialized.")
            return []

        all_chains_tvl = []
        logging.info(f"Fetching TVL data for chains: {chain_names}")
        
        try:
            current_timestamp = int(time.time())
            
            # --- ЕТО Я ФИНАЛНАТА КОРЕКЦИЯ ---
            # Итерираме през всяка мрежа и правим отделна заявка с правилния метод
            for chain in chain_names:
                logging.info(f"  -> Fetching TVL for {chain}...")
                
                # ИЗПОЛЗВАМЕ ПРЕДЛОЖЕНИЯ ОТ ГРЕШКАТА МЕТОД: get_chain_hist_tvl
                response_df = self.llama.get_chain_hist_tvl(chain=chain)

                if isinstance(response_df, pd.DataFrame) and not response_df.empty:
                    # Взимаме последната (най-актуалната) стойност за TVL
                    latest_tvl_value = response_df['tvl'].iloc[-1]
                    
                    chain_data = {
                        'chain': chain,
                        'tvl': float(latest_tvl_value),
                        'timestamp': current_timestamp
                    }
                    all_chains_tvl.append(chain_data)
                    # Малка пауза, за да не товарим API-то
                    time.sleep(0.2) 
                else:
                    logging.warning(f"  -> No TVL data returned for {chain}")
            # --- КРАЙ НА КОРЕКЦИЯТА ---

            if all_chains_tvl:
                logging.info(f"✅ Successfully processed TVL data for {len(all_chains_tvl)} chains.")
            else:
                logging.warning("API calls were made, but processing resulted in an empty list.")
                
            return all_chains_tvl

        except Exception as e:
            logging.error(f"❌ An exception occurred while fetching TVL data from DefiLlama: {e}", exc_info=True)
            return []

# --- Тестовият блок остава същият ---
if __name__ == '__main__':
    logging.info("--- Testing DefiLlamaHandler ---")
    
    chains_to_track = ["Ethereum", "Solana", "Arbitrum", "Polygon"]
    
    handler = DefiLlamaHandler()
    tvl_data = handler.get_chains_tvl(chains_to_track)

    if tvl_data:
        print("\nSuccessfully fetched TVL data:")
        for data in tvl_data:
            tvl_in_billions = data['tvl'] / 1_000_000_000
            print(f"  - Chain: {data['chain']}, TVL: ${tvl_in_billions:.2f}B")
    else:
        print("\nCould not fetch TVL data. Check the logs above for errors.")