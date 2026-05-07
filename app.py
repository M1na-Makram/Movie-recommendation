import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_all
from content_based import ContentBasedFilter
from collaborative import CollaborativeFilter
from hybrid import HybridRecommender
from evaluation import full_evaluation
from posters import get_poster_url, get_posters_parallel, PLACEHOLDER

st.set_page_config(page_title="CineMatch AI", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")

# ─── PREMIUM CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg-primary: #0a0a0f;
    --bg-card: rgba(255,255,255,0.03);
    --bg-card-hover: rgba(255,255,255,0.06);
    --accent-purple: #a855f7;
    --accent-cyan: #06b6d4;
    --accent-pink: #ec4899;
    --accent-emerald: #10b981;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border-subtle: rgba(255,255,255,0.06);
    --glow-purple: 0 0 30px rgba(168,85,247,0.15);
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: var(--bg-primary);
    background-image:
        radial-gradient(ellipse 80% 60% at 10% 0%, rgba(168,85,247,0.08) 0%, transparent 50%),
        radial-gradient(ellipse 60% 50% at 90% 100%, rgba(6,182,212,0.06) 0%, transparent 50%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,15,25,0.95) 0%, rgba(10,10,18,0.98) 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
section[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--text-muted) !important;
    margin-top: 1.5rem;
}

/* Hero */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1rem;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(168,85,247,0.15), rgba(6,182,212,0.15));
    border: 1px solid rgba(168,85,247,0.25);
    border-radius: 50px;
    padding: 6px 18px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--accent-purple);
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f1f5f9 0%, #a855f7 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-sub {
    color: var(--text-secondary);
    font-size: 1rem;
    font-weight: 300;
    max-width: 600px;
    margin: 0 auto;
}

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 2rem 0 1rem;
}
.section-header .icon { font-size: 1.3rem; }
.section-header .label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-primary);
}
.section-header .line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border-subtle), transparent);
}

/* Movie Cards */
.movie-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 0;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}
.movie-poster {
    width: 100%;
    height: 240px;
    object-fit: cover;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    transition: transform 0.6s ease;
}
.movie-card:hover .movie-poster {
    transform: scale(1.08);
}
.movie-poster-wrap {
    overflow: hidden;
    position: relative;
}
.movie-poster-wrap::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 80px;
    background: linear-gradient(transparent, var(--bg-primary));
    pointer-events: none;
}
.movie-card:hover {
    transform: translateY(-8px);
    border-color: rgba(168, 85, 247, 0.4);
    box-shadow: 0 10px 40px rgba(168, 85, 247, 0.2), 0 0 15px rgba(6, 182, 212, 0.2);
    background: rgba(255, 255, 255, 0.05);
}
.movie-card-inner { padding: 22px; flex-grow: 1; display: flex; flex-direction: column; }
.movie-rank {
    position: absolute;
    top: 14px;
    right: 14px;
    width: 34px;
    height: 34px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 800;
    color: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    z-index: 10;
}
.movie-title-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    background: linear-gradient(90deg, #fff, #cbd5e1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
    line-height: 1.3;
    min-height: 2.6rem;
}
.movie-genres { 
    display: flex; 
    flex-wrap: wrap; 
    gap: 6px; 
    margin-bottom: 20px; 
    min-height: 24px;
}
.genre-chip {
    background: linear-gradient(135deg, rgba(168,85,247,0.1), rgba(6,182,212,0.1));
    border: 1px solid rgba(168,85,247,0.3);
    color: #e2e8f0;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    box-shadow: inset 0 1px 3px rgba(255,255,255,0.05);
}
.score-bar-container {
    background: rgba(0,0,0,0.2);
    border-radius: 12px;
    padding: 14px;
    border: 1px solid rgba(255,255,255,0.03);
    margin-top: auto;
}
.score-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}
.score-label { font-size: 0.65rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.score-value { font-size: 0.9rem; font-weight: 800; }
.score-value.hybrid { color: #34d399; text-shadow: 0 0 10px rgba(52,211,153,0.3); }
.score-value.cb { color: var(--accent-purple); }
.score-value.cf { color: var(--accent-cyan); }
.score-track {
    width: 100%;
    height: 6px;
    background: rgba(255,255,255,0.05);
    border-radius: 6px;
    overflow: hidden;
    margin-top: 4px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);
}
.score-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}
.score-fill.hybrid { background: linear-gradient(90deg, #10b981, #34d399); box-shadow: 0 0 10px rgba(52,211,153,0.5); }
.score-fill.cb { background: linear-gradient(90deg, #7c3aed, #a855f7); }
.score-fill.cf { background: linear-gradient(90deg, #0891b2, #06b6d4); }

/* History */
.history-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 0;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(8px);
    overflow: hidden;
}
.history-item:hover {
    border-color: rgba(236,72,153,0.4);
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(236,72,153,0.15);
}
.history-title {
    color: var(--text-primary);
    font-weight: 700;
    font-size: 0.85rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 8px;
    padding: 0 10px;
}
.history-stars { color: #fbbf24; font-size: 0.75rem; letter-spacing: 2px; padding-bottom: 12px; }


/* Metric cards */
.metric-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 1rem 0; }
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover { border-color: rgba(168,85,247,0.25); background: var(--bg-card-hover); }
.metric-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text-muted);
    font-weight: 600;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
}
.metric-value.green { color: var(--accent-emerald); }
.metric-value.purple { color: var(--accent-purple); }
.metric-value.cyan { color: var(--accent-cyan); }
.metric-value.pink { color: var(--accent-pink); }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-purple), #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.3px;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(168,85,247,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(168,85,247,0.35) !important;
}

/* Hide default streamlit */
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stMetric"] { display: none; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    color: var(--text-secondary) !important;
    padding: 8px 20px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(168,85,247,0.15), rgba(6,182,212,0.15)) !important;
    border-color: rgba(168,85,247,0.3) !important;
    color: var(--accent-purple) !important;
}

