import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import api_config
from api.api_client import get_data_from_api


def get_transaction_data():
    return get_data_from_api(url=api_config.transaction_url,
                             timeout=api_config.timeout,
                             maximum_retries=api_config.maximum_retries
                             )