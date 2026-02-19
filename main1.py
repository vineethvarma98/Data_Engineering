#python code to read a table schema and validate it with newly ingesting data
#ingeting data formats = csv, json

import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host = "mine",
    user = "root",
    password = "root",
    database = "mydb1",
)

cursor = conn.cursor()

cursor.execute("DSELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'countries_population2'")

output = cursor.fetchall()

db_schema = {column_name : data_type for column_name, data_type in output}

file_path = "E:\VARMA\data science\countries_dataset\countries_dataset\csv_data\countries_population\countries_population.csv"

df = pd.read_csv(file_path)

def datatype_conversion(dict1, df):

    dic = df.dtypes.to_dict()

    if set(dict1.keys()) != set(dic.keys()):
        print("columns mismatched, aborting the data loading")
    print("data columns are matched, proceeding with next validation")


    for (key,value), (key1,value1) in zip(db_schema,dic):
        if value == value1:
            pass
        elif value1 == "string" & (value == "varchar" or value == "text"):
            pass
        elif value1 == "int" & (value == "int" or value == "bigint"):
            pass
        else:
            #need to do typecasting
return df

datatype_conversion(db_schema,df)

columns = list(db_schema.keys())
col_str = ", ".join(columns)
value = ", ".join(["%s"] * len(columns))

sql = f"""
INSERT INTO {table_name} ({col_str})
VALUES ({value})
"""

for _, row in df.iterrows():
    values = [row[col] for col in columns]
    cursor.execute(sql, values)


conn.commit()

print(f"{len(df)} records successfully inserted/updated.")

cursor.close()
conn.close()