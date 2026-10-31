
import os
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, project_root)

from sqlalchemy import text
from production_database.production_DB_connection import (
    production_database_engine_connection,
)


def main():
    engine = production_database_engine_connection()

    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT DB_NAME()")
        ).scalar_one()

        customer_count = connection.execute(
            text("SELECT COUNT(*) FROM dbo.Customers")
        ).scalar_one()

        event_count = connection.execute(
            text("SELECT COUNT(*) FROM dbo.CustomerChangeEvents")
        ).scalar_one()

    print(f"Connected database: {database_name}")
    print(f"Customer records: {customer_count}")
    print(f"Change event records: {event_count}")


if __name__ == "__main__":
    main()
