 
from sqlalchemy import create_engine, text
import pyodbc
from urllib.parse import quote_plus
def production_database_engine_connection():
    connection_string = quote_plus(
        r"DRIVER={ODBC Driver 18 for SQL Server};"
        r"SERVER=DESKTOP-HIGKAHM\SQLEXPRESS;"
        r"DATABASE=NovaPayDB;"
        r"Trusted_Connection=yes;"
        r"TrustServerCertificate=yes;"
    )

    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
    return engine

    