import streamlit as st
import pandas as pd
import json
import re
from sqlalchemy import create_engine, inspect, text
from langchain_community.utilities import SQLDatabase
from google import genai
from dotenv import load_dotenv
import os

# --- Load environment variables ---
load_dotenv()

# Read database credentials and API key from .env file
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
api_key = os.getenv("GOOGLE_API_KEY")

# --- 1. Streamlit UI setup ---
st.set_page_config(page_title="AI SQL Assistant", layout="wide")
st.title("💾 AI-Powered SQL Query Assistant")
st.write("Ask questions in natural language and get live query results with explanations.")

# --- 2. Connect to PostgreSQL ---
connection_string = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

try:
    engine = create_engine(connection_string)
    db = SQLDatabase(engine)
    inspector = inspect(engine)
    st.success("✅ Connected to PostgreSQL database successfully!")
except Exception as e:
    st.error(f"❌ Database connection failed: {e}")
    st.stop()

# --- 3. Extract sample table data (LOVs) once ---
tables = list(db.get_usable_table_names())
table_data = {}  # Dictionary to store extracted table and column information

with engine.connect() as conn:
    for table in tables:
        print(f"\nExtracting from: {table}")

        # Get metadata for each column in the table
        columns = inspector.get_columns(table)
        table_data[table] = {}

        for col in columns:
            col_name = col["name"]

            # Skip columns that look like ID fields
            if "id" in col_name.lower():
                print(f"  Skipping ID column: {col_name}")
                continue

            try:
                # Retrieve distinct values for each column
                query = text(f'SELECT DISTINCT "{col_name}" FROM "{table}"')
                result = conn.execute(query).fetchall()

                # Extract non-null values only
                values = [r[0] for r in result if r[0] is not None]

                # Include LOVs only if the column has ≤ 10 distinct values
                if len(values) <= 10:
                    table_data[table][col_name] = values
                    print(f"  Added {len(values)} LOVs for {col_name}")
                else:
                    # Skip columns with too many distinct values
                    table_data[table][col_name] = []
                    print(f"  {col_name} has {len(values)} distinct values — skipping LOVs")

                print(f"  Collected {len(values)} LOVs for {col_name}")

            except Exception as e:
                print(f"  Skipped {col_name}: {e}")

# --- 4. Initialize Gemini client ---
client = genai.Client(api_key=api_key)

# --- 5. Create schema description prompt ---
prompt_desc = f"""
You are a database analyst.

Below is JSON data showing table names, column names, and their 10 sample values (LOVs).

Your task:
1. Write a short, clear description for each table.
2. For each column, describe what it likely represents.
3. When relevant, mention what the LOVs indicate.
4. Output must be valid JSON in this structure:

{{
  "tables": {{
    "table_name": {{
      "description": "Short summary of what this table stores",
      "Table Relations": "Identify logical relationships (joins) between tables (e.g. customer_id in orders → id in customers)",
      "columns": {{
        "column_name": {{
          "description": "Meaning of the column",
          "lovs": [list of sample values]
        }}
      }}
    }}
  }}
}}
"""

with st.spinner("🔍 Analyzing database schema..."):
    desc_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_desc + "\n\nHere is the extracted data:\n\n" + json.dumps(table_data, indent=2)
    )

schema_json = desc_response.text.strip()

# --- 6. Use session state to persist user input ---
if "query_submitted" not in st.session_state:
    st.session_state.query_submitted = False

user_question = st.text_input("💬 Ask a question about your data:")

if st.button("Generate & Run SQL Query"):
    st.session_state.query_submitted = True
    st.session_state.user_question = user_question

# --- 7. Run the query only once ---
if st.session_state.query_submitted and st.session_state.user_question:
    user_question = st.session_state.user_question

    with st.spinner("🧠 Generating SQL query..."):
        prompt_sql = f"""
        You are an expert SQL query generator.

        Here is the JSON schema describing the database and LOVs:

        {schema_json}

        Based on this schema, generate a valid PostgreSQL SQL query for:

        "{user_question}"

        Return only the SQL query without explanations.
        """

        sql_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_sql
        )

        generated_sql = sql_response.text.strip()
        clean_sql = re.sub(r"^```[a-zA-Z]*|```$", "", generated_sql.strip()).strip()

        st.subheader("🧾 Generated SQL Query")
        st.code(clean_sql, language="sql")

        # --- Execute SQL query ---
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(clean_sql, conn)

            st.subheader("📊 Query Result")
            st.dataframe(df, use_container_width=True)

            # --- Summary generation ---
            summary_prompt = f"""
            You are a data analyst. Below is a sample of SQL query results:
            {df.head(10).to_json(orient='records', indent=2)}

            Write a 3–5 sentence summary describing:
            1. What this data represents
            2. Key columns and trends
            3. Insights you can infer
            """

            with st.spinner("🧩 Generating summary..."):
                summary_response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=summary_prompt
                )

            st.subheader("📝 Data Summary")
            st.write(summary_response.text.strip())

        except Exception as e:
            st.error(f"❌ Error executing SQL query: {e}")
