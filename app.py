import streamlit as st
import pandas as pd
from agent_logic import process_query, HIGH_INTENT_QUERIES, generate_summary, validate_company, search_companies
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Company Research Agent",
    page_icon="🔍",
    layout="wide"
)

# Title and Description
st.title("🔍 Company Research & Partner Sourcing Agent")
st.markdown("""
**Goal:** Find consulting firms, studios, and transformation boutiques that are partner‑ready for SaaS, Cloud, AI/ML, QA, and white‑label execution.
""")

# Sidebar
st.sidebar.header("Research Configuration")

st.sidebar.subheader("Target Industry / Keywords")
selected_queries = st.sidebar.multiselect(
    "Select High-Intent Queries",
    HIGH_INTENT_QUERIES,
    default=[HIGH_INTENT_QUERIES[0], HIGH_INTENT_QUERIES[4]] # Default to first few
)

num_results = st.sidebar.slider("Max Results Per Query", min_value=1, max_value=20, value=5)

run_btn = st.sidebar.button("Start Research", type="primary")

# Main Area
if run_btn:
    if not selected_queries:
        st.warning("Please select at least one query.")
    else:
        results_container = st.container()
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        all_companies = []
        total_queries = len(selected_queries)
        
        for i, query in enumerate(selected_queries):
            status_text.text(f"Running Query {i+1}/{total_queries}: {query}")
            
            # Run search and validation
            # We need to adapt the logic slightly to be more stream-friendly if possible,
            # but for now, we'll just run the function.
            
            # To provide better feedback, let's break down the process_query inside app.py or modify agent_logic
            # But adhering to the plan, we use the imported logic.
            # However, `process_query` in agent_logic does it all.
            # Let's import the components to show progress if we want, or just call process_query.
            
            try:
                # Direct call for simplicity
                companies = process_query(query, num_results=num_results)
                
                # Check for duplicates before adding
                existing_urls = {c['Website'] for c in all_companies}
                for c in companies:
                    if c['Website'] not in existing_urls:
                        all_companies.append(c)
                        existing_urls.add(c['Website'])
                        
            except Exception as e:
                st.error(f"Error processing query '{query}': {e}")
            
            progress_bar.progress((i + 1) / total_queries)
            
        status_text.text("Research Complete!")
        
        # Display Results
        if all_companies:
            df = pd.DataFrame(all_companies)
            
            # Reorder columns matches user request: Company | Website | Why It Fits | Evidence | LinkedIn Search Strings
            cols = ["Company", "Website", "Why It Fits", "Evidence", "LinkedIn Search Strings"]
            # Ensure all cols exist
            for col in cols:
                if col not in df.columns:
                    df[col] = "" # Should satisfy
            
            df = df[cols]
            
            st.subheader(" Identified Partners")
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Analysis & Summary")
            summary = generate_summary(df)
            st.markdown(summary)
            
            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Results (CSV)",
                csv,
                "partner_shortlist.csv",
                "text/csv",
                key='download-csv'
            )
            
            # Markdown Table Export
            md_table = df.to_markdown(index=False)
            st.download_button(
                "Download Results (Markdown)",
                md_table,
                "partner_shortlist.md",
                "text/markdown",
                key='download-md'
            )
            
        else:
            st.info("No companies found that matched the strict validation criteria. Try increasing the number of results or selecting more queries.")

with st.expander("Usage Guide"):
    st.markdown("""
    1. **Select Queries**: Choose from the pre-defined high-intent search queries.
    2. **Set Limit**: Adjust how many search results to fetch per query (more results = slower but more comprehensive).
    3. **Run**: Click 'Start Research'.
    4. **Review**: The agent will search, visit websites, validate content against the checklist, and present a shortlist.
    """)
