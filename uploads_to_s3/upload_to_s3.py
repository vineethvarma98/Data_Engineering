import boto3
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers= logging.FileHandler("file_conversion.log")
)

def upload_parquet_files_to_s3(parquet_files, bucket_name, s3_folder="parquet"):
    try:
        logger.info(f"connection established to s3")
        for file_path in parquet_files:
            upload_to_s3(file_path, bucket_name, s3_folder)
            logger.info(f"file uploaded to s3")

    except Exception as e:
        logger.critical(f"unable to upload to s3: {file_path}")