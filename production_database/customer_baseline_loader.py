
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from transform.customer_transformer import transform_customers

from production_database.customer_baseline_snapshot import (
    get_customer_baseline_snapshot,
)
import uuid

import logging

logger = logging.getLogger(__name__)

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


def validate_customer_baseline_records(
    dimension_records,
    expected_customer_count,
):
    logger.info(
        "START | Customer baseline validation | records=%d",
        len(dimension_records),
    )

    # 1. Validate record count
    assert expected_customer_count > 0, (
    "Expected customer count must be greater than zero."
)

    assert len(dimension_records) == expected_customer_count, (
    f"Expected {expected_customer_count} customer records, "
    f"got {len(dimension_records)}"
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


def load_customer_baseline(
    baseline_run_id,
    dimension_records,
    checkpoint_records,
    expected_customer_count,
    snapshot_at,
):
    logger.info(
        "START | Customer baseline loading | "
        "run_id=%s | customers=%d",
        baseline_run_id,
        expected_customer_count,
    )

    if expected_customer_count <= 0:
        raise ValueError(
            "Expected customer count must be greater than zero."
        )

    if len(dimension_records) != expected_customer_count:
        raise ValueError(
            "Dimension record count does not match expected count."
        )

    if len(checkpoint_records) != expected_customer_count:
        raise ValueError(
            "Checkpoint record count does not match expected count."
        )

    dimension_customer_ids = {
        record["customer_id"]
        for record in dimension_records
    }

    checkpoint_customer_ids = {
        record["customer_id"]
        for record in checkpoint_records
    }
    if len(dimension_customer_ids) != len(dimension_records):
        raise ValueError(
            "Duplicate customer IDs found in dimension records."
        )


    if len(checkpoint_customer_ids) != len(checkpoint_records):
        raise ValueError(
            "Duplicate customer IDs found in checkpoint records."
        )

    if any(
        record["baseline_event_sequence"] < 0
        for record in checkpoint_records
    ):
        raise ValueError(
            "Baseline event sequences cannot be negative."
        )

    if dimension_customer_ids != checkpoint_customer_ids:
        raise ValueError(
            "Dimension customer IDs and checkpoint customer IDs "
            "do not match."
        )

    if any(
        record["valid_from"] != snapshot_at
        for record in dimension_records
    ):
        raise ValueError(
            "Dimension valid_from values do not match snapshot_at."
        )

    with analytics_engine.begin() as conn:

        run = conn.execute(
            text("""
                SELECT
                    status,
                    expected_customer_count
                FROM gold.customer_baseline_run
                    WITH (UPDLOCK, HOLDLOCK)
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
                f"Baseline run is not IN_PROGRESS: {run['status']}"
            )

        if run["expected_customer_count"] != expected_customer_count:
            raise ValueError(
                "Expected customer count does not match "
                "the baseline run."
            )

        existing_dimension_count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM gold.dim_customer WITH (TABLOCKX, HOLDLOCK)
            """)
        ).scalar_one()

        if existing_dimension_count != 0:
            raise RuntimeError(
                "Customer dimension table is not empty. "
                "Initial baseline loading has been stopped."
            )
        existing_checkpoint_count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM gold.customer_baseline_checkpoint
                    WITH (TABLOCKX, HOLDLOCK)
            """)
        ).scalar_one()

        if existing_checkpoint_count != 0:
            raise RuntimeError(
                "Checkpoint table is not empty. "
                "Initial baseline loading has been stopped."
            )

        

        dimension_insert = text("""
            INSERT INTO gold.dim_customer
            (
                customer_id,
                account_number,
                first_name,
                last_name,
                full_name,
                customer_initials,
                gender,
                date_of_birth,
                age,
                is_adult,
                eligibility,
                customer_segment,
                phone_number,
                email_domain,
                duplicate_email,
                account_status,
                wallet_balance,
                wallet_segment,
                risk_level,
                risk_flag,
                created_at,
                account_tenure_days,
                customer_lifetime_stage,
                valid_from,
                valid_to,
                is_current
            )
            VALUES
            (
                :customer_id,
                :account_number,
                :first_name,
                :last_name,
                :full_name,
                :customer_initials,
                :gender,
                :date_of_birth,
                :age,
                :is_adult,
                :eligibility,
                :customer_segment,
                :phone_number,
                :email_domain,
                :duplicate_email,
                :account_status,
                :wallet_balance,
                :wallet_segment,
                :risk_level,
                :risk_flag,
                :created_at,
                :account_tenure_days,
                :customer_lifetime_stage,
                :valid_from,
                :valid_to,
                :is_current
            )
        """)

        conn.execute(
            dimension_insert,
            dimension_records,
        )

        logger.info(
            "SUCCESS | Customer dimension records inserted | records=%d",
            len(dimension_records),
        )

        checkpoint_insert = text("""
            INSERT INTO gold.customer_baseline_checkpoint
            (
                customer_id,
                baseline_event_sequence,
                baseline_run_id,
                captured_at
            )
            VALUES
            (
                :customer_id,
                :baseline_event_sequence,
                :baseline_run_id,
                :captured_at
            )
        """)

        checkpoint_insert_records = [
            {
                "customer_id": record["customer_id"],
                "baseline_event_sequence": record[
                    "baseline_event_sequence"
                ],
                "baseline_run_id": baseline_run_id,
                "captured_at": snapshot_at,
            }
            for record in checkpoint_records
        ]

        conn.execute(
            checkpoint_insert,
            checkpoint_insert_records,
        )

        logger.info(
            "SUCCESS | Customer baseline checkpoints inserted | "
            "records=%d",
            len(checkpoint_insert_records),
        )

    logger.info(
        "SUCCESS | Customer baseline transaction committed | "
        "run_id=%s | customers=%d",
        baseline_run_id,
        expected_customer_count,
    )

    return True


    
def finalize_customer_baseline(
    baseline_run_id,
    expected_customer_count,
):
    with analytics_engine.begin() as conn:

        # 1. Verify the baseline run.
        run = conn.execute(
            text("""
                SELECT
                    status,
                    expected_customer_count
                FROM gold.customer_baseline_run
                    WITH (UPDLOCK, HOLDLOCK)
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
                "Expected customer count does not match "
                "the baseline run."
            )

        # 2. Verify the complete baseline.
        verification = conn.execute(
            text("""
                SELECT
                    (
                        SELECT COUNT(*)
                        FROM gold.customer_baseline_checkpoint
                        WHERE baseline_run_id = :baseline_run_id
                    ) AS checkpoint_count,

                    (
                        SELECT COUNT(DISTINCT customer_id)
                        FROM gold.customer_baseline_checkpoint
                        WHERE baseline_run_id = :baseline_run_id
                    ) AS unique_checkpoint_count,

                    (
                        SELECT COUNT(*)
                        FROM gold.dim_customer
                    ) AS dimension_count,

                    (
                        SELECT COUNT(DISTINCT customer_id)
                        FROM gold.dim_customer
                    ) AS unique_dimension_count,

                    (
                        SELECT COUNT(*)
                        FROM gold.dim_customer
                        WHERE is_current = 1
                    ) AS current_dimension_count,

                    (
                        SELECT COUNT(*)
                        FROM gold.customer_baseline_checkpoint AS cp
                        WHERE cp.baseline_run_id = :baseline_run_id
                          AND NOT EXISTS (
                              SELECT 1
                              FROM gold.dim_customer AS dc
                              WHERE dc.customer_id = cp.customer_id
                                AND dc.is_current = 1
                          )
                    ) AS missing_current_dimension_count
            """),
            {"baseline_run_id": baseline_run_id},
        ).mappings().one()

        if (
            verification["checkpoint_count"] != expected_customer_count
            or verification["unique_checkpoint_count"] != expected_customer_count
            or verification["dimension_count"] != expected_customer_count
            or verification["unique_dimension_count"] != expected_customer_count
            or verification["current_dimension_count"] != expected_customer_count
            or verification["missing_current_dimension_count"] != 0
        ):
            raise ValueError(
                f"Baseline verification failed: {dict(verification)}"
            )

        # 3. Mark the baseline run as completed.
        updated_run_id = conn.execute(
            text("""
                UPDATE gold.customer_baseline_run
                SET
                    status = 'COMPLETED',
                    completed_at = SYSUTCDATETIME(),
                    loaded_customer_count = :loaded_customer_count
                OUTPUT INSERTED.baseline_run_id
                WHERE baseline_run_id = :baseline_run_id
                  AND status = 'IN_PROGRESS'
            """),
            {
                "baseline_run_id": baseline_run_id,
                "loaded_customer_count": expected_customer_count,
            },
        ).scalar_one_or_none()

        if updated_run_id is None:
            raise RuntimeError(
                "Baseline run status could not be updated."
            )
       

        # 4. Check whether the baseline control row exists.
        control_exists = conn.execute(
            text("""
                SELECT control_id
                FROM gold.customer_baseline_control
                    WITH (UPDLOCK, HOLDLOCK)
                WHERE control_id = 1
            """)
        ).scalar_one_or_none()

        # 5. Insert or update the authoritative baseline reference.
        if control_exists is None:
            conn.execute(
                text("""
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
                """),
                {"baseline_run_id": baseline_run_id},
            )
        else:
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

        logger.info(
            "SUCCESS | Customer baseline finalized | "
            "run_id=%s | customers=%d",
            baseline_run_id,
            expected_customer_count,
        )

    return True



