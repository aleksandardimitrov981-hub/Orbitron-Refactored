# src/analysis/ai_analyzer.py
import ollama
import json
from typing import Dict, Any
# Импортваме името на модела от централната конфигурация
from config import OLLAMA_MODEL

class AIAnalyzer:
    """
    Клас, отговорен за комуникацията с Ollama и анализа на текст.
    """
    def __init__(self, model: str = OLLAMA_MODEL):
        self.model = model
        print(f"🧠 AI Analyzer initialized with model: {self.model}")

    def analyze_article_title(self, title: str, is_economic: bool = False) -> Dict[str, Any] or None:
        """
        Анализира заглавие на статия и връща структуриран речник с резултатите.
        """
        prompt = self._build_prompt(title, is_economic)

        try:
            response = ollama.chat(
                model=self.model,
                format='json',
                messages=[{'role': 'user', 'content': prompt}]
            )

            # json.loads превръща текстовия JSON отговор в Python речник
            analysis_data = json.loads(response['message']['content'])

            # Връщаме целия речник, вместо отделни променливи
            return {
                "summary": analysis_data.get("summary", "N/A"),
                "sentiment": analysis_data.get("sentiment", "Neutral"),
                "reasoning": analysis_data.get("reasoning", "N/A"),
                "investment_factors": analysis_data.get("investment_factors", "None")
            }
        except Exception as e:
            print(f"   -> ❌ Error during AI analysis for '{title}': {e}")
            return None

    def _build_prompt(self, title: str, is_economic: bool) -> str:
        """Помощен метод за конструиране на промпта за AI модела."""
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

if __name__ == '__main__':
    print("--- Testing AI Analyzer ---")
    analyzer = AIAnalyzer()
    test_title = "Bitcoin Surges Past $80,000 as Major Bank Announces Crypto Services"
    analysis = analyzer.analyze_article_title(test_title)

    if analysis:
        print("\nAnalysis successful:")
        # Използваме json.dumps за красиво отпечатване на речника
        print(json.dumps(analysis, indent=2))
    else:
        print("\nAnalysis failed.")