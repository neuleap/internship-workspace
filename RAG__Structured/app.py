"""
app.py — Streamlit + Gemini SQL Assistant
Connects to PostgreSQL, analyzes schema silently,
then enables Gemini-powered SQL generation and chat.
"""

# ---------------------------------------------------------------
# STEP 1 — IMPORT LIBRARIES
# ---------------------------------------------------------------
import os
import re
import json
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, inspect, text
from langchain_community.utilities import SQLDatabase
from google import genai
from dotenv import load_dotenv
import plotly.express as px

# ---------------------------------------------------------------
# STEP 2 — LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------------
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------------------------------------------------------
# STEP 3 — STREAMLIT CONFIG
# ---------------------------------------------------------------
st.set_page_config(page_title="SQL Query Assistant", layout="wide")
st.title("🧠 Gemini Data Analyst & Conversational Chat")
st.write(
    "Use the first section for SQL generation and the second for "
    "conversational follow-ups based on results."
)

# ---------------------------------------------------------------
# SCHEMA EXTRACTION FUNCTION
# ---------------------------------------------------------------
def get_db_schema_and_lovs(db_engine, db_inspector, sql_db):
    """Inspect tables and retrieve LOVs (lookup values)."""
    tables_to_process = ["customers", "orders", "order_details", "products"]
    schema_info = []

    with db_engine.connect() as conn:
        for table in tables_to_process:
            if table not in db_inspector.get_table_names():
                schema_info.append(f"Table '{table}' not found in database.")
                continue

            columns = db_inspector.get_columns(table)
            column_details = []
            for col in columns:
                col_name = col["name"]
                col_type = str(col["type"])
                detail = f"{col_name} ({col_type})"

                if "id" in col_name.lower() and table not in ["order_details"]:
                    column_details.append(detail + " (ID/Key column)")
                    continue

                try:
                    query = text(f'SELECT DISTINCT "{col_name}" FROM "{table}"')
                    result = conn.execute(query).fetchall()
                    values = [r[0] for r in result if r[0] is not None]
                    if 0 < len(values) <= 10:
                        lovs = [str(v) for v in values]
                        detail += f" - LOVs: [{', '.join(lovs[:10])}]"
                    elif len(values) > 10:
                        detail += (
                            f" - NOTE: High cardinality ({len(values)} distinct values)."
                            " LOVs skipped."
                        )
                    column_details.append(detail)
                except Exception as err:  # pylint: disable=broad-exception-caught
                    column_details.append(
                        detail + f" - NOTE: Error during LOV extraction: {err}"
                    )

            if column_details:
                schema_info.append(f"{table}:\n  - {';\n  - '.join(column_details)}")
    return "\n\n".join(schema_info)

# ---------------------------------------------------------------
# SCHEMA DESCRIPTION USING GEMINI
# ---------------------------------------------------------------
def generate_schema_description_json(client, text_schema):
    """Use Gemini to convert text schema into structured JSON."""
    prompt = f"""
    You are a database analyst.
    Below is the extracted database schema (table names, column names, data types, and sample values/LOVs).

    DATABASE SCHEMA TEXT:
    {text_schema}

    Your task:
    1. Write a short description for each table.
    2. Describe each column briefly.
    3. Output valid JSON with this structure:

    {{
      "tables": {{
        "table_name": {{
          "description": "...",
          "columns": {{
            "column_name": {{"description": "..."}}
          }}
        }}
      }}
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        clean_json = re.sub(r"```json|```", "", response.text.strip())
        json.loads(clean_json)
        return clean_json
    except Exception as err:  # pylint: disable=broad-exception-caught
        st.error(f"❌ Error generating schema description: {err}")
        return "Schema description could not be generated."

# ---------------------------------------------------------------
# STEP 4 — DATABASE CONNECTION & SILENT SCHEMA ANALYSIS
# ---------------------------------------------------------------
try:
    connection_string = (
        f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(connection_string)
    db = SQLDatabase(engine)
    inspector = inspect(engine)
    st.success("✅ Connected to PostgreSQL successfully!")

    # Perform schema extraction immediately (no spinner, silent)
    client = genai.Client(api_key=GEMINI_API_KEY)
    st.session_state.db_schema_context = get_db_schema_and_lovs(engine, inspector, db)
    st.session_state.db_schema_description = generate_schema_description_json(
        client, st.session_state.db_schema_context
    )

except (ConnectionError, OSError, Exception) as e:  # pylint: disable=broad-exception-caught
    st.error(f"❌ Database connection failed: {e}")
    st.stop()

# ---------------------------------------------------------------
# STEP 5 — STATE INITIALIZATION
# ---------------------------------------------------------------
if "memory_str" not in st.session_state:
    st.session_state.memory_str = ""

SQL_GENERATION_CONTEXT = f"""
You are an expert SQL data analyst working with PostgreSQL (Northwind database).

DATABASE SCHEMA DETAILS (including LOVs for low-cardinality columns):
{st.session_state.db_schema_context}