def create_customer_baseline_run(expected_customer_count):

    if expected_customer_count <= 0:
        raise ValueError(
            "Expected customer count must be greater than zero."
        )

    baseline_run_id = uuid.uuid4()

    with analytics_engine.begin() as conn:

        # Prevent another baseline from starting while one is in progress.
        existing_run = conn.execute(
            text("""
                SELECT baseline_run_id
                FROM gold.customer_baseline_run
                    WITH (UPDLOCK, HOLDLOCK)
                WHERE status = 'IN_PROGRESS'
            """)
        ).scalar_one_or_none()

        if existing_run is not None:
            raise RuntimeError(
                f"Another baseline run is already in progress: "
                f"{existing_run}"
            )

        # Create the baseline run.
        baseline_run = conn.execute(
            text("""
                INSERT INTO gold.customer_baseline_run
                (
                    baseline_run_id,
                    status,
                    started_at,
                    expected_customer_count,
                    loaded_customer_count
                )
                OUTPUT
                    INSERTED.baseline_run_id,
                    INSERTED.started_at
                VALUES
                (
                    :baseline_run_id,
                    'IN_PROGRESS',
                    SYSUTCDATETIME(),
                    :expected_customer_count,
                    0
                )
            """),
            {
                "baseline_run_id": baseline_run_id,
                "expected_customer_count": expected_customer_count,
            },
        ).mappings().one()

    logger.info(
        "SUCCESS | Customer baseline run created | "
        "run_id=%s | expected_customers=%d | started_at=%s",
        baseline_run["baseline_run_id"],
        expected_customer_count,
        baseline_run["started_at"],
    )

    return (
        baseline_run["baseline_run_id"],
        baseline_run["started_at"],
    )


