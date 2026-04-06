#!/usr/bin/env python3
"""
Career Radar — Streamlit dashboard (русский интерфейс)
"""

import pandas as pd
import streamlit as st
from datetime import datetime

from collector import DB_PATH, get_connection, init_db

st.set_page_config(page_title="Career Radar", layout="wide", page_icon="📡")

# --- CSS стили ---
st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; margin-bottom: 0; }
    .main-sub { color: #888; font-size: 0.9rem; margin-bottom: 1.5rem; }
    .stat-card { background: #f8f9fa; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.5rem; }
    .stat-label { font-size: 0.75rem; color: #888; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.05em; }
    .stat-value { font-size: 1.8rem; font-weight: 600; line-height: 1.2; }
    .stat-value.red { color: #c0392b; }
    .stat-value.green { color: #27ae60; }
    .stat-value.blue { color: #2980b9; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; margin-right: 6px; }
    .badge-layoffs { background: #fde8e8; color: #c0392b; }
    .badge-hiring { background: #e8f8e8; color: #27ae60; }
    .badge-hiring_freeze { background: #fff3e0; color: #e67e22; }
    .badge-startup { background: #e8f0fe; color: #2980b9; }
    .badge-visa { background: #f3e5f5; color: #8e44ad; }
    .badge-remote_work { background: #f1f1f1; color: #555; }
    .badge-tech { background: #e8f4fd; color: #1a6fa8; }
    .badge-ai_jobs { background: #e8fdf5; color: #1a8a6e; }
    .news-card { border: 1px solid #eee; border-radius: 10px; padding: 0.85rem 1rem; margin-bottom: 0.5rem; background: white; }
    .news-title { font-size: 0.9rem; font-weight: 500; margin-bottom: 4px; line-height: 1.4; }
    .news-meta { font-size: 0.75rem; color: #888; }
    .insight-card { border: 1px solid #e8e8e8; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; background: white; }
    .insight-pattern { background: #f0f7ff; border-left: 3px solid #2980b9; padding: 8px 12px; border-radius: 0 8px 8px 0; font-size: 0.85rem; color: #444; margin-top: 10px; }
    .section-title { font-size: 0.75rem; font-weight: 500; color: #888; text-transform: uppercase; letter-spacing: 0.07em; margin: 1.25rem 0 0.5rem; }
    .trend-label { font-size: 0.8rem; color: #555; }
    .stButton > button { border-radius: 8px; border: 1px solid #ddd; background: white; font-size: 0.85rem; text-align: left; width: 100%; padding: 0.5rem 0.75rem; }
    .stButton > button:hover { background: #f8f9fa; border-color: #bbb; }
    div[data-testid="stSidebarContent"] { padding-top: 1rem; }
    .live-dot { display: inline-block; width: 8px; height: 8px; background: #27ae60; border-radius: 50%; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

CATEGORY_LABELS = {
    "layoffs": "увольнения",
    "hiring": "найм",
    "hiring_freeze": "заморозка найма",
    "startup": "стартапы",
    "visa": "визы",
    "remote_work": "удалёнка",
    "tech": "технологии",
    "ai_jobs": "AI & работа",
}

CATEGORY_BADGE = {
    "layoffs": "badge-layoffs",
    "hiring": "badge-hiring",
    "hiring_freeze": "badge-hiring_freeze",
    "startup": "badge-startup",
    "visa": "badge-visa",
    "remote_work": "badge-remote_work",
    "tech": "badge-tech",
    "ai_jobs": "badge-ai_jobs",
}


@st.cache_data(ttl=60)
def load_articles() -> pd.DataFrame:
    init_db()
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT id, title, url, source, published_date, summary, category, is_analyzed FROM articles ORDER BY COALESCE(published_date, '') DESC",
            conn,
        )
    finally:
        conn.close()


@st.cache_data(ttl=60)
def load_insights(limit: int = 10) -> pd.DataFrame:
    init_db()
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT id, created_at, content, article_count FROM insights ORDER BY created_at DESC LIMIT ?",
            conn, params=(int(limit),)
        )
    finally:
        conn.close()


def badge(category: str) -> str:
    cls = CATEGORY_BADGE.get(category, "badge-tech")
    label = CATEGORY_LABELS.get(category, category)
    return f'<span class="badge {cls}">{label}</span>'


def main():
    df = load_articles()
    insights_df = load_insights()

    # --- Шапка ---
    col_title, col_status = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="main-title">📡 Career Radar</div>', unsafe_allow_html=True)
        now = datetime.now().strftime("%d.%m.%Y, %H:%M")
        st.markdown(f'<div class="main-sub">Разведка рынка труда США · обновлено {now}</div>', unsafe_allow_html=True)
    with col_status:
        st.markdown('<br><span style="color:#27ae60;font-size:0.85rem;">● в сети</span>', unsafe_allow_html=True)

    # --- Боковая панель ---
    with st.sidebar:
        st.markdown('<div class="section-title">Фильтры</div>', unsafe_allow_html=True)
        all_cats = sorted(df["category"].dropna().unique().tolist()) if len(df) else []
        selected = st.multiselect(
            "Категории",
            options=all_cats,
            default=all_cats,
            format_func=lambda x: CATEGORY_LABELS.get(x, x)
        )

        st.markdown('<div class="section-title">Создать контент</div>', unsafe_allow_html=True)
        if len(insights_df) > 0:
            if st.button("✍️ Пост по последним трендам"):
                st.session_state["show_post"] = True

        st.markdown('<div class="section-title">Тренды за всё время</div>', unsafe_allow_html=True)
        if len(df) > 0:
            counts = df.groupby("category").size().sort_values(ascending=False)
            max_count = counts.max()
            for cat, count in counts.items():
                label = CATEGORY_LABELS.get(cat, cat)
                pct = int(count / max_count * 100)
                st.markdown(f'<div class="trend-label">{label} — {count}</div>', unsafe_allow_html=True)
                st.progress(pct / 100)

    filtered = df[df["category"].isin(selected)] if selected else df.iloc[0:0]

    # --- Статистика ---
    layoffs_count = len(filtered[filtered["category"] == "layoffs"])
    hiring_count = len(filtered[filtered["category"].isin(["hiring"])])
    startup_count = len(filtered[filtered["category"] == "startup"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''<div class="stat-card">
            <div class="stat-label">Всего статей</div>
            <div class="stat-value">{len(filtered)}</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="stat-card">
            <div class="stat-label">Увольнения</div>
            <div class="stat-value red">{layoffs_count}</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="stat-card">
            <div class="stat-label">Найм</div>
            <div class="stat-value green">{hiring_count}</div>
        </div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="stat-card">
            <div class="stat-label">Стартапы</div>
            <div class="stat-value blue">{startup_count}</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("---")

    # --- Два столбца: инсайты + новости ---
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-title">Лента новостей</div>', unsafe_allow_html=True)

        if len(filtered) == 0:
            st.info("Нет статей. Запусти `python3 collector.py` чтобы загрузить новости.")
        else:
            for _, row in filtered.head(50).iterrows():
                cat = row.get("category", "tech")
                title = row.get("title", "Без названия")
                source = row.get("source", "")
                pub = (row.get("published_date") or "")[:10]
                url = row.get("url", "#")
                st.markdown(f'''<div class="news-card">
                    <div>{badge(cat)}</div>
                    <div class="news-title"><a href="{url}" target="_blank" style="color:inherit;text-decoration:none;">{title}</a></div>
                    <div class="news-meta">{source} · {pub}</div>
                </div>''', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">AI-аналитика</div>', unsafe_allow_html=True)

        if len(insights_df) == 0:
            st.info("Инсайтов пока нет. Запусти `python3 analyzer.py` после загрузки новостей.")
        else:
            for _, row in insights_df.iterrows():
                date = (row.get("created_at") or "")[:16].replace("T", " ")
                count = int(row.get("article_count", 0))
                content = row.get("content", "")
                with st.expander(f"📊 {date} · {count} статей", expanded=True):
                    st.markdown(content)


if __name__ == "__main__":
    main()
