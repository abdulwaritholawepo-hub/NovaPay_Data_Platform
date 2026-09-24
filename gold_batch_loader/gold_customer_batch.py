import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gold_batch_loader.gold_generic_batch_loader import generic_batch_loader
from gold_incremental_loader.gold_generic_incremental import DOMAIN_CONFIG
from silver_query.silver_generic_query import generic_silver_query

silver_data = generic_silver_query("customers")
config = DOMAIN_CONFIG["customer"]
table_name = config["table"]
gold_customer_column_order = [
    
    'customer_id',
    'account_number',
    'first_name',
    'last_name',
    'full_name',
    'customer_initials',
    'gender',
    'date_of_birth',
    'age',
    'is_adult',
    'eligibility',
    'customer_segment',
    'phone_number',
    'email_domain',
    'duplicate_email',
    'account_status',
    'wallet_balance',
    'wallet_segment',
    'risk_level',
    'risk_flag',
    'created_at',
    'account_tenure_days',
    'customer_lifetime_stage',
    'valid_from',
    'valid_to',
    'is_current',
    ]
parameters = (
        'customer_id',
        'account_number',
        'first_name',
        'last_name',
        'full_name',
        'customer_initials',
        'gender',
        'date_of_birth',
        'age',
        'is_adult',
        'eligibility',
        'customer_segment',
        'phone_number',
        'email_domain',
        'duplicate_email',
        'account_status',
        'wallet_balance',
        'wallet_segment',
        'risk_level',
        'risk_flag',
        'created_at',
        'account_tenure_days',
        'customer_lifetime_stage',
        'sysdatetime()' ,
        'null',
        '1'
    )
def gold_customer_batch_loader():
    loader = generic_batch_loader(table_name=table_name,
                                   column_order= gold_customer_column_order,
                                   transformed_data= silver_data,
                                   domain="customer",
                                   schema='dbo.'
                                   )
    return loader
gold_customer_batch_loader()