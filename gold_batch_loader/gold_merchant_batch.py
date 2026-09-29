import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gold_batch_loader.gold_generic_batch_loader import generic_batch_loader
from gold_incremental_loader.gold_generic_incremental import DOMAIN_CONFIG
from gold_incremental_loader.gold_merchant_incremental_loader import gold_merchant_incremental_load
config = DOMAIN_CONFIG["merchant"]
table_name = config["table"]
gold_merchant_column_order = [
'merchant_id',
'merchant_code',
'merchant_name',
'category',
'segment',
'email',
'email_domain',
'duplicate_email',
'phone_number',
'city',
'state',
'location',
'account_number',
'merchant_status',
'is_active',
'created_at',
'merchant_tenure_days',
'tenure_category']


def gold_merchant_batch_loader():
    loader = generic_batch_loader(table_name=table_name,
                                  column_order= gold_merchant_column_order,
                                  transformed_data=gold_merchant_incremental_load(),
                                  domain="merchant",
                                  schema='gold.'
                                  )
    return loader

gold_merchant_batch_loader()
