import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
engine = analytics_database_engine_connection()

def generic_silver_query(table_name):
    with engine.begin() as conn:
       result_list = []
       result = conn.execute(text(f"""
        SELECT *
        FROM dbo.{table_name}
        """)).mappings().all()
    
       
        
    return result