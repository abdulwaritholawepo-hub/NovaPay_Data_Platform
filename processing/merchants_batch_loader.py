import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transform.merchant_transformer_helper import COLUMN_ORDER
from processing.batch_loader import generic_batch_loader
from transform.merchants_transformation import transform_merchants

def merchants_batch_loader():
    return generic_batch_loader(batch_domain="merchants",
                                domain_column_order=COLUMN_ORDER,
                                transformed_data=transform_merchants())