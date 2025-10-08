"""
ui/streamlit_app.py: Streamlit user interface for the LLM-SQL application.
To run: streamlit run ui/streamlit_app.py
"""
import streamlit as st
import pandas as pd
from app.main import run_query_pipeline # Import the main function

def display_results(df: pd.DataFrame, summary: str, sql_query: str = None):
    """Displays the final results in a structured format."""
    st.markdown("---")
    
    st.subheader("🤖 Insights & Explanation")
    st.markdown(summary)
    
    if sql_query:
        st.subheader("📝 SQL Query Used")
        st.code(sql_query, language="sql")
        
    if not df.empty:
        st.subheader("📋 Raw Data Table")
        st.dataframe(df)

def main_app():
    """Main function to run the Streamlit application."""
    
    st.set_page_config(
        page_title="LLM-SQL Data Analyst", 
        page_icon="🔍", 
        layout="wide"
    )
    
    st.title("Ask Your Data! 📊")
    st.caption("Natural Language to SQL Query Engine powered by Gemini & PostgreSQL.")

    # User Input
    user_query = st.text_input(
        "Enter your question about the database (e.g., 'What are the top 5 selling categories and their total revenue?')",
        key="user_query_input"
    )

    if st.button("Generate Insights", type="primary") and user_query:
        # State management for loading/caching
        with st.spinner("Processing... Generating SQL, executing query, and structuring results..."):
            
            # Execute the full pipeline
            df_results, final_summary, error_message, sql_query = run_query_pipeline(user_query)

        st.markdown("---")
        
        if error_message:
            st.error(f"❌ Pipeline Failed: {error_message}")
        elif final_summary and "cannot answer" in final_summary: # Handle "QUERY_NOT_POSSIBLE" case
            st.warning(final_summary)
        else:
            # Success state
            if df_results is not None and not df_results.empty:
                display_results(df_results, final_summary, sql_query)
            elif final_summary:
                # Handle queries that return an empty set but a valid summary
                st.info("Query executed successfully, but returned no data.")
                st.subheader("🤖 Explanation")
                st.markdown(final_summary)
            else:
                st.error("An unknown error occurred during processing.")

if __name__ == "__main__":
    main_app()