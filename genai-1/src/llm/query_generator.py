from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

class SQLQueryGenerator:
    def __init__(self, schema_info: dict, api_key: str):
        self.schema_info = schema_info
        self.client = Groq(api_key=api_key)
        # Updated to use a current supported model
        self.model_name = "llama-3.3-70b-versatile"  # Changed from llama-3.1-70b-versatile

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
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert SQL query generator. Return only valid SQL queries without explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model_name,
                temperature=0.0,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            
            if chat_completion.choices:
                return self._extract_sql_query(chat_completion.choices[0].message.content)
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