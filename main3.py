import os
from File_reads.file_reading import convert_to_parquet
from uploads_to_s3.upload_to_s3 import upload_parquet_files_to_s3
from  DB_inserts.db_insertion import insert_into_mysql_with_timestamp,read_parquet_from_s3, create_dynamic_model_with_timestamp
from  DB_inserts.db_insertion import get_db_connection, get_table_schema, mysql_to_python_type 
from dotenv import load_dotenv
import logging


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers= logging.FileHandler("file_conversion.log")
)

folder_path = os.getenv("LOCAL DIRECTORY")
bucket_name = os.getenv("S3_BUCKET")
s3_folder = os.getenv("S3_folder_path")
TABLE_NAME = os.getenv("table_name")

if __name__ == "__main__":
    parquet_files = []
    try:
        logging.info("file conversion module started")
        parquet_files.append(convert_to_parquet(folder_path))
        logging.info("file conversion module ended")
        upload_parquet_files_to_s3(parquet_files, bucket_name, s3_folder)
        table_data = read_parquet_from_s3(s3_folder)
        if table_data is None:
            logging.error("Failed to read parquet. Exiting.")
            exit(1)

        dynamic_model = create_dynamic_model_with_timestamp(TABLE_NAME)
        insert_into_mysql_with_timestamp(TABLE_NAME, dynamic_model, table_data)
        logging.info("insertion of data is successfull")
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
