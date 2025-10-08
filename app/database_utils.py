"""
app/database_utils.py: Manages PostgreSQL connection, metadata extraction, and query execution.
"""
from typing import Any, Dict, List, Tuple
import mysql.connector
import json
# def get_connection():
#     return mysql.connector.connect(
#         host='localhost',       # or your host, e.g., '127.0.0.1' or AWS RDS endpoint
#         user='root',            # your MySQL username
#         password='12345niki',   # your MySQL password
#         database='neuleap'      # your MySQL database
#     )

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        print("Connecting to database...")
        conn = mysql.connector.connect(
            user='root',
            password='12345niki',
            host='localhost',
            database='neuleap'
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None
    

# Save this (or similar logic) in a file like 'llm/llm_utils.py'

from google import genai
from google.genai import types
import os
import yaml

def llm_generate_description(table_name: str, column_name: str, data_type: str, sample_data: List[str]) -> str:
    """
    Uses the Gemini LLM to generate a concise, human-readable description
    for a database column based on its data type and sampled values.
    """
    try:
        # Initialize the client (will use GEMINI_API_KEY env var)
        client = genai.Client(api_key='AIzaSyDC7RjTk1qnZQQsSHrj3TqGT6ZhF7ktREg')
    except Exception as e:
        return f"LLM Initialization Error: {e}"

    # Construct the instruction for the LLM
    system_prompt = (
        "You are a database metadata expert. Your task is to generate a single, concise (1-2 sentence) "
        "human-readable description for a database column. Use the provided table name, column name, "
        "data type, and actual sampled values as context."
    )

    user_prompt = f"""
    Generate a 1-2 sentence description for the following column:
    
    - Table: {table_name}
    - Column: {column_name}
    - Data Type: {data_type}
    - Sampled Data Values: [{', '.join(sample_data)}]
    
    Example output format: "This column tracks the unique ID for each customer and serves as the primary key for the table."
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',  # Fast and capable model for text generation
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)]),
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,  # Keep temperature low for factual, non-creative responses
            ),
        )
        # Clean up the output: remove leading/trailing whitespace
        return response.text.strip()
    
    except Exception as e:
        print(f"LLM Description Generation Failed for {table_name}.{column_name}: {e}")
        return f"<<ERROR: LLM failed to generate description.>>"

def extract_schema_metadata(schema_name: str = 'neuleap') -> str:
    """
    Extracts table and column metadata, using LLM for description generation 
    and listing distinct values for low-cardinality columns (<= 20).
    """
    conn = get_db_connection()
    print("Database connection established.")

    if not conn:
        print("ERROR: Could not connect to database for neuleap")
        return "ERROR: Could not connect to database for neuleap"

    schema_dict: Dict[str, Any] = {}
    cursor = conn.cursor(dictionary=True)
    
    LOW_CARDINALITY_THRESHOLD = 20
    SAMPLE_ROWS_FOR_LLM = 20 # Renamed constant for clarity

    try:
        # 1. Get all tables (same logic)
        cursor.execute(f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{schema_name}'
              AND table_type = 'BASE TABLE';
        """)
        # for i in cursor.fetchall():
        #     print("hii", i)
        tables = [row['TABLE_NAME'] for row in cursor.fetchall()]

        for table in tables:
            # Table Structure - NOTE: LLM could also generate this description!
            table_data: Dict[str, Any] = {
                '_description': f'<<A 1-2 line summary of what the {table} table contains.>>' 
            }
            columns_data: Dict[str, Dict[str, str]] = {}

            # 2. Get column details (same logic)
            # ... (omitted column fetching query for brevity) ... 
            
            # --- Re-execute column fetching for full context ---
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = '{schema_name}' AND table_name = '{table}';
            """)
            columns = cursor.fetchall()
            # for col in columns:
            #     print("col", col)
            
            for col in columns:
                col_name = col['COLUMN_NAME']
                data_type = col['DATA_TYPE']
                known_values_list: List[str] = []
                
                # --- A: Extract Sample Data for LLM Input ---
                sample_values: List[str] = []
                try:
                    sample_query = f"""
                        SELECT `{col_name}` 
                        FROM `{schema_name}`.`{table}` 
                        ORDER BY RAND() 
                        LIMIT {SAMPLE_ROWS_FOR_LLM};
                    """
                    cursor.execute(sample_query)
                    sample_values = [
                        str(row[col_name]) if row[col_name] is not None else 'NULL' 
                        for row in cursor.fetchall()
                    ]
                except mysql.connector.Error as e_sample:
                    print(f"Warning: Failed to sample data for {table}.{col_name}: {e_sample}")


                # --- B: **LLM CALL** to Generate Description ---
                if sample_values:
                    llm_description = llm_generate_description(table, col_name, data_type, sample_values)
                    print(f"LLM Description for {table}.{col_name}: {llm_description}")
                else:
                    llm_description = f"The {col_name} column is of type {data_type}."


                # --- C: Check for Low-Cardinality Values (<= 20 unique) (same logic) ---
                # ... (omitted cardinality check query for brevity) ...
                try:
                    check_query = f"""
                        SELECT COUNT(DISTINCT `{col_name}`) AS unique_count
                        FROM `{schema_name}`.`{table}`;
                    """
                    cursor.execute(check_query)
                    unique_count = cursor.fetchone()['unique_count']

                    if unique_count is not None and unique_count > 0 and unique_count <= LOW_CARDINALITY_THRESHOLD:
                        value_query = f"""
                            SELECT DISTINCT `{col_name}`
                            FROM `{schema_name}`.`{table}`
                            ORDER BY 1
                            LIMIT {LOW_CARDINALITY_THRESHOLD};
                        """
                        cursor.execute(value_query)
                        known_values_list = [
                            str(row[col_name]) for row in cursor.fetchall()
                        ]
                except mysql.connector.Error as e_card:
                    print(f"Warning: Failed to check cardinality for {table}.{col_name}: {e_card}")


                # --- D: Combine all details ---
                details_string = f"Data Type: {data_type}"
                if known_values_list:
                     details_string += f" | Known Values (<= {LOW_CARDINALITY_THRESHOLD} unique): {', '.join(known_values_list)}"


                # Populate the column's details
                columns_data[col_name] = {
                    '_description': llm_description, # <-- Now using LLM-generated text
                    'details': details_string
                }
            
            table_data['columns'] = columns_data
            schema_dict[table] = table_data

    except mysql.connector.Error as e:
        return f"ERROR: Failed to query schema information: {e}"
    finally:
        cursor.close()
        conn.close()

    print("Schema metadata extraction complete.", schema_dict)
    # Final step: Convert the Python dictionary to a JSON string
    with open("output___.json", "w") as f:
        json.dump(schema_dict, f, indent=2, sort_keys=False)
    return json.dumps(schema_dict, indent=2, sort_keys=False)

def execute_sql_query(sql_query: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Executes a read-only SQL query on PostgreSQL and returns the results.
    
    Args:
        sql_query: The SQL query to execute.
        
    Returns:
        A tuple: (list of results, error message or empty string).
    """
    
    conn = get_db_connection()
    if not conn:
        return [], "ERROR: Could not connect to database for query execution."

    cursor = conn.cursor()
    results = []
    error = ""
    
    # Security Best Practice: Only allow SELECT/WITH statements
    normalized_query = sql_query.strip().upper()
    if not (normalized_query.startswith("SELECT") or normalized_query.startswith("WITH")):
        conn.close()
        return [], "SECURITY ERROR: Only read-only SELECT or WITH statements are allowed."

    try:
        cursor.execute(sql_query)
        # Fetch column names
        column_names = [desc[0] for desc in cursor.description]
        # Fetch all rows and format as a list of dictionaries
        rows = cursor.fetchall()
        for row in rows:
            results.append(dict(zip(column_names, row)))

    except mysql.connector.Error as e:
        error = f"SQL EXECUTION ERROR: {e}"
    except Exception as e:
        error = f"An unexpected error occurred: {e}"
    finally:
        cursor.close()
        conn.close()
        
    return results, error




def test_connection():
    try:
        conn = get_db_connection()
        print("Connection established successfully!")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    # Simple test to extract metadata
    # print(extract_schema_metadata("neuleap_1st"))
    extract_schema_metadata("neuleap")