import os
import pandas as pd

def transform_data(local_file_path):
    try:
        # Make sure the file path is correct for local testing
        file_path = os.path.join(local_file_path, 'sales_data_sample.csv') #from data/sales_data_sample.csv
        
        # Read the CSV file into a DataFrame with specified encoding
        df = pd.read_csv(file_path, encoding='ISO-8859-1')

        # Data Cleaning: Example - Fill missing values with 'NA' for STATE and POSTALCODE
        df['STATE'].fillna('NA', inplace=True)
        df['POSTALCODE'].fillna('NA', inplace=True)

        # Standardize product category names to uppercase
        df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')
        df['ORDERDATE'] = df['ORDERDATE'].dt.strftime('%m/%d/%Y')
        df['PRODUCTLINE'] = df['PRODUCTLINE'].str.upper()

        # Data Aggregation by Product Category
        aggregated_df = df.groupby('PRODUCTLINE').agg(
            total_sales_amount=pd.NamedAgg(column='SALES', aggfunc='sum'),
            num_transactions=pd.NamedAgg(column='SALES', aggfunc='count')
        ).reset_index()

        # You can print or return the aggregated dataframe for local testing
        print(aggregated_df)
        return aggregated_df
    
    except Exception as e:
        print(f"Error during transformation: {e}")
        return None

# Test the function locally with the appropriate file path
local_file_path = "C:/Users/User/Documents/Data Analysis Projects/Data Engineering/Yayasan Peneraju Assessment/data/"  # Change to your local directory path
aggregated_data = transform_data(local_file_path)

# Optionally save the transformed data locally for further use
if aggregated_data is not None:
    aggregated_data.to_csv(os.path.join(local_file_path, 'aggregated_sales_data.csv'), index=False)
