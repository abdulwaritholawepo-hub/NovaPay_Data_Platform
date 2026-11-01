
import os
import sys
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from production_database.production_DB_connection import (
    production_database_engine_connection,
)
from sqlalchemy import text
import logging
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
                        snapshot_boundary.snapshot_at,
                        c.customer_id,
                        COALESCE(e.event_sequence, 0) AS event_sequence,
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
                    CROSS JOIN (
                        SELECT SYSUTCDATETIME() AS snapshot_at
                    ) AS snapshot_boundary
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

    if not customer_snapshot:
        raise ValueError(
            "Customer baseline snapshot returned no records."
        )

    snapshot_at = customer_snapshot[0]["snapshot_at"]

    customer_snapshot_list = [
        {
            key: value
            for key, value in customer.items()
            if key != "snapshot_at"
        }
        for customer in customer_snapshot
    ]

    logger.info(
        "SUCCESS | Customer baseline snapshot retrieved | "
        "records=%d | snapshot_at=%s",
        len(customer_snapshot_list),
        snapshot_at,
    )

    return {
        "snapshot_at": snapshot_at,
        "customer_snapshot_list": customer_snapshot_list,
    }
