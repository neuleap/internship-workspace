"""
app/main.py: Main orchestration script for the LLM-SQL pipeline.
"""
from app.database_utils import extract_schema_metadata, execute_sql_query
from llm.llm_chain import generate_sql_query, restructure_results
import pandas as pd
from typing import Tuple, Optional, Dict, List, Any

# Define the schema name to be used for the project
SCHEMA_NAME = "analytics_schema" # Placeholder: Replace with your actual schema name

def run_query_pipeline(user_question: str) -> Tuple[Optional[pd.DataFrame], Optional[str], Optional[str], Optional[str]]:
    """
    Executes the full end-to-end pipeline: Metadata -> SQL Gen -> Execution -> Restructure.

    Args:
        user_question: The natural language question from the user.

    Returns:
        A tuple: (DataFrame of results, human-readable summary, error_message).
    """
    error_message = None
    final_df = None
    summary = None
    
    print("--- 1. Loading Schema Metadata from output.json ---")
    import os
    import json
    schema_context = None
    if os.path.exists("output.json"):
        with open("output.json", "r") as f:
            schema_context = f.read()
        print(f"Loaded schema context from output.json. Length: {len(schema_context)} characters")
    else:
        error_message = "Metadata file output.json not found."
        print(error_message)
        return final_df, summary, error_message, sql_query
    # Optionally, parse JSON if needed:
    # schema_dict = json.loads(schema_context)

    # print("schema_context:", schema_context)

    print("--- 2. Generating SQL Query via Gemini ---")
    sql_query = generate_sql_query(schema_context, user_question)

    print("hello")
    print("sql_query:", sql_query)
    if "ERROR" in sql_query:
        
        error_message = f"SQL Generation Failed: {sql_query}"
        print(error_message)
        return final_df, summary, error_message, None
    
    if sql_query == "QUERY_NOT_POSSIBLE":
        summary = "I cannot answer this question based on the available database schema. Please rephrase your question."
        print(f"SQL Generation Result: {sql_query}")
        return final_df, summary, error_message, None
    
    print(f"Generated SQL: {sql_query}")

    print("--- 3. Executing SQL Query ---")
    raw_results, exec_error = execute_sql_query(sql_query)
    if exec_error:
        error_message = f"SQL Execution Failed: {exec_error}"
        print(error_message)
        return final_df, summary, error_message, None
    
    print(f"Query executed successfully. Rows returned: {len(raw_results)}")

    # Convert results to DataFrame for optional display in UI
    final_df = pd.DataFrame(raw_results)
    
    # Convert results to CSV string for clean input to the restructuring LLM
    if not final_df.empty:
        sql_results_csv = final_df.to_csv(index=False)
    else:
        sql_results_csv = "No results returned."

    print("--- 4. Restructuring Results via Gemini ---")
    summary = restructure_results(user_question, sql_results_csv)
    
    print("Pipeline Complete.")
    return final_df, summary, error_message,sql_query

if __name__ == '__main__':
    # Example Usage:
    example_question = "What are the top 5 selling product categories and their total sales amount?"
    
    df_results, final_summary, error = run_query_pipeline(example_question)
    
    print("\n" + "="*50)
    if error:
        print(f"PIPELINE FAILED: {error}")
    else:
        print(f"User Question: {example_question}")
        print("\n--- FINAL SUMMARY ---")
        print(final_summary)
        print("\n--- RAW DATA PREVIEW ---")
        if df_results is not None:
            print(df_results.head())
        else:
            print("No data frame to display.")
    print("="*50)