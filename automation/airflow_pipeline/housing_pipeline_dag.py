from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import joblib
from twilio.rest import Client
from pymongo import MongoClient
import requests



# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'real_estate_pipeline',
    default_args=default_args,
    description='Real Estate Pipeline with Data Scraping, Cleaning, Training, and API Deployment',
    schedule_interval='@weekly',
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Task 1: Data Scraping


def scrape_data():
    subprocess.run(['python', 'automation/scrape/kijiji_scraper.py'])


scrape_task = PythonOperator(
    task_id='scrape_data',
    python_callable=scrape_data,
    dag=dag,
)

# Task 2: Clean and Store Data in MongoDB


def clean_and_store_data():
    subprocess.run(['python', 'automation/data_storage/mongo_seed.py'])


clean_store_task = PythonOperator(
    task_id='clean_and_store_data',
    python_callable=clean_and_store_data,
    dag=dag,
)

# Task 3: Train Model


def train_model():
    subprocess.run(['python', 'automation/model_training/training.py'])


train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

# Task 4: Restart API to Load New Model


def restart_api():
    print("restarted")


restart_api_task = PythonOperator(
    task_id='restart_api',
    python_callable=restart_api,
    dag=dag,
)

# Task 5: Send Notifications via Twilio

def send_notifications():
    # Define Flask API endpoint
    FLASK_API_URL = "http://localhost:5005/send-sms"

    # Make POST request to the Flask API
    requests.post(FLASK_API_URL)


send_notifications_task = PythonOperator(
    task_id='send_notifications',
    python_callable=send_notifications,
    dag=dag,
)


# Define task dependencies
scrape_task >> clean_store_task >> train_model_task >> restart_api_task >> send_notifications_task

