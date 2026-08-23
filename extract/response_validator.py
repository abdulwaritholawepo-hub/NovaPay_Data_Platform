import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from extract.customer_extractor import extract_customers
import logging
from config import logging_config
required_fields = ["customer_id", "first_name", "last_name", "phone_number", "email", "created_at", "date_of_birth", "gender", "account_status"]

logger = logging.getLogger(__name__)

def validate_customer_data():
    logger.info("Starting customer data validation")
    customer_data = extract_customers()
  
    if isinstance(customer_data, list):
        logger.info("Customer data is a list")
    else:
        logger.error("Customer data is not a list")
        raise  TypeError("Customer data is not a list")
    logger.info(
        "Customer data successfully extracted. Records received: %d",
        len(customer_data)
    )
    if not customer_data:
      logger.error("Extracted customer data is empty")
      raise ValueError("Extracted customer data is empty")
    logger.info("Customer data is not empty")
    
    for customer in customer_data:
        if isinstance(customer, dict):
          logger.info("Customer record is a dictionary")
        else:
          logger.error("Customer data is not a dictionary")
          raise TypeError("Customer data is not a dictionary")
        for field in required_fields:
          if field in customer:
           logger.info("%s is present in the customer data", field)
          else:
              logger.error("%s is not present in the customer data", field)
              raise ValueError(f"{field} is not present in the customer data")
        for key, value in customer.items():
          if value == "":
            logger.error("Customer %s has an empty value for field '%s'",
                         customer.get("customer_id"),
                         key)
            raise ValueError(
                f"Customer {customer.get('customer_id')} has an empty value for field '{key}'"
            )
          if value is None:
            logger.error("%s contains None values", key)
            raise ValueError(f"{key} contains None values")
           
    logger.info(
        "Customer data validation completed successfully. Records validated: %d",
        len(customer_data)
    )
    return customer_data


