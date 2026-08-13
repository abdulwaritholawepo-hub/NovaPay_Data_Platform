from transform.customer_transformer import transform_customers
from transform.transform_helpers import COLUMN_ORDER
from sqlalchemy import text

transformed_customer_data = transform_customers()
def batch_customer_loader(batch_size, start):
    customers = transformed_customer_data
    customer_length = len(customers)
    customer_batch_list = []

    for customer in range(start, customer_length, batch_size):
        customer_batch = customers[customer:customer + batch_size]
        customer_batch_list.append(customer_batch)
    return customer_batch_list

def customer_column():
    columns = ", ".join(COLUMN_ORDER)


    parameters = ", ".join(f":{column}" for column in COLUMN_ORDER)

    insert_customers = text(f"""
    INSERT INTO customers({columns})
    VALUES({parameters})
    """)
    return insert_customers