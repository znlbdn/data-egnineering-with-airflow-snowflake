# Running Apache Airflow on GitHub Codespace

## What is Apache Ariflow?
Apache Airflow is an open-source platform designed to programmatically author, schedule, and monitor complex workflows. It allows users to define tasks and dependencies using Python, enabling dynamic pipeline creation. Airflow's web-based UI provides powerful insights into running and completed workflows. It is widely used for orchestrating data engineering, machine learning, and ETL processes.

Read more : https://airflow.apache.org/docs/

## What is GitHub CodeSpace?
GitHub Codespaces is a cloud-based development environment that provides instant, configurable, and on-demand development environments. Integrated directly into GitHub, it allows developers to code, build, test, and collaborate from any device.

## Seting up the Github Repository
- Create a new repository or fork this repository
- Create a docker file that contain the airflow configuration
- Create a github codespace with 2-core machine type (click the 3 dots button and create with options)
- Run the following command to make a dags, logs, plugins and config directory
  
  ```
  mkdir -p ./dags ./logs ./plugins ./config
  echo -e "AIRFLOW_UID=$(id -u)" > .env
  ```
- Run the following command to initialize the airflow

  ```
  docker-compose up airflow-init
  ```
- Run the following command to start ariflow service on your docker

  ```
  docker-compose up
  ```
- Acces the port on your web browser to see the airflow UI

  ```
  https://your-codespace-instances.app.github.dev:8080/home
  ```

  please remove the :8080

  ```
  https://your-codespace-instances.app.github.dev/home
  ```
- Login with the default credentail

  ```
  username : airflow
  password : airflow
  ```
