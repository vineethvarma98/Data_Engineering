#data frame and data base schema validation using pydantic library
import pandas as pd
from sqlalchemy import create_engine, inspect
from pydantic import BaseModel, ValidationError, create_model
from typing import Optional

username = "mine"
password = "root"
host = "localhost"
port = "3306"
database = "mydb1"
table_name = "countries_population2"

engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")

file_path = "E:/VARMA/data science/countries_dataset/countries_dataset/csv_data/countries_population/countries_population.csv"

inspector = inspect(engine)
columns = inspector.get_columns(table_name)

def mysql_to_python_type_mapping(mysql_type):
    types = str(mysql_type).lower()

    if "int" in types:
        return Optional[int]
    elif "float" in types or "double" in types or "decimal" in types:
        return Optional[float]
    elif "date" in types or "time" in types:
        return Optional[str]   
    else:
        return Optional[str]
    

fields = {}

for col in columns:
    col_name = col["name"]
    py_type = mysql_to_python_type_mapping(col["type"])
    fields[col_name] = (py_type, None)

DynamicModel = create_model("DynamicModel", **fields)

valid_rows = []
invalid_rows = []

for index, row in file_path.iterrows():
    try:
        validated = DynamicModel(**row.to_dict())
        valid_rows.append(validated.dict())
    except ValidationError as e:
        invalid_rows.append({
            "row_index": index,
            "errors": e.errors()
        })

validated_df = pd.DataFrame(valid_rows)
print("Valid rows:", len(valid_rows))
print("Invalid rows:", len(invalid_rows))

if invalid_rows:
    print("\nSample validation errors:")
    for errors in invalid_rows[:3]:
        print(errors)