Rules:
- Use PostgreSQL syntax.
- Use correct table & column names.
- Use proper JOINs between foreign keys.
- Return only SQL — no explanations or markdown.
"""

# ---------------------------------------------------------------
# STEP 6 — SQL GENERATION & EXECUTION
# ---------------------------------------------------------------
st.subheader("1️⃣ Generate New SQL Query & Results")

with st.form(key="sql_form"):
    user_question = st.text_input(
        "Enter your question for the database:",
        placeholder="Example: 'Show top 5 products by total sales'",
        key="sql_input",
    )
    submit_sql_button = st.form_submit_button("🚀 Run SQL Query")

if submit_sql_button and user_question:
    st.session_state.memory_str = ""
    df = pd.DataFrame()
    clean_sql = ""
    summary_text = ""

    with st.spinner("Generating SQL query with Gemini..."):
        try:
            prompt_sql = f"""
            {SQL_GENERATION_CONTEXT}

            User Question:
            "{user_question}"

            Task:
            Generate a valid PostgreSQL SQL query.
            Return only the SQL (no markdown, no explanation).
            """
            sql_response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt_sql
            )
            generated_sql = sql_response.text.strip()
            clean_sql = re.sub(r"^```[a-zA-Z]*|```$", "", generated_sql).strip()

            st.subheader("🧾 Generated SQL Query")
            st.code(clean_sql, language="sql")

            df = pd.read_sql_query(clean_sql, engine)
            if df.empty:
                st.warning("⚠️ Query executed, but returned no data.")
                summary_text = "Query executed but returned no data."
            else:
                st.success("✅ Query executed successfully!")
                st.dataframe(df)

                summary_prompt = f"""
                You are a data analyst.
                Below is a sample of the query result:
                {df.head(10).to_json(orient="records", indent=2)}

                Write a short 2–3 sentence summary describing:
                - What this data represents
                - Key insights
                """
                summary_response = client.models.generate_content(
                    model="gemini-2.5-flash", contents=summary_prompt
                )
                summary_text = summary_response.text.strip()

                st.subheader("🧠 Gemini Summary")
                st.write(summary_text)

                st.subheader("📊 Suggested Visualization")
                df_json = df.head(10).to_json(orient="records", indent=2)
                vis_prompt = f"""
                You are a data visualization assistant.
                Analyze the data and return JSON suggestion:
                {{
                  "chart_type": "bar",
                  "x_axis": "column_name",
                  "y_axis": "column_name"
                }}
                Data sample:
                {df_json}
                """
                vis_response = client.models.generate_content(
                    model="gemini-2.5-flash", contents=vis_prompt
                )
                vis_text = vis_response.text.strip()

                try:
                    vis_json = json.loads(re.sub(r"```json|```", "", vis_text).strip())
                except json.JSONDecodeError:
                    st.warning("⚠️ Gemini returned malformed JSON for visualization.")
                    vis_json = {"chart_type": "none"}

                chart_type = vis_json.get("chart_type", "none")
                x_axis = vis_json.get("x_axis")
                y_axis = vis_json.get("y_axis")

                if (
                    chart_type == "none"
                    or not x_axis
                    or not y_axis
                    or x_axis not in df.columns
                    or y_axis not in df.columns
                ):
                    st.info("ℹ️ Gemini decided no suitable visualization.")
                else:
                    st.success(f"✅ Gemini suggests a {chart_type} chart.")
                    if df[y_axis].dtype in ["int64", "float64", "int32", "float32"]:
                        if chart_type == "bar":
                            st.bar_chart(df.set_index(x_axis)[y_axis])
                        elif chart_type == "pie":
                            fig = px.pie(df, names=x_axis, values=y_axis)
                            st.plotly_chart(fig)
                        elif chart_type == "scatter":
                            st.scatter_chart(df.set_index(x_axis)[y_axis])
                    else:
                        st.warning(f"⚠️ '{y_axis}' is not numeric.")
                        st.dataframe(df)

            st.session_state.memory_str = (
                f"\n--- NEW CONVERSATION THREAD ---\n"
                f"Initial Question: {user_question}\n"
                f"Generated SQL: {clean_sql}\n"
                f"Summary: {summary_text}\n"
                f"DataFrame (Sample): {df.to_json(orient='records', indent=2)}\n"
                f"Schema Description: {st.session_state.db_schema_description}\n"
            )
        except Exception as err:  # pylint: disable=broad-exception-caught
            st.error(f"❌ Error executing SQL query: {err}")

st.markdown("---")

# ---------------------------------------------------------------
# STEP 7 — CONVERSATIONAL CHAT
# ---------------------------------------------------------------
st.subheader("2️⃣ Conversational Chat (Memory-Based)")
if not st.session_state.memory_str:
    st.info("Ask a query in section 1 first to load data into memory.")
else:
    st.write("Current analysis loaded. Ask follow-up questions.")
    with st.form(key="chat_form"):
        follow_up_input = st.text_input(
            "Ask a question based on the last executed query:",
            placeholder="What was the country with the highest sales?",
            key="chat_input",
        )
        submit_chat_button = st.form_submit_button("🤔 Get Contextual Answer")

    if submit_chat_button and follow_up_input:
        with st.spinner("Analyzing memory with Gemini..."):
            prompt_memory = f"""
            CONTEXT:
            You are a conversational data analyst.

            PREVIOUS ANALYSIS HISTORY:
            {st.session_state.memory_str}

            INSTRUCTION:
            - Answer ONLY using the information above.
            - If insufficient info, say: "I don’t have enough information in memory."
            - Be concise and factual.

            USER QUESTION:
            "{follow_up_input}"
            """
            mem_response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt_memory
            )
            follow_up_answer = mem_response.text.strip()

            st.subheader("🧠 Gemini’s Contextual Answer")
            st.write(follow_up_answer)

            st.session_state.memory_str += (
                f"\nUser Follow-up: {follow_up_input}\n"
                f"Gemini Response: {follow_up_answer}\n"
            )
