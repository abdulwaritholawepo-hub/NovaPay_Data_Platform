
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

from sqlalchemy import text
from analytics_database.analytics_DB_connection import (
    analytics_database_engine_connection,
)
import logging

logger = logging.getLogger(__name__)


def finalize_customer_baseline(
    baseline_run_id,
    expected_customer_count,
):
    engine = analytics_database_engine_connection()

    with engine.begin() as conn:

        # 1. Verify that this baseline run exists and is in progress.
        run = conn.execute(
            text("""
                SELECT
                    status,
                    expected_customer_count
                FROM gold.customer_baseline_run WITH (UPDLOCK, HOLDLOCK)
                WHERE baseline_run_id = :baseline_run_id
            """),
            {"baseline_run_id": baseline_run_id},
        ).mappings().one_or_none()

        if run is None:
            raise ValueError(
                f"Baseline run {baseline_run_id} does not exist."
            )

        if run["status"] != "IN_PROGRESS":
            raise ValueError(
                f"Cannot finalize baseline run with status "
                f"{run['status']}."
            )

        if run["expected_customer_count"] != expected_customer_count:
            raise ValueError(
                "The supplied expected customer count does not match "
                "the count recorded for this baseline run."
            )

        # 2. Verify the number of dimension records for this baseline.
        # This assumes the baseline's customer IDs can be identified
        # using its checkpoint records.
        dimension_count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM gold.dim_customer AS dc
                INNER JOIN gold.customer_baseline_checkpoint AS cp
                    ON cp.customer_id = dc.customer_id
                WHERE cp.baseline_run_id = :baseline_run_id
                  AND dc.is_current = 1
            """),
            {"baseline_run_id": baseline_run_id},
        ).scalar_one()

        checkpoint_count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM gold.customer_baseline_checkpoint
                WHERE baseline_run_id = :baseline_run_id
            """),
            {"baseline_run_id": baseline_run_id},
        ).scalar_one()

        if (
            dimension_count != expected_customer_count
            or checkpoint_count != expected_customer_count
        ):
            raise ValueError(
                "Baseline validation failed. "
                f"Expected {expected_customer_count} customers; "
                f"found {dimension_count} matching dimension records "
                f"and {checkpoint_count} checkpoints."
            )

        # 3. Mark the run as completed.
        conn.execute(
            text("""
                UPDATE gold.customer_baseline_run
                SET
                    status = 'COMPLETED',
                    completed_at = SYSUTCDATETIME(),
                    loaded_customer_count = :loaded_customer_count
                WHERE baseline_run_id = :baseline_run_id
                  AND status = 'IN_PROGRESS'
            """),
            {
                "baseline_run_id": baseline_run_id,
                "loaded_customer_count": dimension_count,
            },
        )

        # 4. Set the authoritative baseline reference.
        conn.execute(
            text("""
                UPDATE gold.customer_baseline_control
                SET
                    active_baseline_run_id = :baseline_run_id,
                    updated_at = SYSUTCDATETIME()
                WHERE control_id = 1
            """),
            {"baseline_run_id": baseline_run_id},
        )

        # Insert the initial control row if one does not exist.
        conn.execute(
            text("""
                IF NOT EXISTS (
                    SELECT 1
                    FROM gold.customer_baseline_control
                    WHERE control_id = 1
                )
                BEGIN
                    INSERT INTO gold.customer_baseline_control
                    (
                        control_id,
                        active_baseline_run_id,
                        updated_at
                    )
                    VALUES
                    (
                        1,
                        :baseline_run_id,
                        SYSUTCDATETIME()
                    )
                END
            """),
            {"baseline_run_id": baseline_run_id},
        )

        logger.info(
            "Customer baseline run %s finalized successfully. "
            "Customers loaded: %s",
            baseline_run_id,
            dimension_count,
        )

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
