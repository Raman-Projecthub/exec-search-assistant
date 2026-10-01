import os
import io
import csv
from datetime import datetime, date, timedelta

import streamlit as st
import pandas as pd
from tavily import TavilyClient

client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

st.set_page_config(page_title="Executive & Event Search Assistant", page_icon="🔎", layout="wide")

# ============================================================
# GLOBAL STYLE SYSTEM
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-deep: #070B14;
    --bg-mid: #0B1020;
    --bg-card: #101729;
    --glass-bg: rgba(255,255,255,0.03);
    --glass-border: rgba(255,255,255,0.08);
    --text-primary: #F2F4F8;
    --text-secondary: #8B93A7;
    --accent-blue: #3B82F6;
    --accent-indigo: #6366F1;
    --accent-violet: #8B5CF6;
    --accent-cyan: #22D3EE;
    --accent-pink: #EC4899;
    --accent-green: #22C55E;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 85% 0%, rgba(99,102,241,0.18) 0%, transparent 45%),
        radial-gradient(circle at 10% 35%, rgba(139,92,246,0.14) 0%, transparent 45%),
        radial-gradient(circle at 50% 85%, rgba(34,211,238,0.08) 0%, transparent 50%),
        var(--bg-deep);
    color: var(--text-primary);
}

.block-container { max-width: 1300px; padding-top: 2rem; padding-bottom: 3rem; }

/* ---------- Hero ---------- */
.hero-title {
    font-size: 44px;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 6px;
}
.hero-title .grad {
    background: linear-gradient(90deg, #8B5CF6, #3B82F6, #22D3EE);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.hero-sub { color: var(--text-secondary); font-size: 16px; max-width: 560px; margin-bottom: 18px; }

.pill-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.pill {
    display: flex; align-items: center; gap: 10px;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    padding: 10px 16px;
    backdrop-filter: blur(16px);
    transition: all .25s ease;
}
.pill:hover { border-color: rgba(139,92,246,0.5); box-shadow: 0 0 20px rgba(99,102,241,0.25); transform: translateY(-2px); }
.pill-icon { font-size: 18px; }
.pill-title { font-weight: 600; font-size: 13px; color: var(--text-primary); }
.pill-desc { font-size: 11px; color: var(--text-secondary); }

/* ---------- Glass card wrapper for the form ---------- */
div[data-testid="stForm"] {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 32px;
    backdrop-filter: blur(20px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.35);
}

.search-heading { display:flex; align-items:center; gap:10px; font-size:20px; font-weight:700; margin-bottom: 18px; }

/* ---------- Inputs ---------- */
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 14px !important;
    color: var(--text-primary) !important;
    padding: 10px 14px !important;
    transition: all .2s ease;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.25) !important;
}
label { color: var(--text-secondary) !important; font-size: 13px !important; font-weight: 600 !important; }

/* ---------- Date range input ---------- */
div[data-testid="stDateInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 14px !important;
    color: var(--text-primary) !important;
    padding: 10px 14px !important;
}
div[data-testid="stDateInput"] input:focus {
    border-color: var(--accent-indigo) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.25) !important;
}

/* ---------- Slider ---------- */
div[data-testid="stSlider"] div[role="slider"] {
    background: linear-gradient(90deg, #8B5CF6, #22D3EE) !important;
    box-shadow: 0 0 12px rgba(139,92,246,0.7);
}
div[data-testid="stSlider"] .st-emotion-cache-1y4p8pa,
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
    background: linear-gradient(90deg, #8B5CF6, #3B82F6, #22D3EE) !important;
}

/* ---------- Primary CTA ---------- */
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(90deg, #8B5CF6, #3B82F6, #22D3EE) !important;
    border: none !important;
    border-radius: 14px !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 14px 0 !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.4);
    transition: all .2s ease;
}
div[data-testid="stFormSubmitButton"] button:hover {
    filter: brightness(1.12);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(99,102,241,0.55);
}
div[data-testid="stFormSubmitButton"] button:active { transform: translateY(0px); }

