import streamlit as st
from tavily import TavilyClient

client = TavilyClient(api_key=__import__("os").environ.get("TAVILY_API_KEY"))

st.set_page_config(page_title="Executive & Event Search Assistant", page_icon="🔎", layout="centered")
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

def build_query():
    return " ".join(p for p in [exec_name, designation, company, topic] if p)

if submitted:
    if not exec_name and not company:
        st.error("Enter at least an Executive Name or Company Name.")
    else:
        query = build_query()
        with st.spinner("Fetching live results..."):
            try:
                resp = client.search(query=query, topic="news", max_results=num_results, include_answer=False)
                results = resp.get("results", [])
            except Exception as e:
                st.error(f"Error: {e}")
                results = []

        for r in results:
            with st.container(border=True):
                st.subheader(r.get("title", "Untitled"))
                st.caption(r.get("published_date", ""))
                st.write(r.get("content", "")[:400])
                if r.get("url"):
                    st.markdown(f"[Read more]({r['url']})")
