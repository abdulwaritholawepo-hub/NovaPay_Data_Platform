import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processing.incremental_loader import generic_incremental_loader
from transform.merchants_transformation import transform_merchants
def merchants_incremental_loader():
    return generic_incremental_loader(transformed_data=transform_merchants(),
                                      domain="merchant")