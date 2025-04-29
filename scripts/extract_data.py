from google.cloud import storage
import os
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# GCS configuration
BUCKET_NAME = 'yayasan_peneraju_bucket-1'  # Replace with your GCS bucket name
LOCAL_FILE_PATH = 'H:/My Drive/Data Engineering/Yayasan Peneraju Assessment/fromGCS' #need to update own local path

# Initialize GCS client
storage_client = storage.Client()

def download_csv_files_from_gcs(bucket_name, local_file_path):
    try:
        # Access the GCS bucket
        bucket = storage_client.get_bucket(bucket_name)

        # List all CSV files in the bucket
        blobs = bucket.list_blobs()

        # Filter CSV files
        csv_files = [blob for blob in blobs if blob.name.endswith('.csv')]

        if not csv_files:
            logger.error("No CSV files found in the bucket.")
            return

        # Download each CSV file to local storage
        for blob in csv_files:
            local_file_path_full = os.path.join(local_file_path, blob.name.split('/')[-1])
            blob.download_to_filename(local_file_path_full)
            logger.info(f"Downloaded {blob.name} from GCS to {local_file_path_full}")

    except Exception as e:
        logger.error(f"Error downloading files from GCS: {e}")

# Example usage
if __name__ == "__main__":
    download_csv_files_from_gcs(BUCKET_NAME, LOCAL_FILE_PATH)
