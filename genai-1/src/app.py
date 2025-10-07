import streamlit as st
import os
from dotenv import load_dotenv
from database.db_connector import DatabaseConnector
from llm.query_generator import SQLQueryGenerator

# Load environment variables
load_dotenv()

# Initialize database connector
@st.cache_resource
def init_db():
    return DatabaseConnector()

# Initialize query generator
@st.cache_resource
def init_query_generator(schema_info):
    return SQLQueryGenerator(
        schema_info=schema_info,
        api_key=os.getenv('GROQ_API_KEY')
    )

def main():
    st.title("Northwind Database Insights Assistant")
    st.write("Ask questions about the Northwind trading company data in natural language!")
    
    # Add some example questions
    st.markdown("""
    ### Try asking questions like:
    - What are the top 5 best-selling products?
    - Which customers have placed the most orders?
    - What were the total sales by category?
    - Show me all orders from customers in Germany
    - Which employees have the highest sales?
    """)

    # Initialize components
    db = init_db()
    schema_info = db.get_table_schema()
    query_generator = init_query_generator(schema_info)

    # User input
    user_question = st.text_input(
        "Ask a question about the Northwind data:",
        placeholder="e.g., What are the top 5 products by total sales amount?"
    )

    if user_question:
        try:
            # Generate SQL query
            with st.spinner("Generating SQL query..."):
                sql_query = query_generator.generate_query(user_question)
                
            # Display the generated SQL
            with st.expander("View Generated SQL Query"):
                st.code(sql_query, language="sql")

            # Execute query and display results
            with st.spinner("Fetching results..."):
                results = db.execute_query(sql_query)
                
            if not results.empty:
                st.write("### Results")
                st.dataframe(results)
                
                # Show summary info
                st.info(f"Found {len(results)} records")
            else:
                st.info("No results found for your query.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()