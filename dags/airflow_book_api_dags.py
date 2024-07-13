# Importing module
import requests
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

# Function to fecth book data from API
def get_book_data_from_API(ti):
    api_url = 'https://openlibrary.org/subjects/programming.json'
    response = requests.get(api_url)
    book_data = response.json()
    ti.xcom_push(key = 'book_data', value=book_data)

def transform_data(ti):
    transformed_data = []
    book_data = ti.xcom_pull(key = 'book_data', task_ids = 'get_book_data_from_API')
    for book in book_data['works']:
        title = book['title']
        author = book['authors'][0]['name'] if 'authors' in book and book['authors'] else None
        subject = book['subject'][0]
        status = book['availability']['status'] if 'availability' in book and 'status' in book['availability'] else None
        borrow_availability = book['availability']['available_to_borrow'] if 'availability' in book and 'available_to_borrow' in book['availability'] else None
        publish_date = book['first_publish_year'] if 'first_publish_year' in book else None

        transformed_data.append((title, author, subject, status, borrow_availability, publish_date))
        ti.xcom_push(key='transformed_data', value=transformed_data)

def create_table():
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake-conn')
    create_table_query = """
    CREATE OR REPLACE TABLE  book_table (
        title STRING,
        author STRING,
        subject STRING,
        status STRING,
        borrow_availability BOOLEAN,
        publish_date NUMBER
    )
    """
    snowflake_hook.run(create_table_query)

def insert_to_snowflake(ti):
    transformed_data = ti.xcom_pull(key='transformed_data', task_ids='transform_data')
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake-conn')

    insert_stmt = """
    INSERT INTO PROJECTS_DB.PUBLIC.book_table (title, author, subject, status, borrow_availability, publish_date) VALUES (%s, %s, %s, %s, %s, %s) """

    for record in transformed_data:
        snowflake_hook.run(insert_stmt, parameters=record)

# Define the default arguments
default_args = {
    'owner': 'zainal',
    'depands_on_past':False,
    'email_on_failure':False,
    'emial_on_retry':False,
    'retries':1,
    'retry_delay':timedelta(minutes=5)
}

# Define the DAG
with DAG(
    'airflow_book_api_pipeline',
    default_args=default_args,
    description='a data pipeline to fect book data from API and insert into Snowflake AI Cloud Data Warehouse',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024,1,1),
    catchup=False
) as dag:
    create_table_tasl = PythonOperator(
        task_id='create_table',
        python_callable=create_table,
        provide_context=True
    )

    get_book_data = PythonOperator(
        task_id='get_book_data_from_API',
        python_callable=get_book_data_from_API,
        provide_context=True
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        provide_context=True
    )

    load_to_snowflake = PythonOperator(
        task_id='insert_to_snowflake',
        python_callable=insert_to_snowflake,
        provide_context=True
    )

    # Setting the task dependencises
    create_table_tasl >> get_book_data >> transform >> load_to_snowflake