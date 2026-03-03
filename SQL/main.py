from dotenv import load_dotenv
import requests
import psycopg2
from datetime import datetime
from psycopg2.extras import execute_batch
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("alert_etl.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

OPEN_API = OPEN_ALERTS_API
HISTORY_APIs = HISTORY_API

DB_CONFIG = {
    "host": host,
    "port": port,
    "database": database,
    "user": user,
    "password": password
}

def get_data_from_open_api():
    try:
        logger.info("fetching all the alerts")
        response = requests.get(OPEN_API,timeout= 30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"unable to fetch the results {e}")
        return []

def get_historical_data(start_date, end_date):
    try:
        logger.info(f"fetching all the historical alerts from {start_date} to {end_date}")
        parameters = {"start_date" : start_date, "end_date" : end_date}
        response = requests.get(HISTORY_APIs, params= parameters,timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"unable to fetch the records {e}")
        return []

def db_insert_alerts(alerts):
    if not  alerts:
        logger.info("no alerts to insert")
        return
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        INSERT_QUERY = """
                    insert into alerts(
                    alert_id,
                    title,
                    severity,
                    status,
                    source_system,
                    created_at,
                    updated_at,
                    resolved_at,
                    ingestion_time
                    )  
                    values(
                    VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s)
                    ON CONFLICT (alert_id) DO NOTHING;
                    )  
                    """
        
        records = []

       
        for alert in alerts:  
                alert_id = int(alert["alert_id"])
                title = alert["title"]
                severity = alert["severity_id"]
                status = alert["status_id"]
                source_system = alert["source_system"]
                source_id = int(alert["source_id"])

                created_at = datetime.fromisoformat(alert["created_at"]).date()
                updated_at = datetime.fromisoformat(alert["updated_at"]).date()
                resolved_at = (
                    datetime.fromisoformat(alert["resolved_at"]).date()
                    if alert.get("resolved_at")
                    else None
                )
                ingestion_time = datetime.now()

        records.append((
                alert_id, title,severity,status,source_system,source_id,created_at.date(),updated_at.date(),resolved_at.date(),ingestion_time
            ))
        execute_batch(cursor, INSERT_QUERY, records, page_size=100)

        conn.commit()
        logger.info(f"Inserted {len(records)} records successfully.")

    except Exception as e:
            logger.error(f"Database insert failed: {e}")
    finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()


if __name__ == "__main__":
    logger.info("Starting the Process")

    try:
        open_alerts = get_data_from_open_api()
        history_alerts = get_historical_data(START_DATE, END_DATE)

        all_alerts = open_alerts + history_alerts

        db_insert_alerts(all_alerts)

        logger.info("Alert  Process Completed Successfully")

    except Exception as e:
        logger.critical(f"Fatal error in  process: {e}")