/* Plotly charts */
.js-plotly-plot .plotly .modebar { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─── LOAD DATA & MODELS ───
@st.cache_resource(show_spinner=False)
def initialize_system():
    with st.spinner("⏳ Training recommendation models..."):
        ratings, movies, users = load_all()
        cb = ContentBasedFilter(movies)
        cf = CollaborativeFilter(ratings, n_factors=50)
        cf.train()
        metrics = full_evaluation(cf)
        return ratings, movies, users, cb, cf, metrics

try:
    ratings_df, movies_df, users_df, cb_model, cf_model, eval_metrics = initialize_system()
except Exception as e:
    st.error(f"⚠️ Failed to initialize: {e}")
    st.stop()


# ─── SIDEBAR ───
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0 0.5rem;">
        <div style="font-size:2.5rem;">🎬</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:800;
            background:linear-gradient(135deg,#a855f7,#06b6d4);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;">CineMatch AI</div>
        <div style="color:#64748b; font-size:0.7rem; letter-spacing:1px; text-transform:uppercase; margin-top:4px;">Hybrid Engine v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👤 User Profile")
    user_list = sorted(users_df['user_id'].unique())
    selected_user = st.selectbox("Select User", user_list, index=0, label_visibility="collapsed")

    user_history = ratings_df[ratings_df['user_id'] == selected_user]
    total_rated = len(user_history)
    avg_rating = user_history['rating'].mean()
    fav_movies = user_history[user_history['rating'] >= 4]

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
        border-radius:12px; padding:14px; margin:0.5rem 0;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#64748b; font-size:0.75rem;">Movies Rated</span>
            <span style="color:#f1f5f9; font-weight:700;">{total_rated}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#64748b; font-size:0.75rem;">Avg Rating</span>
            <span style="color:#fbbf24; font-weight:700;">{'⭐' * int(round(avg_rating))} {avg_rating:.1f}</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#64748b; font-size:0.75rem;">Loved Movies</span>
            <span style="color:#ec4899; font-weight:700;">{len(fav_movies)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎛️ Engine Tuning")
    cb_weight = st.slider("Content-Based Weight", 0.0, 1.0, 0.4, 0.05)
    cf_weight = round(1.0 - cb_weight, 2)
    st.caption(f"Collaborative Weight: **{cf_weight}**")

    top_n = st.slider("Recommendations", 5, 20, 10)

    st.markdown("### 📊 Model Stats")
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.15);
            border-radius:10px; padding:10px; text-align:center;">
            <div style="color:#64748b; font-size:0.6rem; text-transform:uppercase; letter-spacing:1px;">RMSE</div>
            <div style="color:#10b981; font-size:1.1rem; font-weight:800; font-family:'Space Grotesk';">{eval_metrics['RMSE']:.3f}</div>
        </div>
        <div style="background:rgba(6,182,212,0.08); border:1px solid rgba(6,182,212,0.15);
            border-radius:10px; padding:10px; text-align:center;">
            <div style="color:#64748b; font-size:0.6rem; text-transform:uppercase; letter-spacing:1px;">MAE</div>
            <div style="color:#06b6d4; font-size:1.1rem; font-weight:800; font-family:'Space Grotesk';">{eval_metrics['MAE']:.3f}</div>
        </div>
        <div style="background:rgba(168,85,247,0.08); border:1px solid rgba(168,85,247,0.15);
            border-radius:10px; padding:10px; text-align:center;">
            <div style="color:#64748b; font-size:0.6rem; text-transform:uppercase; letter-spacing:1px;">F1</div>
            <div style="color:#a855f7; font-size:1.1rem; font-weight:800; font-family:'Space Grotesk';">{eval_metrics['F1-Score']:.3f}</div>
        </div>
        <div style="background:rgba(236,72,153,0.08); border:1px solid rgba(236,72,153,0.15);
            border-radius:10px; padding:10px; text-align:center;">
            <div style="color:#64748b; font-size:0.6rem; text-transform:uppercase; letter-spacing:1px;">Precision</div>
            <div style="color:#ec4899; font-size:1.1rem; font-weight:800; font-family:'Space Grotesk';">{eval_metrics['Precision']:.3f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── HERO ───
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">✦ AI-Powered Hybrid Engine</div>
    <div class="hero-title">Discover Your Next<br>Favorite Movie</div>
    <div class="hero-sub">Combining collaborative intelligence with content analysis to surface films you'll genuinely love.</div>
</div>
""", unsafe_allow_html=True)


# ─── GENERATE ───
col_btn = st.columns([1, 2, 1])
with col_btn[1]:
    generate = st.button("🚀  Generate Recommendations", width="stretch")

if generate:
    progress = st.progress(0, text="Analyzing your taste profile...")
    time.sleep(0.4)
    progress.progress(30, text="Running Content-Based engine...")
    time.sleep(0.3)
    progress.progress(60, text="Running Collaborative engine...")
    time.sleep(0.3)
    progress.progress(85, text="Merging hybrid scores...")

    hybrid = HybridRecommender(cb_model, cf_model, cb_weight=cb_weight, cf_weight=cf_weight)
    recs = hybrid.recommend(selected_user, ratings_df, movies_df, top_n=top_n)

    progress.progress(100, text="Done!")
    time.sleep(0.3)
    progress.empty()

    if recs.empty:
        st.warning("Not enough data to generate recommendations for this user.")
    else:
        # Section header
        st.markdown("""
        <div class="section-header">
            <span class="icon">🎯</span>
            <span class="label">Top Picks For You</span>
            <div class="line"></div>
        </div>
        """, unsafe_allow_html=True)

        # Render movie cards in a 3-column grid
        cols = st.columns(3)
        for idx, row in recs.iterrows():
            col = cols[idx % 3]
            genres_str = str(row.get("genres",""))
            genres_html = "".join([f'<span class="genre-chip">{g}</span>' for g in genres_str.split()[:4]])
            hs = row.get("hybrid_score", 0)
            cb_s = row.get("cb_norm", 0)
            cf_s = row.get("cf_norm", 0)
            poster = get_poster_url(row.get('tmdb_id', 0), title=row.get('title'))
            col.markdown(f"""
            <div class="movie-card">
                <div class="movie-rank">#{idx + 1}</div>
                <div class="movie-poster-wrap">
                    <img class="movie-poster" src="{poster}" alt="{row.get('title','Unknown')}" loading="lazy">
                </div>
                <div class="movie-card-inner">
                    <div class="movie-title-text">{row.get('title','Unknown')}</div>
                    <div class="movie-genres">{genres_html}</div>
                    <div class="score-bar-container">
                        <div class="score-row">
                            <span class="score-label">Hybrid</span>
                            <span class="score-value hybrid">{hs:.2f}</span>
                        </div>
                        <div class="score-track"><div class="score-fill hybrid" style="width:{hs*100:.0f}%"></div></div>
                        <div style="display:flex; gap:16px; margin-top:8px;">
                            <div style="flex:1;">
                                <div class="score-row">
                                    <span class="score-label">CB</span>
                                    <span class="score-value cb">{cb_s:.2f}</span>
                                </div>
                                <div class="score-track"><div class="score-fill cb" style="width:{cb_s*100:.0f}%"></div></div>
                            </div>
                            <div style="flex:1;">
                                <div class="score-row">
                                    <span class="score-label">CF</span>
                                    <span class="score-value cf">{cf_s:.2f}</span>
                                </div>
                                <div class="score-track"><div class="score-fill cf" style="width:{cf_s*100:.0f}%"></div></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ─── ANALYTICS TAB SECTION ───
        st.markdown("""
        <div class="section-header" style="margin-top:2.5rem;">
            <span class="icon">📈</span>
            <span class="label">Recommendation Analytics</span>
            <div class="line"></div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["📊 Score Distribution", "🎭 Genre Breakdown"])

        with tab1:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=recs['title'].str[:25], y=recs['hybrid_score'],
                marker=dict(color=recs['hybrid_score'],
                    colorscale=[[0,'#7c3aed'],[0.5,'#06b6d4'],[1,'#10b981']]),
                text=recs['hybrid_score'].round(2), textposition='outside',
                textfont=dict(color='#94a3b8', size=11)
            ))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8', family='Inter'),
                xaxis=dict(tickangle=-35, showgrid=False, color='#64748b'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', color='#64748b'),
                margin=dict(l=20, r=20, t=30, b=80), height=400,
            )
            st.plotly_chart(fig, width="stretch", key="score_chart")

        with tab2:
            all_genres = []
            for g in recs['genres'].dropna():
                all_genres.extend(str(g).split())
            genre_counts = pd.Series(all_genres).value_counts().head(10)
            fig2 = go.Figure(go.Bar(
                x=genre_counts.values, y=genre_counts.index, orientation='h',
                marker=dict(color=genre_counts.values,
                    colorscale=[[0,'#ec4899'],[0.5,'#a855f7'],[1,'#06b6d4']]),
            ))
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8', family='Inter'),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', color='#64748b'),
                yaxis=dict(showgrid=False, color='#94a3b8', autorange='reversed'),
                margin=dict(l=20, r=20, t=20, b=20), height=350,
            )
            st.plotly_chart(fig2, width="stretch", key="genre_chart")


# ─── WATCH HISTORY ───
st.markdown("""
<div class="section-header" style="margin-top:2rem;">
    <span class="icon">📜</span>
    <span class="label">Recent Watch History</span>
    <div class="line"></div>
</div>
""", unsafe_allow_html=True)

history = ratings_df[ratings_df['user_id'] == selected_user].merge(movies_df, on='movie_id')
history = history.sort_values('rating', ascending=False).head(10)

hist_cols = st.columns(5)
for i, (_, row) in enumerate(history.iterrows()):
    with hist_cols[i % 5]:
        stars = '⭐' * int(row['rating'])
        h_poster = get_poster_url(row.get('tmdb_id', 0), title=row.get('title'))
        st.markdown(f"""
        <div class="history-item" style="padding:0; overflow:hidden;">
            <img src="{h_poster}" style="width:100%; height:140px; object-fit:cover; border-radius:12px 12px 0 0;" loading="lazy">
            <div style="padding:10px;">
                <div class="history-title" title="{row['title']}">{row['title']}</div>
                <div class="history-stars">{stars}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── EVALUATION METRICS ───
st.markdown("""
<div class="section-header" style="margin-top:2rem;">
    <span class="icon">🏆</span>
    <span class="label">Model Performance</span>
    <div class="line"></div>
</div>
""", unsafe_allow_html=True)

colors = ['green','cyan','purple','pink','green']
labels = list(eval_metrics.keys())
values = list(eval_metrics.values())
color_map = {'RMSE':'green','MAE':'cyan','Precision':'purple','Recall':'pink','F1-Score':'green'}

metrics_html = '<div class="metric-grid">'
for lbl, val in eval_metrics.items():
    c = color_map.get(lbl, 'green')
    metrics_html += f'''
    <div class="metric-card">
        <div class="metric-label">{lbl}</div>
        <div class="metric-value {c}">{val:.4f}</div>
    </div>'''
metrics_html += '</div>'
st.markdown(metrics_html, unsafe_allow_html=True)


# ─── FOOTER ───
st.markdown("""
<div style="text-align:center; padding:3rem 0 2rem; border-top:1px solid rgba(255,255,255,0.04); margin-top:3rem;">
    <div style="color:#64748b; font-size:0.75rem; letter-spacing:0.5px;">
        Built with ❤️ using <strong style="color:#a855f7;">Content-Based</strong> + <strong style="color:#06b6d4;">Collaborative</strong> Filtering
    </div>
    <div style="color:#475569; font-size:0.65rem; margin-top:4px;">CineMatch AI • Hybrid Recommendation Engine • MovieLens Dataset</div>
</div>
""", unsafe_allow_html=True)
