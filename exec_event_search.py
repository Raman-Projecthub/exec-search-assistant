"""
Executive & Event Search Assistant
Run: streamlit run exec_event_search.py
Requires: pip install streamlit anthropic
Set env var ANTHROPIC_API_KEY before running.
"""

import os
import json
import streamlit as st
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

st.set_page_config(page_title="Executive & Event Search Assistant", page_icon="🔎", layout="centered")
st.title("🔎 Executive & Event Search Assistant")
st.caption("Fetch real-time articles, news, and events regarding specific company leadership.")

with st.form("search_form"):
    col1, col2 = st.columns(2)
    with col1:
        exec_name = st.text_input("Executive Name", placeholder="e.g., Satya Nadella")
        designation = st.text_input("Designation", placeholder="e.g., CEO")
        num_results = st.slider("Number of results to retrieve", 1, 20, 6)
    with col2:
        company = st.text_input("Company Name", placeholder="e.g., Microsoft")
        topic = st.text_input("Topic, Event, or Problem", placeholder="e.g., AI investment announcement")
        recency = st.selectbox("Recency", ["Any time", "Past 24 hours", "Past week", "Past month", "Past year"])
    submitted = st.form_submit_button("Fetch Live Information", use_container_width=True)

def build_query():
    parts = [p for p in [exec_name, designation, company, topic] if p]
    return " ".join(parts)

def recency_clause():
    return "" if recency == "Any time" else f" Restrict results to news from the {recency.lower()}."

if submitted:
    if not exec_name and not company:
        st.error("Enter at least an Executive Name or Company Name.")
    else:
        query = build_query()
        with st.spinner("Fetching live results..."):
            try:
                resp = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2000,
                    tools=[{"type": "web_search_20250305", "name": "web_search"}],
                    messages=[{
                        "role": "user",
                        "content": (
                            f"Search the web for the {num_results} most relevant, accurate, "
                            f"and recent results about: {query}.{recency_clause()} "
                            "Return ONLY a JSON array (no markdown, no prose) where each item has: "
                            "\"title\", \"source\", \"date\", \"summary\" (2-3 sentences), \"url\". "
                            "Use only information found via search — do not fabricate."
                        )
                    }]
                )
                text = "".join(b.text for b in resp.content if b.type == "text")
                text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                results = json.loads(text)
            except json.JSONDecodeError:
                st.error("Could not parse results. Raw response:")
                st.write(text)
                results = []
            except Exception as e:
                st.error(f"Error: {e}")
                results = []

        for r in results:
            with st.container(border=True):
                st.subheader(r.get("title", "Untitled"))
                st.caption(f"{r.get('source','')} • {r.get('date','')}")
                st.write(r.get("summary", ""))
                if r.get("url"):
                    st.markdown(f"[Read more]({r['url']})")
