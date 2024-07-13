# Data Engineering with Airflow and Snowflake Running on CodeSpace

## What is Apache Ariflow?

Apache Airflow is an open-source platform designed to programmatically author, schedule, and monitor complex workflows. It allows users to define tasks and dependencies using Python, enabling dynamic pipeline creation. Airflow's web-based UI provides powerful insights into running and completed workflows. It is widely used for orchestrating data engineering, machine learning, and ETL processes.

Read more : https://airflow.apache.org/docs/

## What is GitHub CodeSpace?

GitHub Codespaces is a cloud-based development environment that provides instant, configurable, and on-demand development environments. Integrated directly into GitHub, it allows developers to code, build, test, and collaborate from any device.

## Seting up the Github Repository

To setting up the GitHub CodeSpace, you can rever this link to see the full guidlance

Read more : https://github.com/znlbdn/airflow-codespace

## Data Architecture Diagram

Tech in used wihtin this projects are:

1. Snowflake
2. Airflow

## Configure the Snowflake Database

First, you need to setting the database and define all credential that use to configure the Snowflake connection within Airflow

```
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;

CREATE DATABASE IF NOT EXISTS PROJECTS_DB;
```

Define all the credential that use to make connection including => username, password, schema, database, role, region and your snowflake account

## Configure the Conneciton in Airflow

Go to the Airflow UI and then clcik on the admin button then select connection. Add new connection and select snowflake.

![snowflake_conn_airflow](https://github.com/znlbdn/data-egnineering-with-airflow-snowflake/blob/main/assets/snowflake-1.png)
