# src/dashboard/app.py
import sys
import os
import streamlit as st
import pandas as pd

# --- ТРИКЪТ ЗА ПРАВИЛНИТЕ ИМПОРТИ ---
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# --- Новите, по-чисти импорти ---
from config import ASSETS_TO_TRACK
from src.database.database_manager import DatabaseManager

# --- Конфигурация на страницата ---
st.set_page_config(layout="wide", page_title="Orbitron AI Dashboard")
st.title("🚀 ORBITRON AI - Аналитично Табло")

# Преобразуваме речника с активи в списък за селекцията
ASSET_NAMES = list(ASSETS_TO_TRACK.keys())

@st.cache_data(ttl=600)  # Кешираме данните за 10 минути
def load_data():
    """Зарежда всички анализирани статии и пазарни данни."""
    db = DatabaseManager()
    news_list = db.get_all_analyzed_articles()
    market_data_list = db.get_all_market_data()
    
    news_df = pd.DataFrame(news_list)
    market_df = pd.DataFrame(market_data_list)
    
    # Обработваме датите
    if not market_df.empty:
        market_df['date'] = pd.to_datetime(market_df['date'])
    
    return news_df, market_df

# --- Зареждане на данните ---
news_data, market_data = load_data()

if market_data.empty:
    st.warning("Няма налични пазарни данни. Стартирайте `scripts/run_pipeline.py`, за да съберете данни.")
    st.stop()

# --- Контроли в страничната лента ---

# V V V ЕТО ТУК Е ДОБАВКАТА ЗА ЛОГОТО V V V
st.sidebar.image("assets/logo.png", use_container_width=True)
# ^ ^ ^ ЕТО ТУК Е ДОБАВКАТА ЗА ЛОГОТО ^ ^ ^

st.sidebar.header("Настройки на Анализа")
selected_asset_name = st.sidebar.selectbox("Избери Актив:", ASSET_NAMES)
selected_asset_id = ASSETS_TO_TRACK[selected_asset_name]

# --- Филтриране на данните ---
asset_market_data = market_data[market_data['asset_id'] == selected_asset_id].copy()
asset_news_data = news_data[news_data['title'].str.contains(selected_asset_name.split('-')[0], case=False, na=False)].copy()

if asset_market_data.empty:
    st.warning(f"Няма пазарни данни за '{selected_asset_name}'.")
    st.stop()

# --- Показване на ключови метрики ---
st.header(f"Ключови Метрики за {selected_asset_name.capitalize()}")
asset_market_data.sort_values('date', inplace=True, ascending=False)
latest_data = asset_market_data.iloc[0]

price_change_str = "N/A"
if len(asset_market_data) > 1:
    previous_data = asset_market_data.iloc[1]
    price_change = latest_data['price'] - previous_data['price']
    price_change_percent = (price_change / previous_data['price']) * 100 if previous_data['price'] != 0 else 0
    price_change_str = f"{price_change:,.4f} ({price_change_percent:.2f}%)"

col1, col2, col3 = st.columns(3)
col1.metric("Последна Цена (USD)", f"${latest_data['price']:,.4f}", price_change_str)
col2.metric("Пазарна Капитализация", f"${latest_data['market_cap']:,.0f}")
col3.metric("Обем за 24ч", f"${latest_data['total_volume']:,.0f}")
st.markdown("---")

# --- AI ОБОБЩЕН АНАЛИЗ ---
st.header(f"🤖 AI Обобщен Анализ за {selected_asset_name.capitalize()}")

if asset_news_data.empty:
    st.info("Няма налични AI анализи за този актив.")
else:
    sentiment_counts = asset_news_data['sentiment'].value_counts()
    pos_count = sentiment_counts.get("Positive", 0)
    neg_count = sentiment_counts.get("Negative", 0)
    neu_count = sentiment_counts.get("Neutral", 0)

    st.subheader("Разбивка на Настроенията")
    scol1, scol2, scol3 = st.columns(3)
    scol1.metric("🟢 Позитивни Новини", pos_count)
    scol2.metric("🔴 Негативни Новини", neg_count)
    scol3.metric("⚪ Неутрални Новини", neu_count)

    st.subheader("AI Обосновка на Настроенията")
    total_news = pos_count + neg_count
    if total_news > 0:
        pos_percentage = (pos_count / total_news) * 100
        if pos_percentage > 65:
            summary_text = f"Настроението е **силно позитивно**. Над {int(pos_percentage)}% от анализираните новини сочат към благоприятни развития."
            st.success(summary_text)
        elif pos_percentage > 40:
            summary_text = f"Настроението е **предимно неутрално с лек позитивен уклон**. Новините са смесени, но позитивните преобладават."
            st.info(summary_text)
        else:
            summary_text = f"Настроението е **предимно негативно**. Повечето новини дискутират потенциални рискове или неблагоприятни събития."
            st.warning(summary_text)
    else:
        st.info("Няма достатъчно позитивни или негативни новини за формиране на ясна обосновка.")

    st.subheader("Ключови теми от последните новини")
    asset_news_data['published_at'] = pd.to_datetime(asset_news_data['published_at'], errors='coerce', utc=True)
    recent_news = asset_news_data.sort_values(by='published_at', ascending=False).head(5)
    
    for index, row in recent_news.iterrows():
        st.markdown(f"- **{row['sentiment']}**: *{row['summary']}*")

# --- СЕКЦИЯ С ДЕТАЙЛНИ НОВИНИ ---
st.markdown("---")
st.header("Всички свързани новини")
if not asset_news_data.empty:
    sorted_news = asset_news_data.sort_values(by='published_at', ascending=False)
    for index, row in sorted_news.head(20).iterrows():
        with st.expander(f"**{row['title']}** (Настроение: {row['sentiment']})"):
            st.markdown(f"**AI Резюме:** *{row['summary']}*")
            st.markdown(f"**AI Обосновка:** {row['reasoning']}")
            st.markdown(f"**AI Фактори:** {row['investment_factors']}")
            st.markdown(f"**Източник:** {row['source']} | **Публикувано на:** {pd.to_datetime(row['published_at']).strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"[Прочети цялата статия]({row['url']})")
else:
    st.write("Няма намерени новини за този актив.")