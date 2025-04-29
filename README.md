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
   AIRFLOW_UID=50000
   AIRFLOW_IMAGE_NAME=yayasanpeneraju_test
   AIRFLOW_WWW_USER_USERNAME=yayasanpeneraju
   AIRFLOW_WWW_USER_PASSWORD=yayasanpeneraju
   POSTGRES_USER=yayasanpeneraju
   POSTGRES_PASSWORD=yayasanpeneraju
   POSTGRES_DB=yayasanpeneraju
   REDIS_PASSWORD=yayasanpeneraju

