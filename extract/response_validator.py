import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from config import logging_config

logger = logging.getLogger(__name__)

def validate_extracts(extracts, domain, required_fields):
    logger.info("Starting %s data validation", domain)
    
  
    if isinstance(extracts, list):
        logger.info("%s data is a list", domain)
    else:
        logger.error("%s data is not a list", domain)
        raise  TypeError(f"{domain} data is not a list")
    logger.info(
        "%s data successfully extracted. Records received: %d",
        domain,
        len(extracts)
    )
    if not extracts:
      logger.error("Extracted %s data is empty", domain)
      raise ValueError(f"Extracted {domain} data is empty")
    logger.info("%s data is not empty", domain)
    
    for extract in extracts:
        if isinstance(extract, dict):
          logger.info("%s record is a dictionary", domain)
        else:
          logger.error("%s data is not a dictionary", domain)
          raise TypeError(f"{domain} data is not a dictionary")
        for field in required_fields:
          if field in extract:
           logger.info("%s is present in the %s data", field, domain)
          else:
              logger.error("%s is not present in the %s data", field, domain)
              raise ValueError(f"{field} is not present in the {domain} data")
        for key, value in extract.items():
          if value == "":
            logger.error(f"{domain} %s has an empty value for field '%s'",
                         extract.get(f"{domain}_id"),
                         key)
            raise ValueError(
                f"{domain} {extract.get(f'{domain}_id')} has an empty value for field '{key}'"
            )
          if value is None:
            logger.error("%s contains None values", key)
            raise ValueError(f"{key} contains None values")
           
    logger.info(
        "%s data validation completed successfully. Records validated: %d",
        domain,
        len(extracts)
    )
    return extracts

