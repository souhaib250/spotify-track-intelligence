import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Spotify Analytics", layout="wide", initial_sidebar_state="collapsed")

if "page" not in st.session_state:
    st.session_state.page = "Overview"

BG      = "#0F0C1B"
CARD    = "rgba(255,255,255,0.05)"
CARD2   = "rgba(255,255,255,0.09)"
BORDER  = "rgba(255,255,255,0.10)"
TEXT    = "#FDFBF7"
SUB     = "#B8B0D3"
ACCENT  = "#A78BFA"
ACCENT2 = "#8B5CF6"
GREEN   = "#1DB954"
GRID    = "rgba(255,255,255,0.04)"
HOVER_C = "#1A1530"
PLOT_BG = "rgba(0,0,0,0)"

MOOD_COLORS = {
    "High Energy":    "#F472B6",
    "Chill Vibes":    "#60A5FA",
    "Acoustic Mood":  "#34D399",
    "Dark / Intense": "#A78BFA",
}

GENRE_MAP = {"Hip-Hop": "hip-hop", "Electronic": "electronic", "Pop": "pop", "Indie": "indie", "R&B": "r&b"}
PAGES = ["Overview", "Hip-Hop", "Electronic", "Pop", "Indie", "R&B"]

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">'

CSS = (
"html,body,[data-testid='stAppViewContainer'],[data-testid='stMain']{"
f"background:{BG}!important;font-family:'Plus Jakarta Sans',sans-serif!important;color:{TEXT}!important;}}"
"[data-testid='stHeader'],section[data-testid='stSidebar']{display:none!important;}"
"[data-testid='stMainBlockContainer']{padding:2rem 2.5rem 3rem!important;max-width:1400px!important;}"
"[data-testid='stRadio']>label{display:none!important;}"
"[data-testid='stRadio']>div{"
"display:flex!important;flex-direction:row!important;gap:6px!important;"
"background:rgba(255,255,255,0.04)!important;border:1px solid rgba(255,255,255,0.08)!important;"
"border-radius:999px!important;padding:5px!important;width:fit-content!important;}"
"[data-testid='stRadio'] label{margin:0!important;padding:7px 18px!important;"
"border-radius:999px!important;cursor:pointer!important;border:1px solid transparent!important;"
"transition:all .2s ease!important;}"
"[data-testid='stRadio'] label>div:first-child{display:none!important;}"
f"[data-testid='stRadio'] label p{{font-family:'Plus Jakarta Sans',sans-serif!important;"
f"font-size:.82rem!important;font-weight:500!important;color:{SUB}!important;margin:0!important;}}"
f"[data-testid='stRadio'] label:hover{{background:rgba(167,139,250,.12)!important;}}"
f"[data-testid='stRadio'] label:hover p{{color:{TEXT}!important;}}"
"[data-testid='stRadio'] label:has(input:checked){"
f"background:rgba(167,139,250,.18)!important;border-color:rgba(167,139,250,.4)!important;}}"
f"[data-testid='stRadio'] label:has(input:checked) p{{color:{ACCENT}!important;font-weight:700!important;}}"
"[data-testid='stButton']>button{"
f"background:rgba(255,255,255,0.05)!important;color:{SUB}!important;"
"border:1px solid rgba(255,255,255,0.1)!important;border-radius:999px!important;"
"font-family:'Plus Jakarta Sans',sans-serif!important;font-size:.8rem!important;"
"font-weight:500!important;padding:.4rem 1.2rem!important;transition:all .2s ease!important;}"
f"[data-testid='stButton']>button:hover{{border-color:{ACCENT}!important;color:{ACCENT}!important;}}"
"div[data-testid='stMetric']{"
"background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.09)!important;"
"border-radius:16px!important;padding:1.1rem 1.3rem!important;"
"transition:transform .2s,border-color .2s,box-shadow .2s;}"
f"div[data-testid='stMetric']:hover{{transform:translateY(-3px);border-color:rgba(167,139,250,.35)!important;"
"box-shadow:0 8px 24px rgba(139,92,246,.12)!important;}"
f"div[data-testid='stMetricLabel']>div{{color:{SUB}!important;font-size:.72rem!important;"
"font-weight:600!important;text-transform:uppercase!important;letter-spacing:.08em!important;"
"font-family:'Plus Jakarta Sans',sans-serif!important;}"
f"div[data-testid='stMetricValue']>div{{color:{TEXT}!important;font-size:1.55rem!important;"
"font-weight:800!important;font-family:'Plus Jakarta Sans',sans-serif!important;}"
f"div[data-testid='stMetricDelta']>div{{font-size:.74rem!important;color:{SUB}!important;}}"
"div[data-testid='stDataFrame']{background:rgba(255,255,255,0.04)!important;"
"border:1px solid rgba(255,255,255,0.09)!important;border-radius:14px!important;overflow:hidden!important;}"
".sh{display:flex;justify-content:space-between;align-items:baseline;"
"margin:1.5rem 0 .6rem;}"
f".st2{{font-size:.95rem;font-weight:700;color:{TEXT};letter-spacing:-.01em;}}"
f".sm{{font-size:.72rem;font-weight:500;color:{SUB};}}"
)

