# src/analysis/ai_analyzer.py

import ollama
import json
import time  # Импортваме 'time', за да можем да правим паузи
import logging # Ще използваме logging и тук за консистентност
from typing import Dict, Any
from config import OLLAMA_MODEL

# Използваме същия logger формат
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AIAnalyzer:
    """
    Клас, отговорен за комуникацията с Ollama и анализа на текст.
    Вече включва и механизъм за повторен опит при грешка.
    """
    def __init__(self, model: str = OLLAMA_MODEL, max_retries: int = 3):
        self.model = model
        self.max_retries = max_retries # Колко пъти да опитаме при грешка
        logging.info(f"🧠 AI Analyzer initialized with model: {self.model}")

    def analyze_article_title(self, title: str, is_economic: bool = False) -> Dict[str, Any] or None:
        """
        Анализира заглавие на статия и връща структуриран речник с резултатите.
        """
        prompt = self._build_prompt(title, is_economic)

        # --- НОВА ЛОГИКА: Цикъл за повторни опити ---
        for attempt in range(self.max_retries):
            try:
                # Опитваме да изпълним заявката
                response = ollama.chat(
                    model=self.model,
                    format='json',
                    messages=[{'role': 'user', 'content': prompt}]
                )

                # Ако всичко е успешно, обработваме и връщаме резултата
                analysis_data = json.loads(response['message']['content'])
                
                # Връщаме целия речник, вместо отделни променливи
                return {
                    "summary": analysis_data.get("summary", "N/A"),
                    "sentiment": analysis_data.get("sentiment", "Neutral"),
                    "reasoning": analysis_data.get("reasoning", "N/A"),
                    "investment_factors": analysis_data.get("investment_factors", "None")
                }
            except Exception as e:
                # Ако има грешка, логваме я и продължаваме към следващия опит
                logging.warning(f"⚠️ Attempt {attempt + 1}/{self.max_retries} failed for '{title}': {e}")
                
                # Ако това е последният опит, отказваме се
                if attempt + 1 == self.max_retries:
                    logging.error(f"❌ AI analysis failed for '{title}' after {self.max_retries} attempts.")
                    return None
                
                # Изчакваме малко преди да опитаме отново
                time.sleep(2)
        
        return None # Връщаме None, ако цикълът приключи неуспешно

    def _build_prompt(self, title: str, is_economic: bool) -> str:
        """Помощен метод за конструиране на промпта за AI модела (остава непроменен)."""
        # ... съдържанието на този метод е същото като преди ...
        prompt = f"""
        Analyze the following news article title and provide a structured JSON response.
        The title is: "{title}"

        Your response MUST be a single JSON object with the following four keys:
        1. "summary": A brief, one-sentence summary of the article's likely content.
        2. "sentiment": The overall sentiment. Must be one of: "Positive", "Negative", "Neutral".
        3. "reasoning": A short explanation for why you chose that sentiment, based ONLY on the title.
        4. "investment_factors": Key factors or entities mentioned that could influence investment decisions (e.g., specific companies, regulations, market trends). List them as a comma-separated string. If none, return "None".

        Example response format:
        {{
            "summary": "The article discusses a significant price increase for Bitcoin, potentially driven by new institutional investments.",
            "sentiment": "Positive",
            "reasoning": "The title mentions a price surge and favorable market conditions, which is bullish for the asset.",
            "investment_factors": "Bitcoin, institutional investment"
        }}
        """

        if is_economic:
            prompt += "\n\nIMPORTANT CONTEXT: This title is from a major economic news event. Analyze its potential market-wide significance with higher priority."

        prompt += "\n\nNow, analyze the provided title and generate the JSON object."
        return prompt