
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from production_database.production_DB_connection import production_database_engine_connection
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from transform.customer_transformer import transform_customers
import datetime as dt

import logging

logger = logging.getLogger(__name__)

production_engine = production_database_engine_connection()
analytics_engine = analytics_database_engine_connection()


def get_customer_baseline_snapshot():
    logger.info("START | Customer baseline snapshot retrieval started")

    with production_engine.connect() as connection:
        connection.execute(
            text("SET TRANSACTION ISOLATION LEVEL SNAPSHOT")
        )
        connection.commit()

        with connection.begin():
            customer_snapshot = connection.execute(text("""
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
            """)).mappings().all()

    customer_snapshot_list = [
        dict(customer) for customer in customer_snapshot
    ]

    logger.info(
        "SUCCESS | Customer baseline snapshot retrieved | records=%d",
        len(customer_snapshot_list)
    )

    return customer_snapshot_list


def prepare_customer_baseline_records(customer_snapshot_list):
    logger.info(
        "START | Preparing customer baseline records | records=%d",
        len(customer_snapshot_list)
    )

    customer_records = []
    checkpoint_records = []

    for customer in customer_snapshot_list:
        customer_record = {
            key: value
            for key, value in customer.items()
            if key != "event_sequence"
        }

        checkpoint_record = {
            "customer_id": customer["customer_id"],
            "baseline_event_sequence": customer["event_sequence"]
        }

        customer_records.append(customer_record)
        checkpoint_records.append(checkpoint_record)

    logger.info(
        "SUCCESS | Customer baseline records prepared | customers=%d | checkpoints=%d",
        len(customer_records),
        len(checkpoint_records)
    )

    return customer_records, checkpoint_records


def transform_customer_baseline(customer_records):
    logger.info(
        "START | Customer baseline transformation started | records=%d",
        len(customer_records)
    )

    transformed_customers = transform_customers(
        customer_data=customer_records
    )

    logger.info(
        "SUCCESS | Customer baseline transformation completed | records=%d",
        len(transformed_customers)
    )
    return transformed_customers


def prepare_customer_dimension_records(
    transformed_customers,
    baseline_valid_from,
):
    logger.info(
        "START | Customer dimension record preparation | records=%d",
        len(transformed_customers),
    )

    dimension_records = []

    for customer in transformed_customers:
        dimension_record = {
            "customer_id": customer["customer_id"],
            "account_number": customer["account_number"],
            "first_name": customer["first_name"],
            "last_name": customer["last_name"],
            "full_name": customer["full_name"],
            "customer_initials": customer["customer_initials"],
            "gender": customer["gender"],
            "date_of_birth": customer["date_of_birth"],
            "age": customer["age"],
            "is_adult": customer["is_adult"],
            "eligibility": customer["eligibility"],
            "customer_segment": customer["customer_segment"],
            "phone_number": customer["phone_number"],
            "email_domain": customer["email_domain"],
            "duplicate_email": customer["duplicate_email"],
            "account_status": customer["account_status"],
            "wallet_balance": customer["wallet_balance"],
            "wallet_segment": customer["wallet_segment"],
            "risk_level": customer["risk_level"],
            "risk_flag": customer["risk_flag"],
            "created_at": customer["created_at"],
            "account_tenure_days": customer["account_tenure_days"],
            "customer_lifetime_stage": customer[
                "customer_lifetime_stage"
            ],
            "valid_from": baseline_valid_from,
            "valid_to": None,
            "is_current": True,
        }

        dimension_records.append(dimension_record)

    logger.info(
        "SUCCESS | Customer dimension records prepared | records=%d",
        len(dimension_records),
    )

    return dimension_records


def validate_customer_baseline_records(dimension_records):
    logger.info(
        "START | Customer baseline validation | records=%d",
        len(dimension_records),
    )

    # 1. Validate record count
    assert len(dimension_records) == 15, (
        f"Expected 15 customer records, got {len(dimension_records)}"
    )

    # 2. Validate unique customer_id values
    customer_ids = [
        record["customer_id"]
        for record in dimension_records
    ]

    assert len(customer_ids) == len(set(customer_ids)), (
        "Duplicate customer_id values found in baseline records"
    )

    # 3. Validate identical valid_from timestamps
    valid_from_values = [
        record["valid_from"]
        for record in dimension_records
    ]

    assert len(set(valid_from_values)) == 1, (
        "Baseline records do not share the same valid_from timestamp"
    )

    # 4. Validate initial SCD Type 2 fields
    invalid_scd_records = [
        record["customer_id"]
        for record in dimension_records
        if record["valid_to"] is not None
        or record["is_current"] is not True
    ]

    assert not invalid_scd_records, (
        "Invalid initial SCD Type 2 fields for customer IDs: "
        f"{invalid_scd_records}"
    )

    logger.info(
        "SUCCESS | Customer baseline validation passed | "
        "record_count=%d | unique_customer_ids=%d | "
        "shared_valid_from=%s | current_records=%d",
        len(dimension_records),
        len(set(customer_ids)),
        valid_from_values[0],
        len(dimension_records),
    )

    return True


def validate_customer_dimension_schema(dimension_records):
    logger.info(
        "START | Customer dimension schema validation | records=%d",
        len(dimension_records),
    )

    expected_columns = {
        "customer_id",
        "account_number",
        "first_name",
        "last_name",
        "full_name",
        "customer_initials",
        "gender",
        "date_of_birth",
        "age",
        "is_adult",
        "eligibility",
        "customer_segment",
        "phone_number",
        "email_domain",
        "duplicate_email",
        "account_status",
        "wallet_balance",
        "wallet_segment",
        "risk_level",
        "risk_flag",
        "created_at",
        "account_tenure_days",
        "customer_lifetime_stage",
        "valid_from",
        "valid_to",
        "is_current",
    }

    if not dimension_records:
        raise ValueError(
            "Customer dimension schema validation failed: "
            "no dimension records were provided"
        )

    validation_errors = []

    for index, record in enumerate(dimension_records, start=1):
        actual_columns = set(record.keys())

        missing_columns = expected_columns - actual_columns
        unexpected_columns = actual_columns - expected_columns

        if missing_columns or unexpected_columns:
            validation_errors.append({
                "record_number": index,
                "customer_id": record.get("customer_id"),
                "missing_columns": sorted(missing_columns),
                "unexpected_columns": sorted(unexpected_columns),
            })

    if validation_errors:
        logger.error(
            "FAILURE | Customer dimension schema validation | errors=%s",
            validation_errors,
        )
        raise ValueError(
            f"Customer dimension schema validation failed: "
            f"{validation_errors}"
        )

    logger.info(
        "SUCCESS | Customer dimension schema validation passed | "
        "records=%d | expected_columns=%d",
        len(dimension_records),
        len(expected_columns),
    )

    return True

if __name__ == "__main__":
    snapshot = get_customer_baseline_snapshot()

    customer_records, checkpoint_records = (
        prepare_customer_baseline_records(snapshot)
    )

    transformed_customers = transform_customer_baseline(
        customer_records
    )
    customer_dimension_records = prepare_customer_dimension_records(
        transformed_customers= transformed_customers,
        baseline_valid_from=dt.datetime.now())
    print(len(customer_dimension_records))
    print(customer_dimension_records[0])
    
    validate_customer_baseline_records(customer_dimension_records)
    validate_customer_dimension_schema(customer_dimension_records)