if __name__ == "__main__":

    baseline_run_id = "E47C0DCE-BA90-4DAE-B6AA-8F5655B0AE69"

    logger.info(
        "START | Customer baseline preparation | run_id=%s",
        baseline_run_id,
    )

    # 1. Retrieve the existing baseline run
    with analytics_engine.connect() as conn:
        baseline_run = conn.execute(
            text("""
                SELECT
                    baseline_run_id,
                    status,
                    expected_customer_count,
                    started_at
                FROM gold.customer_baseline_run
                WHERE baseline_run_id = :baseline_run_id
            """),
            {"baseline_run_id": baseline_run_id},
        ).mappings().one_or_none()

    if baseline_run is None:
        raise ValueError(
            "The specified customer baseline run does not exist."
        )

    if baseline_run["status"] != "IN_PROGRESS":
        raise ValueError(
            f"Baseline run is not IN_PROGRESS: "
            f"{baseline_run['status']}"
        )

    expected_customer_count = baseline_run[
        "expected_customer_count"
    ]

    # 2. Retrieve the production customer snapshot
    baseline_snapshot = get_customer_baseline_snapshot()

    snapshot_at = baseline_snapshot["snapshot_at"]

    customer_snapshot_list = baseline_snapshot[
        "customer_snapshot_list"
    ]
    # 3. Confirm production snapshot count matches the baseline run.
    if len(customer_snapshot_list) != expected_customer_count:
        raise ValueError(
            "Production snapshot customer count does not match "
            f"the baseline run. Expected {expected_customer_count}, "
            f"got {len(customer_snapshot_list)}."
        )

    # 4. Prepare customer records and event checkpoints
    customer_records, checkpoint_records = (
        prepare_customer_baseline_records(
            customer_snapshot_list
        )
    )

    # 5. Transform customer records
    transformed_customers = transform_customer_baseline(
        customer_records
    )

    # 6. Prepare dimension records using the snapshot timestamp
    dimension_records = prepare_customer_dimension_records(
        transformed_customers,
        snapshot_at,
    )

    # 7. Validate baseline records
    validate_customer_baseline_records(
        dimension_records,
        expected_customer_count,
    )

    # 8. Validate dimension schema
    validate_customer_dimension_schema(
        dimension_records
    )

    # 9. Confirm checkpoint count
    if len(checkpoint_records) != expected_customer_count:
        raise ValueError(
            "Checkpoint record count does not match "
            "the expected customer count."
        )

    # 10. Load dimension records and baseline checkpoints.
    load_customer_baseline(
        baseline_run_id=baseline_run_id,
        dimension_records=dimension_records,
        checkpoint_records=checkpoint_records,
        expected_customer_count=expected_customer_count,
        snapshot_at=snapshot_at,
    )

    # 11. Finalize the baseline run.
    finalize_customer_baseline(
        baseline_run_id=baseline_run_id,
        expected_customer_count=expected_customer_count,
    )
    logger.info(
        "SUCCESS | Customer baseline preparation completed | "
        "run_id=%s | snapshot_at=%s | customers=%d | checkpoints=%d",
        baseline_run_id,
        snapshot_at,
        len(dimension_records),
        len(checkpoint_records),
    )

    print("Baseline run ID:", baseline_run_id)
    print("Snapshot timestamp:", snapshot_at)
    print("Baseline status:", "COMPLETED")
    print("Expected customers:", expected_customer_count)
    print("Loaded dimension records:", len(dimension_records))
    print("Loaded checkpoint records:", len(checkpoint_records))

   
