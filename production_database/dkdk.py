import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from production_database.test_update_customer import run_tests
from production_database.seed_database import conn
run_tests(engine=conn, customer_id=1)