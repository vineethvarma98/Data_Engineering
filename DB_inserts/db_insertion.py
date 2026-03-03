from dotenv import load_dotenv
import pyarrow.parquet as pq
import mysql.connector
from pydantic import BaseModel, ValidationError, create_model
from typing import Optional
import logging
import datetime
import boto3
from io import BytesIO

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


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def mysql_to_python_type(mysql_type: str):
    t = mysql_type.lower()
    if "int" in t:
        return Optional[int]
    elif "float" in t or "double" in t or "decimal" in t:
        return Optional[float]
    elif "date" in t or "time" in t:
        return Optional[str]
    else:
        return Optional[str]
    

def get_table_schema(table_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"DESCRIBE {table_name}")
    columns = cursor.fetchall()
    cursor.close()
    conn.close()
    return columns

def create_dynamic_model_with_timestamp(table_name):
    columns = get_table_schema(table_name)
    logging.info("table schema is retrieved")
    fields = {}
    for col in columns:
        col_name = col["Field"]
        py_type = mysql_to_python_type(col["Type"])
        fields[col_name] = (py_type, None)
    # Add ingestion timestamp column
    fields["ingested_at"] = (Optional[str], None)
    return create_model("DynamicModel", **fields)


def read_parquet_from_s3(s3_key):
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
        file_buffer = BytesIO(response["Body"].read())
        table = pq.read_table(file_buffer)
        return table
    except Exception as e:
        logging.error(f"Error reading parquet from S3: {e}")
        return None
    
def insert_into_mysql_with_timestamp(table_name, dynamic_model, table_data):

    try:

        conn = get_db_connection()
        cursor = conn.cursor()
        logging.info("database connection established")
        valid_rows = 0
        invalid_rows = 0

        for i in range(table_data.num_rows):
            row_dict = {name: table_data.column(name)[i].as_py() for name in table_data.schema.names}
            row_dict["ingested_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            try:
                validated = dynamic_model(**row_dict)
                placeholders = ", ".join(["%s"] * len(validated.__dict__))
                columns = ", ".join(validated.__dict__.keys())
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(validated.__dict__.values()))
                valid_rows += 1
            except ValidationError as ve:
                logging.warning(f"Row {i} validation error: {ve}")
                invalid_rows += 1
            except Exception as e:
                logging.error(f"Row {i} insert error: {e}")
                invalid_rows += 1

        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Inserted {valid_rows} valid rows, {invalid_rows} invalid rows.")
    except Exception as e:
        logging.critical(f"error occured while connecting to database: {e} ")

    

