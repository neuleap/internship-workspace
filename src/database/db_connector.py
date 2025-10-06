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
            'database': os.getenv('DB_NAME', 'northwind'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        return create_engine(connection_string)

    def execute_query(self, query: str) -> list:
        """Execute SQL query and return results"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                return [dict(row) for row in result]
        except Exception as e:
            raise Exception(f"Error executing query: {str(e)}")

    def get_table_schema(self) -> dict:
        """Get schema information for all tables"""
        schema_query = """
            SELECT 
                t.table_name,
                array_agg(
                    json_build_object(
                        'column_name', c.column_name,
                        'data_type', c.data_type,
                        'description', col_description(format('%I.%I', t.table_schema, t.table_name)::regclass, c.ordinal_position)
                    )
                ) as columns
            FROM 
                information_schema.tables t
            JOIN 
                information_schema.columns c 
                ON t.table_name = c.table_name 
                AND t.table_schema = c.table_schema
            WHERE 
                t.table_schema = 'public'
            GROUP BY 
                t.table_name;
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(schema_query))
                return {row.table_name: row.columns for row in result}
        except Exception as e:
            raise Exception(f"Error fetching schema: {str(e)}")