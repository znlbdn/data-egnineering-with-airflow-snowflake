# Data Engineering with Airflow and Snowflake Running on CodeSpace

## What is Apache Ariflow?

Apache Airflow is an open-source platform designed to programmatically author, schedule, and monitor complex workflows. It allows users to define tasks and dependencies using Python, enabling dynamic pipeline creation. Airflow's web-based UI provides powerful insights into running and completed workflows. It is widely used for orchestrating data engineering, machine learning, and ETL processes.

Read more : https://airflow.apache.org/docs/

## What is GitHub CodeSpace?

GitHub Codespaces is a cloud-based development environment that provides instant, configurable, and on-demand development environments. Integrated directly into GitHub, it allows developers to code, build, test, and collaborate from any device.

To setting up the GitHub CodeSpace, you can rever this link to see the full guidlance

Read more : https://github.com/znlbdn/airflow-codespace

## Data Architecture Diagram

![snowflake_airflow_arch](https://github.com/znlbdn/data-egnineering-with-airflow-snowflake/blob/main/assets/airflow-snow-arch.png)

Tech in used wihtin this projects are:

1. Snowflake
2. Airflow
3. GitHub CodeSpace

## Configure the Snowflake Database

First, you need to setting the database and define all credential that use to configure the Snowflake connection within Airflow

```
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;

CREATE DATABASE IF NOT EXISTS PROJECTS_DB;
```

Define all the credential that use to make connection including => username, password, schema, database, role, region and your snowflake account

## Configure the Snowflake Conneciton within Airflow

Go to the Airflow UI and then clcik on the admin button then select connection. Add new connection and select snowflake.

![snowflake_conn_airflow](https://github.com/znlbdn/data-egnineering-with-airflow-snowflake/blob/main/assets/snowflake-1.png)

## Creating DAG

DAG (Directed Acyliy Graph) represents a sets of task including dependencies. Within DAG, we also define a task, task dependencies, operator, and scheduler. Let's create our DAG pipeline that extract data from API and loading to the Snowflake AI Cloud Data Warehouse.

- Define the operator, python library and snowflake provider

In this project, PythonOperator is used to define the task within a workflow.

```
import requests
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
```

- Define the task function that

Task can be define as how to execute the operator within the context of DAG

```
def get_book_data_from_API(ti):
    api_url = 'https://openlibrary.org/subjects/programming.json'
    response = requests.get(api_url)
    book_data = response.json()
    ti.xcom_push(key = 'book_data', value=book_data)
```

The first task is define to get data from API that define in the api_url varibale then convert ot json format. ti.xcom_push is s a method used to share data between tasks.

```
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
```

Then, define the transformation task that store stroe extracted data to a list in the transformed_data varibale. Then using the same method to share the data to the next task.

```
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
```

Then, define a task that creating a table within Snowflake. Using the Snowflake connection that have been defined before.

```
def insert_to_snowflake(ti):
    transformed_data = ti.xcom_pull(key='transformed_data', task_ids='transform_data')
    snowflake_hook = SnowflakeHook(snowflake_conn_id='snowflake-conn')

    insert_stmt = """
    INSERT INTO PROJECTS_DB.PUBLIC.book_table (title, author, subject, status, borrow_availability, publish_date) VALUES (%s, %s, %s, %s, %s, %s) """

    for record in transformed_data:
        snowflake_hook.run(insert_stmt, parameters=record)
```

Lastly, define the task that store the data to the table in Snowflake.

- Define the default Argument and DAG

First, define the defualt argument indlucidng the owner, emial on failure and etc.

```
default_args = {
    'owner': 'zainal',
    'depands_on_past':False,
    'email_on_failure':False,
    'emial_on_retry':False,
    'retries':1,
    'retry_delay':timedelta(minutes=5)
}
```

Then, define the DAG as shown below including the name of DAG that show in Airflow UI, schedule, description of DAG and the task.

```
with DAG(
    'airflow_book_api_pipeline',
    default_args=default_args,
    description='a data pipeline to fect book data from API and insert into Snowflake AI Cloud Data Warehouse',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024,1,1),
    catchup=False
) as dag:
    create_table_task = PythonOperator(
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
```

- Lastly, define the task dependecies that used to ordering the task and flow execetion.

```
create_table_task >> get_book_data >> transform >> load_to_snowflake
```

This mean that the create table task will execute first then extract data from api, transorm data and load to snowflake.

![snowflake_airflow_arch](https://github.com/znlbdn/data-egnineering-with-airflow-snowflake/blob/main/assets/api-snowflake-data.png)

![snowflake_airflow_viz](https://github.com/znlbdn/data-egnineering-with-airflow-snowflake/blob/main/assets/viz-airflow-snowflake.png)
