import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import logging
from config import logging_config
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_data_from_api(url, timeout, maximum_retries):
 
    for attempts in range(1, maximum_retries + 1):
        try:
            response = requests.get(url, timeout=timeout )
        
            response.raise_for_status()
            logger.info("Request successful")
            data = response.json()
            return data
        except requests.exceptions.HTTPError as http_error:
            status_code = http_error.response.status_code
            if 500 <= status_code <= 599:
                if attempts == maximum_retries:
                    logger.error("Maximum retries reached")
                    raise http_error
                else:
                    wait_time = attempts**2
                    logger.warning("Retrying in %d seconds", wait_time)
                    time.sleep(wait_time)
            else:
                logger.error("HTTP error: %s", status_code)
                raise http_error
                
            
            
        except  (
            requests.exceptions.RequestException,)as err: 
            last_exception = err
            error_type = type(last_exception).__name__
            logger.error(f"{error_type} occurred: {last_exception}")
            if attempts == maximum_retries:
                logger.error("Maximum retries reached")
                raise last_exception
                
            else:
                wait_time = attempts**2
                logger.warning("Retrying in %d seconds", wait_time)
                time.sleep(wait_time)

