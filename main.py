import os
import boto3
import pandas as pd
import sqlalchemy
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# AWS/S3 Configuration
s3_bucket = os.getenv('S3_BUCKET')
s3_key = os.getenv('S3_KEY')

# RDS Configuration
rds_host = os.getenv('RDS_HOST')
rds_user = os.getenv('RDS_USER')
rds_password = os.getenv('RDS_PASSWORD')
rds_db = os.getenv('RDS_DB')
rds_table = os.getenv('RDS_TABLE')

# Glue Fallback Configuration
glue_db = os.getenv('GLUE_DB')
glue_table = os.getenv('GLUE_TABLE')
glue_s3_location = os.getenv('GLUE_S3_LOCATION')

# AWS Clients
s3 = boto3.client('s3')
glue = boto3.client('glue')

def download_csv_from_s3():
    print(f" Downloading s3://{s3_bucket}/{s3_key}")
    try:
        s3.download_file(s3_bucket, s3_key, 'people.csv')
        df = pd.read_csv('people.csv')
        print(" Successfully read CSV")
        return df
    except ClientError as e:
        print(f" Failed to read CSV from S3: {e}")
        raise

def upload_to_rds(df):
    print(f"🚀 Uploading to RDS table `{rds_table}`...")
    try:
        engine = sqlalchemy.create_engine(
            f"mysql+pymysql://{rds_user}:{rds_password}@{rds_host}/{rds_db}"
        )
        df.to_sql(rds_table, con=engine, if_exists='replace', index=False)
        print(" Upload to RDS successful.")
        return True
    except Exception as e:
        print(f" RDS Upload Failed: {e}")
        return False

def fallback_to_glue():
    print("⚠️Falling back to AWS Glue...")

    try:
        glue.create_table(
            DatabaseName=glue_db,
            TableInput={
                'Name': glue_table,
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'id', 'Type': 'int'},
                        {'Name': 'name', 'Type': 'string'},
                        {'Name': 'email', 'Type': 'string'}
                    ],
                    'Location': f"s3://{s3_bucket}/{glue_s3_location}",
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {'field.delim': ','}
                    }
                },
                'TableType': 'EXTERNAL_TABLE',
                'Parameters': {'classification': 'csv'}
            }
        )
        print(" AWS Glue fallback successful.")
    except glue.exceptions.AlreadyExistsException:
        print("⚠️Glue table already exists.")
    except Exception as e:
        print(f" Glue fallback failed: {e}")

def main():
    df = download_csv_from_s3()
    success = upload_to_rds(df)
    if not success:
        fallback_to_glue()

if __name__ == "__main__":
    main()
