import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.merchant_transformer_helper import MERCHANT_COLUMN_ORDER
from processing.batch_loader import generic_batch_loader
from transform.merchants_transformation import transform_merchants
from processing.incremental_loader import DOMAIN_CONFIG
config = DOMAIN_CONFIG["merchant"]
table_name = config["table"]
def batch_loader_merchants():
    return generic_batch_loader(batch_domain=table_name,
                                domain_column_order=MERCHANT_COLUMN_ORDER,
                                transformed_data=transform_merchants(),
                                domain="merchant")