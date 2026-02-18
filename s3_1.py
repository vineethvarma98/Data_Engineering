import boto3
import os

s3 = boto3.client('s3')

bucket_name = "dataengpracticebucket"
file_path_directory = "E:/VARMA/data science/countries_dataset/countries_dataset/csv_data/countries_population/"


for files in os.listdir(file_path_directory):
    file_path = os.path.join(file_path_directory, files)
    file_type = files.split(".")[1]
    #print(file_type)
    #print(file_path)
    if file_type == "csv":
        s3.upload_file(file_path,bucket_name,f"csv/{files}")
    elif file_type == "json":
        s3.upload_file(file_path,bucket_name,f"json/{files}")
    elif file_type == "orc":
        s3.upload_file(file_path,bucket_name,f"orc/{files}")
    elif file_type == "parquet":
        s3.upload_file(file_path,bucket_name,f"parquet/{files}")
    else:
        print("no files found")

print("done")