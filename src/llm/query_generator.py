import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

class SQLQueryGenerator:
    def __init__(self, schema_info: dict, api_key: str):
        self.schema_info = schema_info
        genai.configure(api_key=api_key)
        # Configure safety settings
        generation_config = {
            "temperature": 0.0,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.0-pro-exp",  # Using a supported model from the list
            generation_config=generation_config,
            safety_settings=safety_settings
        )

    def generate_query(self, question: str) -> str:
        """Generate SQL query from natural language question"""
        formatted_schema = self._format_schema_for_prompt()
        
        prompt = f"""You are an expert SQL query generator.
        Given the following PostgreSQL database schema:
        {formatted_schema}
        
        Generate a SQL query to answer this question: {question}
        
        Return ONLY the SQL query without any additional text or explanation.
        The query should be correct, efficient, and follow PostgreSQL syntax."""

        try:
            response = self.model.generate_content(prompt)
            if response.parts:
                return self._extract_sql_query(response.text)
            else:
                raise Exception("No response generated from the model")
        except Exception as e:
            raise Exception(f"Error generating SQL query: {str(e)}")

    def _format_schema_for_prompt(self) -> str:
        """Format schema information for the prompt"""
        schema_text = []
        for table, columns in self.schema_info.items():
            cols = [f"    - {col['column_name']} ({col['data_type']})" for col in columns]
            schema_text.append(f"Table: {table}\nColumns:\n" + "\n".join(cols))
        return "\n\n".join(schema_text)

    def _extract_sql_query(self, response: str) -> str:
        """Extract SQL query from LLM response"""
        # Remove any markdown formatting if present
        query = response.replace("```sql", "").replace("```", "").strip()
        return query