/* ---------- Download button ---------- */
div[data-testid="stDownloadButton"] button {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}
div[data-testid="stDownloadButton"] button:hover { border-color: var(--accent-cyan) !important; }

/* ---------- Status row ---------- */
.status-row { display:flex; align-items:center; justify-content:space-between; margin: 28px 0 14px 0; flex-wrap: wrap; gap: 10px; }
.status-left { display:flex; align-items:center; gap:10px; }
.status-icon { font-size: 20px; }
.status-title { font-weight:700; font-size:18px; }
.status-sub { color: var(--text-secondary); font-size: 13px; }
.live-pill {
    display:inline-flex; align-items:center; gap:6px;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.4);
    color: var(--accent-green);
    border-radius: 999px; padding: 6px 14px; font-size: 12px; font-weight: 600;
}
.live-dot { width:7px; height:7px; border-radius:50%; background: var(--accent-green); box-shadow: 0 0 8px var(--accent-green); animation: pulse 1.6s infinite; }
@keyframes pulse { 0%{opacity:1;} 50%{opacity:0.4;} 100%{opacity:1;} }
.count-badge { color: var(--text-secondary); font-size: 13px; }

/* ---------- Dashboard card (timeline wrapper) ---------- */
.dash-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 24px 24px 8px 24px;
    backdrop-filter: blur(16px);
    margin-bottom: 24px;
}
.dash-card-title { font-weight: 700; font-size: 17px; display:flex; align-items:center; gap:8px; }
.dash-card-sub { color: var(--text-secondary); font-size: 13px; margin-bottom: 14px; }

/* ---------- Result cards ---------- */
.result-card {
    border: 1px solid var(--glass-border);
    background: var(--glass-bg);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 12px;
    backdrop-filter: blur(14px);
    transition: all .2s ease;
    animation: fadein .4s ease;
}
.result-card:hover {
    transform: translateY(-2px);
    border-color: rgba(139,92,246,0.45);
    box-shadow: 0 8px 28px rgba(99,102,241,0.18);
}
@keyframes fadein { from { opacity:0; transform: translateY(6px);} to { opacity:1; transform: translateY(0);} }
.badge-news {
    display:inline-block; background: rgba(59,130,246,0.15); color:#93C5FD;
    font-size: 10px; font-weight: 700; letter-spacing: .5px;
    border-radius: 6px; padding: 3px 8px; margin-right: 8px;
}
.result-meta { color: var(--text-secondary); font-size: 12px; margin-bottom: 6px; }
.result-card a.result-title {
    text-decoration: none; color: var(--text-primary);
    font-size: 16px; font-weight: 600; line-height: 1.4; display:block; margin-bottom: 4px;
}
.result-card a.result-title:hover { color: var(--accent-cyan); }
.result-source { color: var(--text-secondary); font-size: 12px; }

/* ---------- Empty state ---------- */
.empty-state {
    text-align:center; padding: 60px 20px;
    background: var(--glass-bg);
    border: 1px dashed var(--glass-border);
    border-radius: 20px;
    margin-top: 20px;
}
.empty-icon { font-size: 36px; margin-bottom: 12px; }
.empty-title { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.empty-sub { color: var(--text-secondary); font-size: 14px; }

/* ---------- Error box ---------- */
div[data-testid="stAlert"] {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.35) !important;
    border-radius: 14px !important;
}

@media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
}

