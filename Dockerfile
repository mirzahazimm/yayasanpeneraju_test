# Use the official Airflow image as a base
FROM apache/airflow:2.5.1

# Install required Python libraries
RUN pip install --no-cache-dir \
    pandas \
    sqlalchemy \
    psycopg2 \
    google-cloud-storage \
    pyOpenSSL \
    cryptography

# Set the working directory inside the container
WORKDIR /opt/airflow

# Optional: Create the airflow user and set permissions
RUN useradd -m airflow && \
    mkdir -p ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/dags ${AIRFLOW_HOME}/plugins && \
    chown -R airflow:airflow ${AIRFLOW_HOME}

# Optional: Set the Airflow home directory for clarity
ENV AIRFLOW_HOME=/opt/airflow

# Optional: Generate a Fernet Key dynamically
RUN FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())") && \
    echo $FERNET_KEY > ${AIRFLOW_HOME}/.fernet_key

# Set the Airflow-specific environment variable for the Fernet Key from the generated file
ENV AIRFLOW__CORE__FERNET_KEY=$FERNET_KEY

# Copy your DAGs to the container (ensure you have the correct path to your DAGs folder)
COPY ./dags /opt/airflow/dags

# Set Airflow-specific environment variables
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor

# Switch to the airflow user
USER airflow

# Ensure that the required dependencies are installed and Airflow is configured properly
RUN pip install --no-cache-dir apache-airflow==2.5.1
