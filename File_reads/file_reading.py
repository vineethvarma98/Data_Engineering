from dotenv import load_dotenv
import os
import json
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pv
import pyarrow.orc as orc
import logging
import datetime


load_dotenv()

folder_path = os.getenv("LOCAL_DIRECTORY")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers= logging.FileHandler("file_conversion.log")
)

logger = logging.getLogger(__name__)

def convert_to_parquet(file_directory):
    try :
        table = None
        today = datetime.date.today()
        for files in os.listdir(file_directory):
            file_path = os.path.join(file_directory,files)
            #print(files)
            ctime = os.path.getctime(file_path)
            file_date = datetime.date.fromtimestamp(ctime)
            if file_date == today :
                file_type = files.split(".")[1]
                if file_type == "parquet":
                        logger.info(f"already in parquet skipping conversion {file_path}")
                elif file_type == ".csv":
                        table = pv.read_csv(file_path)
                        logger.info(f"CSV loaded: {file_path}")
                elif file_type == ".json":
                        with open(file_path, "r") as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            table = pa.Table.from_pylist(data)
                            logger.info(f"JSON loaded: {file_path}")
                        else:
                            raise ValueError("JSON must be list of objects")
                elif file_type == ".orc" :
                        with open(file_path, "rb") as f:
                            reader = orc.ORCFile(f)
                        table = reader.read()
                        logger.info(f"ORC loaded: {file_path}")
                else:
                        print("Unsupported file format")
                        logger.warning(f"Unsupported file type: {file_path}")

                output = file_path.split(".")[0] + ".parquet"
                pq.write_table(table, output, compression="snappy")
                logger.info(f"Converted to Parquet: {file_path} → {output}")
                return output

    except Exception as e:
        logger.error(f"error in processing the file : {file_path} : {e}")
        return None 



