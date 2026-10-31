
from production_database.production_DB_connection import (
    production_database_engine_connection,
)
from sqlalchemy import text
import os
import sys
import logging

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


logger = logging.getLogger(__name__)


def get_customer_baseline_snapshot():
    logger.info(
        "START | Customer baseline snapshot retrieval started"
    )

    production_engine = production_database_engine_connection()

    with production_engine.connect() as connection:
        connection.execute(
            text("SET TRANSACTION ISOLATION LEVEL SNAPSHOT")
        )
        connection.commit()

        with connection.begin():
            customer_snapshot = connection.execute(
                text("""
                    SELECT
                        c.customer_id,
                        CASE
                            WHEN e.event_sequence IS NULL THEN 0
                            ELSE e.event_sequence
                        END AS event_sequence,
                        c.first_name,
                        c.last_name,
                        c.email,
                        c.phone_number,
                        c.date_of_birth,
                        c.gender,
                        c.account_number,
                        c.wallet_balance,
                        c.account_status,
                        c.created_at
                    FROM dbo.Customers AS c
                    LEFT JOIN (
                        SELECT
                            customer_id,
                            MAX(event_sequence) AS event_sequence
                        FROM dbo.CustomerChangeEvents
                        GROUP BY customer_id
                    ) AS e
                        ON c.customer_id = e.customer_id
                """)
            ).mappings().all()

    customer_snapshot_list = [
        dict(customer)
        for customer in customer_snapshot
    ]

    logger.info(
        "SUCCESS | Customer baseline snapshot retrieved | records=%d",
        len(customer_snapshot_list),
    )

    return customer_snapshot_list
