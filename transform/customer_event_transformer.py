import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.pending_customer_event_retrieval_component import retrieve_and_validate_customer_events
from transform.customer_transformer_helper import (get_customer_age_details,
                                                   calculate_account_tenure,
                                                   get_full_name,
                                                   get_customer_initials,
                                                   get_email_domain,
                                                   get_wallet_segment,
                                                   get_risk_details,
                                                   clean_transform_value,
                                                   
                                                   MISSING_VALUES)

def transform_customer_events(fully_validated_event_records):
    event_list =[]
    for records in fully_validated_event_records:
        customer_snapshot  = records.get("customer_snapshot")
        event_metadata = records.get("event_metadata")
        effective_at = event_metadata.get("effective_at")
        date_of_birth = customer_snapshot.get("date_of_birth")
        created_at = customer_snapshot.get("created_at")
        first_name = customer_snapshot.get("first_name")
        last_name = customer_snapshot.get("last_name")
        email = customer_snapshot.get("email")
        wallet_balance = customer_snapshot.get("wallet_balance")
        account_status = customer_snapshot.get("account_status")
        customer_id = customer_snapshot.get("customer_id")
        account_number = customer_snapshot.get("account_number")
        gender = customer_snapshot.get("gender")
        phone_number = customer_snapshot.get("phone_number")
        clean_email = clean_transform_value(key="email",
                                                    val=email,
                                                    missing_values=MISSING_VALUES)
        clean_date_of_birth = clean_transform_value(key="date_of_birth",
                                                    val=date_of_birth,
                                                    missing_values=MISSING_VALUES)
        clean_created_at = clean_transform_value(key="created_at",
                                                    val=created_at,
                                                    missing_values=MISSING_VALUES)
        clean_wallet_balance = clean_transform_value(key="wallet_balance",
                                                    val=wallet_balance,
                                                    missing_values=MISSING_VALUES)
        clean_account_status = clean_transform_value(key="account_status",
                                                    val=account_status,
                                                    missing_values=MISSING_VALUES)
        clean_customer_id = clean_transform_value(key="customer_id",
                                                  val=customer_id,
                                                  missing_values=MISSING_VALUES)
        clean_account_number = clean_transform_value(key="account_number",
                                                     val=account_number,
                                                     missing_values=MISSING_VALUES)
        clean_first_name =  clean_transform_value(key="first_name",
                                                  val=first_name,
                                                  missing_values=MISSING_VALUES)
        clean_last_name = clean_transform_value(key="last_name",
                                                val=last_name,
                                                missing_values=MISSING_VALUES)
        clean_gender = clean_transform_value(key="gender",
                                             val=gender,
                                             missing_values=MISSING_VALUES)
        clean_phone_number = clean_transform_value(key="phone_number",
                                                   val=phone_number,
                                                   missing_values=MISSING_VALUES)

        
        customer_age_details = get_customer_age_details(date_of_birth=clean_date_of_birth,
                                 reference_date=effective_at)
        age, is_adult, eligibility, customer_segment = customer_age_details
        account_tenure = calculate_account_tenure(date_of_birth=clean_date_of_birth,
                                                  created_at=clean_created_at,
                                                  reference_date=effective_at)
        account_tenure_days,customer_lifetime_stage = account_tenure
        full_name = get_full_name(first_name=clean_first_name, last_name=clean_last_name)
        customer_initials = get_customer_initials(first_name=clean_first_name,
                                                  last_name=clean_last_name)
        email_domain = get_email_domain(email=clean_email)
        wallet_segment = get_wallet_segment(wallet_balance=clean_wallet_balance)
        risk_level, risk_flag = get_risk_details(account_status=clean_account_status,
                                                 wallet_balance=clean_wallet_balance)
        transformed_customer = customer_snapshot.copy()
        transformed_customer["customer_id"] = clean_customer_id
        transformed_customer["email"] = clean_email
        transformed_customer["date_of_birth"] = clean_date_of_birth
        transformed_customer["created_at"] = clean_created_at
        transformed_customer["first_name"] = clean_first_name
        transformed_customer["last_name"] = clean_last_name
        transformed_customer["wallet_balance"] = clean_wallet_balance
        transformed_customer["account_status"] = clean_account_status
        transformed_customer["gender"] = clean_gender
        transformed_customer["phone_number"] = clean_phone_number
        transformed_customer["account_number"] = clean_account_number
        transformed_customer["age"] = age
        transformed_customer["is_adult"] = is_adult
        transformed_customer["eligibility"] = eligibility
        transformed_customer["customer_segment"] = customer_segment
        transformed_customer["account_tenure_days"] = account_tenure_days
        transformed_customer["customer_lifetime_stage"] = customer_lifetime_stage
        transformed_customer["full_name"] = full_name
        transformed_customer["email_domain"] = email_domain
        transformed_customer["wallet_segment"] = wallet_segment
        transformed_customer["risk_level"] = risk_level
        transformed_customer["risk_flag"] = risk_flag
        transformed_customer["customer_initials"] = customer_initials
        event_dict = {"transformed_customer": transformed_customer,
                    "event_metadata": event_metadata
                }
        event_list.append(event_dict)
        
    return event_list