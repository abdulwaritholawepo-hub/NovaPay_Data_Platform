from sqlalchemy import text 

from production_database.production_DB_connection import production_database_engine_connection

def get_records(table_name):
    engine = production_database_engine_connection()
    records_list = []
    with engine.begin() as conn:
        queried_records = conn.execute(text(
            f"""
            SELECT *
            FROM {table_name}
            """
        ))
        for records in queried_records.mappings():
            records_list.append(dict(records))
    return records_list
