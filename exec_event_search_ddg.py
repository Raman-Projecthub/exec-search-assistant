import os
import io
import csv
from datetime import datetime

import streamlit as st
import pandas as pd
from tavily import TavilyClient

client = TavilyClient(api_key=os.environ.get("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"))

st.set_page_config(page_title="Executive & Event Search Assistant", page_icon="🔎", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #0e1117; }
div[data-testid="stForm"] {
    border: 1px solid #2a2e37;
    border-radius: 12px;
    padding: 24px;
    background-color: #12151c;
}
.result-card {
    border: 1px solid #2a2e37;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    background-color: #161a23;
}
.result-card a {
    text-decoration: none;
    color: #e6e6e6;
    font-size: 16px;
    font-weight: 500;
}
.result-card a:hover { color: #4da3ff; }
.result-source { color: #8a8f98; font-size: 12px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.title("🔎 Executive & Event Search Assistant")
st.caption("Fetch real-time articles, news, and events regarding specific company leadership.")

RECENCY_MAP = {"Any time": None, "Past 24 hours": "d", "Past week": "w", "Past month": "m", "Past year": "y"}

with st.form("search_form"):
    col1, col2 = st.columns(2)
    with col1:
        exec_name = st.text_input("Executive Name", placeholder="e.g., Satya Nadella")
        designation = st.text_input("Designation", placeholder="e.g., CEO")
        num_results = st.slider("Number of results to retrieve", 1, 20, 6)
    with col2:
        company = st.text_input("Company Name", placeholder="e.g., Microsoft")
        topic = st.text_input("Topic, Event, or Problem", placeholder="e.g., AI investment announcement")
        recency = st.selectbox("Recency", list(RECENCY_MAP.keys()))
    submitted = st.form_submit_button("Fetch Live Information", use_container_width=True)

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
    """Relevance score: name mention is required; company/title add confidence."""
    text = (r.get("title", "") + " " + r.get("content", "")).lower()
    score = 0
    if name.strip().lower() in text:
        score += 3
    else:
        return 0
    if company_.strip() and company_.strip().lower() in text:
        score += 2
    if title_.strip() and title_.strip().lower() in text:
        score += 1
    return score

def run_search(query, n):
    resp = client.search(query=query, topic="news", max_results=n, include_answer=False)
    return resp.get("results", [])

def fetch_executive_results(name, company_, title_, n):
    """
    Progressive, quota-efficient search:
    1) Name + Company + Title  (most targeted, run once)
    2) Name + Company          (only if step 1 insufficient)
    3) Name + Title            (only if step 2 still insufficient)
    Stops as soon as enough high-confidence (name-matched) results are found.
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

if submitted:
    if not exec_name and not company:
        st.error("Enter at least an Executive Name or Company Name.")
    else:
        with st.spinner("Fetching live results..."):
            try:
                if exec_name.strip():
                    results, num_queries = fetch_executive_results(
                        exec_name, company, designation, num_results
                    )
                    st.caption(f"Used {num_queries} search {'query' if num_queries == 1 else 'queries'} to reach these results.")
                else:
                    fallback_query = " ".join(p for p in [company.strip(), designation.strip(), topic.strip() or "News OR Events"] if p)
                    results = run_search(fallback_query, num_results)
            except Exception as e:
                st.error(f"Error: {e}")
                results = []

        if not results:
            st.info("No results found.")
        else:
            timeline_rows = []
            for r in results:
                d = parse_date(r.get("published_date"))
                if d is not None and not pd.isna(d):
                    timeline_rows.append({"date": pd.to_datetime(d), "title": r.get("title", "Untitled")})

            if timeline_rows:
                df_timeline = pd.DataFrame(timeline_rows).sort_values("date")
                counts = df_timeline.groupby(df_timeline["date"].dt.date).size().reset_index(name="articles")
                counts.columns = ["date", "articles"]
                st.subheader("Coverage Timeline")
                st.bar_chart(counts.set_index("date"))
            else:
                st.caption("Timeline unavailable — no publish dates returned for these results.")

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

            st.subheader("Results")
            for r in results:
                title = r.get("title", "Untitled")
                url = r.get("url", "")
                domain = url.split("/")[2] if url.count("/") >= 2 else ""
                st.markdown(
                    f"""<div class="result-card">
                            <a href="{url}" target="_blank">{title}</a>
                            <div class="result-source">{domain}</div>
                        </div>""",
                    unsafe_allow_html=True
                )
