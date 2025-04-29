# ETL & Data Pipeline with Airflow and Python

## 📖 Overview
This project implements a simplified ETL pipeline that:
1. **Extracts** daily sales CSVs from a GCS bucket  
2. **Transforms** and aggregates by product category  
3. **Loads** into a PostgreSQL data warehouse  
4. **Validates** row counts as a data-quality check  

All steps are orchestrated in an Airflow DAG (`dags/etl_pipeline.py`) scheduled to run once per day.

---

## 📋 Prerequisites

1. **Docker & Docker Compose** installed (v20+).  
2. A **Google Cloud service-account JSON** key with Storage Object Viewer permissions.  
3. A local folder for your GCS key (e.g. `~/keys/etl-gcs.json`).  
4. A `.env` file in the project root, containing:
   ```dotenv
   POSTGRES_USER=yayasanpeneraju
   POSTGRES_PASSWORD=yayasanpeneraju
   POSTGRES_DB=yayasanpeneraju
   AIRFLOW_IMAGE_NAME=apache/airflow:2.5.1
