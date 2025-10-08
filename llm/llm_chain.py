"""
llm/llm_chain.py: Handles all interactions with the Gemini LLM via LangChain.
"""
from ast import Return
from os import environ
from google import genai
from google.genai import types
from llm.prompts import (
    format_sql_generation_prompt,
    format_result_restructuring_prompt,
)

# Initialize LangChain with Gemini (assuming GEMINI_API_KEY is in environment)
try:
    # Use gemini-2.5-flash for faster response times for chat/generation
    llm = genai.Client(api_key='AIzaSyDC7RjTk1qnZQQsSHrj3TqGT6ZhF7ktREg')
except Exception as e:
    print(f"Error initializing Gemini LLM: {e}")
    llm = None  # Handle the failure gracefully

def generate_sql_query(schema_context: str, user_query: str) -> str:
    """
    Uses Gemini to translate a natural language query into a PostgreSQL SQL query.

    Args:
        schema_context: Detailed description of the database schema.
        user_query: The user's question.

    Returns:
        The generated SQL query string.
    """
    if not llm:
        return "ERROR: LLM not initialized."

    try:
        # print("Schema Context Length:", len(schema_context))
        # print("User Query:", user_query)
        user_prompt=user_query
        system_prompt = (
            "You are an expert SQL query generator.\n\n"
            "Based on this schema, generate a valid MySQL SQL query for:\n"
            "\"{user_prompt}\"\n\n"
            "Return only the SQL query without explanations.\n"
            "{schema_context}"
        ).format(user_prompt=user_prompt, schema_context=schema_context)
        # print("system_prompt", system_prompt)
        
        response = llm.models.generate_content(
             model='gemini-2.5-flash',  # Fast and capable model for text generation
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)]),
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.5,  # Keep temperature low for factual, non-creative responses
            ),
        )
        
        # print("hi", response.candidates[0].content.parts[0].text)
        generated_query =  response.candidates[0].content.parts[0].text

        # print("Generated raw response from LLM:", generated_query)
        # Simple validation based on prompt rules
        if not generated_query or 'QUERY_NOT_POSSIBLE' in generated_query:
            return "QUERY_NOT_POSSIBLE"
        
        # Security Best Practice: Remove potential unwanted markdown formatting
        if generated_query.startswith("```sql"):
            generated_query = generated_query.strip("```sql").strip()
        if generated_query.endswith("```"):
            generated_query = generated_query.strip("```").strip()

        # print("Generated SQL Query:", generated_query.strip())
        return generated_query.strip()
    except Exception as e:
        print(f"Error during SQL generation: {e}")
        return "ERROR: Failed to generate SQL query."

def restructure_results(user_question: str, sql_results_csv: str) -> str:
    """
    Uses Gemini to transform raw SQL results into a user-friendly summary.

    Args:
        user_question: The original user question.
        sql_results_csv: The raw SQL results formatted as a CSV string.

    Returns:
        A human-readable summary of the results.
    """
    if not llm:
        return "ERROR: LLM not initialized."

    try:
        # messages = format_result_restructuring_prompt(user_question, sql_results_csv)
        user_prompt=user_question
        system_prompt=f"""
        You are an expert SQL result summarizer.

        Based on the following SQL results, provide a concise summary:

        {sql_results_csv}
        """
        # Invoke the LLM
        response = llm.models.generate_content(
            model='gemini-2.5-flash',  # Fast and capable model for text generation
            contents=[
                types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)]),
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.5,  # Keep temperature low for factual, non-creative responses
            ),
        )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"Error during result restructuring: {e}")
        return "ERROR: Failed to restructure results."