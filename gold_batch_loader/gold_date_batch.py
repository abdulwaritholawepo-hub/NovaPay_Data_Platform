import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import text
from analytics_database.analytics_DB_connection import analytics_database_engine_connection
from gold_incremental_loader.gold_generic_incremental import gold_generic_incremental_loader
import time
import logging
from config import logging_config
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError, OperationalError, DBAPIError
import datetime as dt
import itertools as it

logger = logging.getLogger(__name__)
engine = analytics_database_engine_connection()
logger.info("Analytics database engine created successfully")
date_column_order =[
    'full_date',
    'day',
    'day_name',
    'day_of_week',
    'week_of_year',
    'month',
    'month_name',
    'quarter',
    'quarter_name',
    'year',
    ]

def date_batch_loader():

    columns = ", ".join(date_column_order)
    parameters = ", ".join(
        f":{column}" for column in date_column_order
    )
    
    start_date = dt.date.fromisoformat('2025-01-01')
    end_date = dt.date.fromisoformat('2027-12-31')

    date_list = []
    date_list.append('2025-01-01')
    while start_date < end_date:
        
        start_date += dt.timedelta(days=1)
        full_date = dt.date.strftime(start_date, "%Y-%m-%d")
        day_number = dt.date.strftime(start_date,"%d")
        day_name = dt.date.strftime(start_date, "%A")
        day_of_week = dt.date.isoweekday(start_date)
        week_of_year = dt.date.isocalendar(start_date).week
        month_number = dt.date.strftime(start_date, "%m")
        month_name = dt.date.strftime(start_date, "%B")
        quarter_number = (start_date.month -1) // 3+1
        quarter_name = f"Q{quarter_number}"
        year = dt.date.strftime(start_date, "%Y")
        
        date_list.append(start_date)
        
        if start_date == end_date:
            break
    
    
    field_list = []
    
    for date in date_list:
        date_field = []
        date= dt.datetime.fromisoformat(str(date))
         
        full_date = dt.datetime.strftime(date, "%Y-%m-%d")
        date_field.append(full_date)
        day_number = dt.datetime.strftime(date,"%d")
        date_field.append(day_number)
        day_name = dt.datetime.strftime(date, "%A")
        date_field.append(day_name)
        day_of_week = dt.datetime.isoweekday(date)
        date_field.append(day_of_week)
        week_of_year = dt.datetime.isocalendar(date).week
        date_field.append(week_of_year)
        month_number = dt.datetime.strftime(date, "%m")
        date_field.append(month_number)
        month_name = dt.datetime.strftime(date, "%B")
        date_field.append(month_name)
        quarter_number = (date.month - 1) // 3+1
        date_field.append(quarter_number)
        quarter_name = f"Q{quarter_number}"
        date_field.append(quarter_name)
        year = dt.datetime.strftime(date, "%Y")
        date_field.append(year) 

        field_list.append(date_field)
        
    dict_insert_list = []
    with engine.begin() as conn:
        results= conn.execute(text("""
        SELECT full_date
        FROM gold.dim_date
        """)).scalars().all()
        
    
    for insert_data in field_list:
        
        if dt.datetime.fromisoformat(str(insert_data[0])) not in results:
            dict_insert = { 
                    column_order: insert
                    for insert, column_order in it.zip_longest(insert_data, date_column_order)
                }
            dict_insert_list.append(dict_insert)
   
 
    if dict_insert_list is None or not dict_insert_list:
        print("empty dict insert list")
    else:
        insert_records = text(f"""
            INSERT INTO gold.dim_date
            (
        
                {columns}
            )
            VALUES
            (

            {parameters}
            )
        """)
        with engine.begin() as  conn:
            insert_batch = conn.execute(insert_records, dict_insert_list)
            print("insert completed")
        return insert_batch
date_batch_loader()