@media (max-width: 768px) {
    .hero-title { font-size: 30px; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero-title">🔎 <span class="grad">Executive &amp; Event</span><br>Search Assistant</div>
<div class="hero-sub">Real-time intelligence on company leadership, events, news, and developments.</div>
<div class="pill-row">
    <div class="pill"><span class="pill-icon">⚡</span><div><div class="pill-title">Real-time</div><div class="pill-desc">news &amp; articles</div></div></div>
    <div class="pill"><span class="pill-icon">👤</span><div><div class="pill-title">Leadership</div><div class="pill-desc">insights</div></div></div>
    <div class="pill"><span class="pill-icon">📅</span><div><div class="pill-title">Events</div><div class="pill-desc">&amp; conferences</div></div></div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SEARCH PANEL  (same fields, logic untouched — recency replaced with date range)
# ============================================================
with st.form("search_form"):
    st.markdown('<div class="search-heading">🔍 Search Executive News &amp; Events</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        exec_name = st.text_input("👤 Executive Name", placeholder="e.g., Satya Nadella")
        designation = st.text_input("💼 Designation", placeholder="e.g., CEO")
        num_results = st.slider("Number of results to retrieve", 1, 20, 6)
    with col2:
        company = st.text_input("🏢 Company Name", placeholder="e.g., Microsoft")
        topic = st.text_input("📄 Topic, Event, or Problem", placeholder="e.g., AI investment announcement")
        date_range = st.date_input(
            "📅 Date Range",
            value=(date.today() - timedelta(days=365), date.today()),
            max_value=date.today(),
            help="Narrows the search to this exact window — more precise than a recency bucket, and sent directly to the search API.",
        )
    submitted = st.form_submit_button("🔎  Fetch Live Information  →", use_container_width=True)

# Normalize the date_input result: it can be a single date while the user
# is mid-selection, or a (start, end) tuple once both are picked.
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    start_date, end_date = date_range[0], date.today()
else:
    start_date, end_date = date_range, date.today()


# ============================================================
# SEARCH LOGIC — UNCHANGED FROM PREVIOUS VERSION
# ============================================================
def _q(name, company_, title_, include_title=True, include_company=True):
    """Build a quoted, executive-anchored query string."""
    parts = [f'"{name.strip()}"']
    if include_company and company_.strip():
        parts.append(f'"{company_.strip()}"')
    if include_title and title_.strip():
        parts.append(title_.strip())
    if topic.strip():
        parts.append(topic.strip())
    return " ".join(parts)

def score_result(r, name, company_, title_):
    """Relevance score: at least partial name match required; company/title add confidence."""
    text = (r.get("title", "") + " " + r.get("content", "")).lower()
    name_tokens = [t for t in name.strip().lower().split() if t]
    full_match = name.strip().lower() in text
    last_name_match = len(name_tokens) > 1 and name_tokens[-1] in text
    any_token_match = any(t in text for t in name_tokens if len(t) > 2)

    if full_match:
        score = 3
    elif last_name_match:
        score = 2
    elif any_token_match:
        score = 1
    else:
        return 0

    if company_.strip() and company_.strip().lower() in text:
        score += 2
    if title_.strip() and title_.strip().lower() in text:
        score += 1
    return score

def run_search(query, n):
    fetch_n = min(max(n * 2, 10), 20)
    resp = client.search(
        query=query,
        topic="news",
        max_results=fetch_n,
        include_answer=False,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )
    return resp.get("results", [])

def fetch_executive_results(name, company_, title_, n):
    """
    Progressive, quota-efficient search:
    1) Name + Company + Title  (most targeted, run once)
    2) Name + Company          (only if step 1 insufficient)
    3) Name + Title            (only if step 2 still insufficient)
    """
    seen_urls = set()
    scored = []

    def add(results):
        for r in results:
            url = r.get("url", "")
            if url in seen_urls:
                continue
            s = score_result(r, name, company_, title_)
            if s > 0:
                seen_urls.add(url)
                scored.append((s, r))

    def sufficient():
        strong = sum(1 for s, _ in scored if s >= 4)
        return len(scored) >= n and strong >= max(1, n // 2)

    queries_run = []

    q1 = _q(name, company_, title_, include_title=True, include_company=True)
    add(run_search(q1, n))
    queries_run.append(q1)

    if not sufficient() and company_.strip():
        q2 = _q(name, company_, title_, include_title=False, include_company=True)
        if q2 not in queries_run:
            add(run_search(q2, n))
            queries_run.append(q2)

    if not sufficient() and title_.strip():
        q3 = _q(name, company_, title_, include_title=True, include_company=False)
        if q3 not in queries_run:
            add(run_search(q3, n))
            queries_run.append(q3)

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:n]], len(queries_run)

def parse_date(raw):
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            return datetime.strptime(raw[:len(fmt) + 5] if "%z" in fmt else raw[:19], fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(raw, errors="coerce")
    except Exception:
        return None

# ============================================================
# RESULTS / STATES
# ============================================================
if submitted:
    if not exec_name and not company:
        st.error("Enter at least an Executive Name or Company Name.")
    else:
        with st.spinner("Analyzing executive intelligence · fetching current sources..."):
            try:
                if exec_name.strip():
                    results, num_queries = fetch_executive_results(
                        exec_name, company, designation, num_results
                    )
                    query_note = f"Used {num_queries} search {'query' if num_queries == 1 else 'queries'} to reach these results."
                else:
                    fallback_query = " ".join(p for p in [company.strip(), designation.strip(), topic.strip() or "News OR Events"] if p)
                    results = run_search(fallback_query, num_results)
                    query_note = "Used 1 search query to reach these results."
            except Exception as e:
                st.markdown(f"""
                <div class="empty-state">
                    <div class="empty-icon">⚠️</div>
                    <div class="empty-title">Unable to retrieve intelligence</div>
                    <div class="empty-sub">We couldn't retrieve the requested information. Please check the search parameters and try again.<br><span style="color:#6B7280;font-size:12px;">({e})</span></div>
                </div>
                """, unsafe_allow_html=True)
                results = []
                query_note = ""

        if not results:
            if query_note != "" or exec_name or company:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <div class="empty-title">No results found</div>
                    <div class="empty-sub">Try broadening the topic, removing the designation filter, or widening recency.</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # ---- Status row ----
            st.markdown(f"""
            <div class="status-row">
                <div class="status-left">
                    <span class="status-icon">📋</span>
                    <div>
                        <div class="status-title">Search Results</div>
                        <div class="status-sub">{query_note}</div>
                    </div>
                </div>
                <div class="status-left">
                    <span class="count-badge">{len(results)} results</span>
                    <span class="live-pill"><span class="live-dot"></span>Live data</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ---- Timeline view ----
            timeline_rows = []
            for r in results:
                d = parse_date(r.get("published_date"))
                if d is not None and not pd.isna(d):
                    timeline_rows.append({"date": pd.to_datetime(d), "title": r.get("title", "Untitled")})

            st.markdown("""
            <div class="dash-card">
                <div class="dash-card-title">📈 Coverage Timeline</div>
                <div class="dash-card-sub">Distribution of articles, events, and mentions over time.</div>
            """, unsafe_allow_html=True)

            if timeline_rows:
                df_timeline = pd.DataFrame(timeline_rows).sort_values("date")
                counts = df_timeline.groupby(df_timeline["date"].dt.date).size().reset_index(name="articles")
                counts.columns = ["date", "articles"]
                st.bar_chart(counts.set_index("date"), color="#8B5CF6")
            else:
                st.caption("Timeline unavailable — no publish dates returned for these results.")

            st.markdown("</div>", unsafe_allow_html=True)

            # ---- CSV export ----
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(["Title", "URL", "Published Date"])
            for r in results:
                writer.writerow([r.get("title", ""), r.get("url", ""), r.get("published_date", "")])
            st.download_button(
                label="⬇ Download results as CSV",
                data=csv_buffer.getvalue(),
                file_name="search_results.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # ---- Headline cards ----
            st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
            for r in results:
                title = r.get("title", "Untitled")
                url = r.get("url", "")
                pub = r.get("published_date", "")
                domain = url.split("/")[2] if url.count("/") >= 2 else ""
                st.markdown(
                    f"""<div class="result-card">
                            <div class="result-meta"><span class="badge-news">NEWS</span>{domain} · {pub}</div>
                            <a class="result-title" href="{url}" target="_blank">{title}</a>
                            <div class="result-source">Read article →</div>
                        </div>""",
                    unsafe_allow_html=True
                )
else:
    # ---- Default empty state before first search ----
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🧭</div>
        <div class="empty-title">Ready to investigate</div>
        <div class="empty-sub">Enter an executive and company to discover recent news, events, and developments.</div>
    </div>
    """, unsafe_allow_html=True)
