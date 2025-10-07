import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnector:
    def __init__(self):
        self.engine = self._create_connection()

    def _create_connection(self):
        """Create database connection"""
        db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'northwind'),  # Updated to northwind
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        return create_engine(connection_string)

    def execute_query(self, query: str):
        """Execute SQL query and return results as pandas DataFrame"""
        try:
            with self.engine.connect() as connection:
                result = pd.read_sql(query, connection)
                return result
        except Exception as e:
            raise Exception(f"Error executing query: {str(e)}")

    def get_table_schema(self) -> dict:
        """Get schema information for all tables"""
        schema_query = """
            SELECT 
                t.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable
            FROM 
                information_schema.tables t
            JOIN 
                information_schema.columns c 
                ON t.table_name = c.table_name 
                AND t.table_schema = c.table_schema
            WHERE 
                t.table_schema = 'public'
                AND t.table_type = 'BASE TABLE'
            ORDER BY 
                t.table_name, c.ordinal_position;
        """
        try:
            with self.engine.connect() as connection:
                result = pd.read_sql(schema_query, connection)
                
                # Group by table_name and create the expected format
                schema_dict = {}
                for table_name in result['table_name'].unique():
                    table_columns = result[result['table_name'] == table_name]
                    schema_dict[table_name] = [
                        {
                            'column_name': row['column_name'],
                            'data_type': row['data_type'],
                            'is_nullable': row['is_nullable']
                        }
                        for _, row in table_columns.iterrows()
                    ]
                return schema_dict
        except Exception as e:
            raise Exception(f"Error fetching schema: {str(e)}")