st.markdown(FONTS + f"<style>{CSS}</style>", unsafe_allow_html=True)


@st.cache_data
def load():
    return pd.read_csv("data/tracks_clustered.csv")

@st.cache_data
def load_meta():
    try:
        return json.load(open("data/model_meta.json"))
    except Exception:
        return {"r2": "N/A", "mae": "N/A"}

df = load()
meta = load_meta()
last_synced = str(df["last_synced"].iloc[0])[:10] if "last_synced" in df.columns else "N/A"


def fig_style(fig):
    fig.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="Plus Jakarta Sans", color=TEXT, size=12),
        margin=dict(l=4, r=4, t=28, b=4),
        hoverlabel=dict(bgcolor="#1A1530", bordercolor="rgba(167,139,250,.3)",
                        font=dict(family="Plus Jakarta Sans", color=TEXT, size=12)),
        legend=dict(font=dict(size=11, color=SUB), bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(color=SUB, size=11), title_font=dict(color=SUB))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, tickfont=dict(color=SUB, size=11), title_font=dict(color=SUB))
    return fig


def scatter_fig(data):
    fig = px.scatter(
        data, x="energy", y="popularity", color="mood",
        hover_data={"track_name": True, "artist_name": True, "tempo": ":.0f", "energy": ":.2f"},
        color_discrete_map=MOOD_COLORS, opacity=0.85,
        labels={"energy": "Energy", "popularity": "Popularity", "mood": "Mood"},
    )
    fig.update_traces(marker=dict(size=10, line=dict(width=1.5, color="rgba(15,12,27,0.6)")))
    return fig_style(fig)


def donut_fig(data):
    counts = data["mood"].value_counts()
    colors = [MOOD_COLORS.get(m, ACCENT) for m in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.62,
        marker=dict(colors=colors, line=dict(color=BG, width=3)),
        textinfo="percent",
        textfont=dict(family="Plus Jakarta Sans", size=12, color=TEXT),
        hovertemplate="<b>%{label}</b><br>%{value} tracks (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=PLOT_BG, font=dict(family="Plus Jakarta Sans", color=TEXT),
        margin=dict(l=4, r=4, t=20, b=4),
        legend=dict(font=dict(size=11, color=SUB), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#1A1530", bordercolor="rgba(167,139,250,.3)",
                        font=dict(family="Plus Jakarta Sans", color=TEXT)),
    )
    return fig


def bar_fig(data, x, y, color=None):
    c = color or ACCENT2
    fig = px.bar(data, x=x, y=y, color_discrete_sequence=[c],
                 labels={x: x.replace("_", " ").title(), y: y.replace("_", " ").title()})
    fig.update_traces(
        marker_line_width=0,
        marker_cornerradius=6,
        marker_color=c,
        marker_opacity=0.85,
    )
    return fig_style(fig)


