import os
from dotenv import load_dotenv
from src.database.db_connector import DatabaseConnector

load_dotenv()

try:
    print("Testing Northwind database connection...")
    db = DatabaseConnector()
    
    print("Getting table schema...")
    schema = db.get_table_schema()
    print("✅ Database connection successful!")
    print("Tables found:", list(schema.keys()))
    
    # Test some basic queries
    print("\nTesting sample queries...")
    
    # Count tables
    tables = ["categories", "customers", "employees", "orders", "order_details", "products"]
    for table in tables:
        if table in schema:
            try:
                result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result.iloc[0]['count']
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error - {e}")
    
    # Test a join query
    print("\nTesting complex query...")
    complex_query = """
    SELECT 
        p.product_name,
        c.category_name,
        SUM(od.quantity * od.unit_price) as total_sales
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    JOIN order_details od ON p.product_id = od.product_id
    GROUP BY p.product_name, c.category_name
    ORDER BY total_sales DESC
    LIMIT 5
    """
    
    results = db.execute_query(complex_query)
    print("Top 5 products by sales:")
    print(results)
    
except Exception as e:
    print(f"❌ Error: {e}")