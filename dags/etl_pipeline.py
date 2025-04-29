from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from google.cloud import storage
import os
import pandas as pd
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# Set up logging for the DAG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GCS configuration: these variables need to be set for GCS authentication
BUCKET_NAME = 'yayasan_peneraju_bucket-1'  # Name of the GCS bucket
LOCAL_FILE_PATH = '/opt/airflow/data/'  # Local path to store the downloaded files
GCS_KEY_FILE_PATH = '/opt/airflow/gcs_key.json'  # Path to the GCS service account key

# Initialize GCS client with the provided service account key
storage_client = storage.Client.from_service_account_json(GCS_KEY_FILE_PATH)

def download_csv_files_from_gcs(bucket_name, local_file_path):
    """
    Downloads CSV files from a specified Google Cloud Storage bucket
    and saves them to a local directory.
    """
    try:
        bucket = storage_client.get_bucket(bucket_name)  # Access the GCS bucket
        blobs = bucket.list_blobs()  # List all objects (files) in the bucket
        csv_files = [b for b in blobs if b.name.endswith('.csv')]  # Filter out CSV files

        # If no CSV files are found, log an error and exit
        if not csv_files:
            logger.error("No CSV files found in the bucket.")
            return

        # Download each CSV file to the local path
        for blob in csv_files:
            dest = os.path.join(local_file_path, blob.name.split('/')[-1])  # Define the local path
            blob.download_to_filename(dest)  # Download the file
            logger.info(f"Downloaded {blob.name} to {dest}")  # Log successful download

    except Exception as e:
        logger.error(f"Error downloading files from GCS: {e}")
        raise  # Re-raise the error for downstream handling


def transform_data(local_file_path):
    """
    Transforms the data by cleaning missing values, standardizing date formats,
    and aggregating sales data by product category.
    """
    try:
        file_path = os.path.join(local_file_path, 'sales_data_sample.csv')  # Path to the input CSV file
        df = pd.read_csv(file_path, encoding='ISO-8859-1') # Read the CSV file into a DataFrame

        # Data Cleaning: Fill missing values in STATE and POSTALCODE columns with 'NA'
        df['STATE'].fillna('NA', inplace=True)
        df['POSTALCODE'].fillna('NA', inplace=True)

        # Standardize date format for the 'ORDERDATE' column
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')
        df['ORDERDATE'] = df['ORDERDATE'].dt.strftime('%m/%d/%Y')

        # Standardize product category names to uppercase
        df['PRODUCTLINE'] = df['PRODUCTLINE'].str.upper()

        # Data Aggregation by Product Category: Calculate total sales amount and number of transactions
        aggregated_df = df.groupby('PRODUCTLINE').agg(
            total_sales_amount=pd.NamedAgg(column='SALES', aggfunc='sum'),
            num_transactions=pd.NamedAgg(column='SALES', aggfunc='count')
        ).reset_index()  # Reset index after aggregation

        # Save the aggregated data to a new CSV file
        out_path = os.path.join(local_file_path, 'aggregated_sales_data.csv')
        aggregated_df.to_csv(out_path, index=False)
        logger.info(f"Transformed data saved to {out_path}")  # Log successful transformation
        return out_path  # Return the path of the transformed data

    except Exception as e:
        logger.error(f"Error during data transformation: {e}")
        raise  # Re-raise the error for downstream handling


def load_data_to_postgres(transformed_file_path):
    """
    Loads the transformed data from a CSV file into PostgreSQL database.
    """
    try:
        df = pd.read_csv(transformed_file_path)  # Read the transformed data into a DataFrame

        # Get PostgreSQL connection details from environment variables
        pg_user = os.getenv("POSTGRES_USER")
        pg_pass = os.getenv("POSTGRES_PASSWORD")
        pg_host = 'postgres'  # Postgres service in Docker
        pg_db = os.getenv("POSTGRES_DB")
        pg_port = '5432'

        # Construct the PostgreSQL connection string
        conn_str = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

        # Create the engine for PostgreSQL connection using SQLAlchemy
        engine = create_engine(conn_str)

        # Load the data into PostgreSQL (replace table if it exists)
        df.to_sql('sales_data', engine, if_exists='replace', index=False)
        logger.info(f"Loaded {len(df)} rows into {pg_db}.sales_data")  # Log successful load

    except Exception as e:
        logger.error(f"Error during data loading to PostgreSQL: {e}")
        raise  # Re-raise the error for downstream handling


def row_count_validation():
    """
    Performs a basic data quality check: Ensures that the sales_data table in PostgreSQL
    is not empty.
    """
    pg_user = os.getenv("POSTGRES_USER")
    pg_pass = os.getenv("POSTGRES_PASSWORD")
    pg_host = 'postgres'
    pg_db = os.getenv("POSTGRES_DB")
    pg_port = '5432'

    # Construct the PostgreSQL connection string
    conn_str = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    engine = create_engine(conn_str)

    try:
        # Query the count of rows in the 'sales_data' table
        with engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM sales_data")
            count = result.scalar()

        # Validate the row count
        if count == 0:
            raise ValueError("Data quality check failed: sales_data table is empty")
        logger.info(f"Data quality check passed: {count} rows in sales_data")  # Log successful validation

    except Exception as e:
        logger.error(f"Error during data quality check: {e}")
        raise  # Re-raise the error for downstream handling


# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 30),  # Start date for the DAG
    'retries': 1,  # Number of retries on failure
    'retry_delay': timedelta(minutes=5),  # Delay between retries
}

# Define the DAG
dag = DAG(
    'etl_pipeline',  # Name of the DAG
    default_args=default_args,
    description='Daily sales ETL pipeline',
    schedule_interval='@daily',  # Schedule to run the DAG daily
    catchup=False,  # Do not backfill previous runs
)

# Define the tasks in the DAG

# Task 1: Download data from GCS
download_task = PythonOperator(
    task_id='download_data_from_gcs',  # Task ID
    python_callable=download_csv_files_from_gcs,  # Function to call
    op_args=[BUCKET_NAME, LOCAL_FILE_PATH],  # Arguments to pass to the function
    dag=dag,  # DAG the task belongs to
)

# Task 2: Transform the downloaded data
transform_task = PythonOperator(
    task_id='transform_data',  # Task ID
    python_callable=transform_data,  # Function to call
    op_args=[LOCAL_FILE_PATH],  # Arguments to pass to the function
    dag=dag,  # DAG the task belongs to
)

# Task 3: Load transformed data to PostgreSQL
load_task = PythonOperator(
    task_id='load_data_to_postgres',  # Task ID
    python_callable=load_data_to_postgres,  # Function to call
    op_args=["{{ ti.xcom_pull(task_ids='transform_data') }}"],  # Get transformed file path from XCom
    dag=dag,  # DAG the task belongs to
)

# Task 4: Perform data quality check
quality_check = PythonOperator(
    task_id='row_count_validation',  # Task ID
    python_callable=row_count_validation,  # Function to call
    dag=dag,  # DAG the task belongs to
)

# Set task dependencies: Define the execution order of tasks
download_task >> transform_task >> load_task >> quality_check