def section(title, meta_label=""):
    left = f'<span class="st2">{title}</span>'
    right = f'<span class="sm">{meta_label}</span>' if meta_label else ""
    st.markdown(f'<div class="sh">{left}{right}</div>', unsafe_allow_html=True)


col_a, col_b, col_c = st.columns([2, 5.5, 1.5], vertical_alignment="center")
with col_a:
    dot = f'<span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:{GREEN};box-shadow:0 0 10px {GREEN};margin-right:8px;vertical-align:middle;"></span>'
    name = f'<span style="font-size:.95rem;font-weight:800;color:{TEXT};letter-spacing:-.02em;">Spotify Analytics</span>'
    st.markdown(dot + name, unsafe_allow_html=True)

with col_b:
    nav = st.radio("nav", PAGES, index=PAGES.index(st.session_state.page),
                   horizontal=True, label_visibility="collapsed")
    if nav != st.session_state.page:
        st.session_state.page = nav
        st.rerun()

with col_c:
    st.write("")

st.markdown(f'<hr style="border:none;border-top:1px solid {BORDER};margin:.75rem 0 1.5rem;">', unsafe_allow_html=True)


if st.session_state.page == "Overview":
    r2_val = meta["r2"]
    r2_pct = f"{float(r2_val)*100:.1f}%" if isinstance(r2_val, (int, float)) else "N/A"
    top_artist = df.groupby("artist_name")["popularity"].mean().idxmax()
    n_tracks = len(df)
    n_genres = df["genre"].nunique()
    n_artists = df["artist_name"].nunique()

    pills = ""
    for label, val in [
        (f"{n_tracks} Tracks", ACCENT),
        (f"{n_genres} Genres", "#60A5FA"),
        (f"{n_artists} Artists", "#F472B6"),
        (f"R² {r2_val}", "#34D399"),
        (f"Synced {last_synced}", SUB),
    ]:
        pills += (
            f'<span style="display:inline-flex;align-items:center;gap:5px;'
            f'background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);'
            f'border-radius:999px;padding:5px 14px;font-size:.8rem;font-weight:600;color:{val};">'
            f'{label}</span>'
        )

    hero = (
        f'<div style="background:linear-gradient(135deg,#2D1B69 0%,#1E1040 40%,#0F0C1B 100%);'
        f'border:1px solid rgba(167,139,250,.2);border-radius:20px;padding:2.5rem 2.5rem 2rem;'
        f'margin-bottom:1.5rem;position:relative;overflow:hidden;">'
        f'<div style="position:absolute;top:-60px;right:-60px;width:280px;height:280px;'
        f'background:radial-gradient(circle,rgba(167,139,250,.18) 0%,transparent 70%);'
        f'border-radius:50%;pointer-events:none;"></div>'
        f'<div style="position:absolute;bottom:-80px;left:30%;width:320px;height:320px;'
        f'background:radial-gradient(circle,rgba(29,185,84,.08) 0%,transparent 70%);'
        f'border-radius:50%;pointer-events:none;"></div>'
        f'<p style="font-size:.78rem;font-weight:600;color:{GREEN};text-transform:uppercase;'
        f'letter-spacing:.12em;margin:0 0 .6rem;">Track & Mood Intelligence</p>'
        f'<h1 style="font-size:2rem;font-weight:800;color:{TEXT};margin:0 0 .5rem;'
        f'letter-spacing:-.03em;line-height:1.15;">Your Music, Decoded.</h1>'
        f'<p style="font-size:.9rem;color:{SUB};margin:0 0 1.5rem;max-width:520px;">'
        f'ETL pipeline · SQLite analytics · K-Means mood clustering · RandomForest prediction</p>'
        f'<div style="display:flex;flex-wrap:wrap;gap:8px;">{pills}</div>'
        f'</div>'
    )
    st.markdown(hero, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tracks", str(n_tracks), f"{n_artists} artists")
    c2.metric("Avg Popularity", f"{df['popularity'].mean():.1f}", f"Top: {top_artist}")
    c3.metric("RF Model R²", str(r2_val), f"MAE {meta['mae']}")
    c4.metric("Mood Clusters", str(df["mood"].nunique()), "K-Means k=4")

    cl, cr = st.columns([1.4, 1], gap="medium")
    with cl:
        section("Avg Popularity by Genre", "SQL GROUP BY")
        g_avg = df.groupby("genre", as_index=False)["popularity"].mean().sort_values("popularity", ascending=False)
        st.plotly_chart(bar_fig(g_avg, "genre", "popularity"), use_container_width=True)
    with cr:
        section("Mood Distribution", "K-Means k=4")
        st.plotly_chart(donut_fig(df), use_container_width=True)

    section("Energy vs Popularity", "All Tracks")
    st.plotly_chart(scatter_fig(df), use_container_width=True)

    section("Top 10 Tracks", "Ranked by Popularity")
    top10 = df.nlargest(10, "popularity")[
        ["track_name", "artist_name", "genre", "mood", "popularity", "energy", "danceability", "release_date"]
    ].reset_index(drop=True)
    top10.columns = ["Track", "Artist", "Genre", "Mood", "Popularity", "Energy", "Danceability", "Release"]
    st.dataframe(top10, use_container_width=True, hide_index=True)

else:
    gkey = GENRE_MAP[st.session_state.page]
    gdf = df[df["genre"] == gkey].copy()

    baseline = df["popularity"].mean()
    gavg = gdf["popularity"].mean()
    delta = gavg - baseline
    top_a = gdf.groupby("artist_name")["popularity"].mean().idxmax() if len(gdf) > 0 else "N/A"
    top_t = gdf.nlargest(1, "popularity")["track_name"].iloc[0] if len(gdf) > 0 else "N/A"
    top_pop = int(gdf["popularity"].max()) if len(gdf) > 0 else 0
    top_t_short = top_t[:22] + "…" if len(top_t) > 22 else top_t

    page_hero = (
        f'<div style="background:linear-gradient(135deg,#2D1B69 0%,#1E1040 60%,#0F0C1B 100%);'
        f'border:1px solid rgba(167,139,250,.2);border-radius:20px;'
        f'padding:1.75rem 2.5rem;margin-bottom:1.5rem;">'
        f'<p style="font-size:.72rem;font-weight:600;color:{GREEN};text-transform:uppercase;'
        f'letter-spacing:.12em;margin:0 0 .4rem;">Genre Deep Dive</p>'
        f'<h2 style="font-size:1.6rem;font-weight:800;color:{TEXT};margin:0;letter-spacing:-.02em;">'
        f'{st.session_state.page}</h2>'
        f'</div>'
    )
    st.markdown(page_hero, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{st.session_state.page} Tracks", str(len(gdf)), f"{gdf['artist_name'].nunique()} artists")
    c2.metric("Avg Popularity", f"{gavg:.1f}", f"{delta:+.1f} vs catalog")
    c3.metric("Top Artist", top_a, "Highest mean")
    c4.metric("Peak Track", str(top_pop), top_t_short)

    r1, r2 = st.columns([1.5, 1], gap="medium")
    with r1:
        section(f"Top {st.session_state.page} Tracks", f"{len(gdf)} Tracks")
        tbl = gdf.nlargest(10, "popularity")[
            ["track_name", "artist_name", "mood", "popularity", "energy", "danceability", "release_date"]
        ].reset_index(drop=True)
        tbl.columns = ["Track", "Artist", "Mood", "Popularity", "Energy", "Danceability", "Release"]
        st.dataframe(tbl, use_container_width=True, hide_index=True)
    with r2:
        section("Mood Breakdown", "Cluster share")
        st.plotly_chart(donut_fig(gdf), use_container_width=True)

    r3, r4 = st.columns([1.3, 1], gap="medium")
    with r3:
        section("Energy vs Popularity", "Audio features")
        st.plotly_chart(scatter_fig(gdf), use_container_width=True)
    with r4:
        section("Popularity by Artist", "Mean score")
        a_avg = gdf.groupby("artist_name", as_index=False)["popularity"].mean().sort_values("popularity", ascending=False)
        st.plotly_chart(bar_fig(a_avg, "artist_name", "popularity", "#60A5FA"), use_container_width=True)
