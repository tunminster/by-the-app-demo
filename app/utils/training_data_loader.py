from azure.storage.blob import BlobServiceClient
import csv
import os
from flask import current_app
from app.extensions import cache
import pandas as pd

def load_training_data_from_blob(container_name, blob_name):
    
    connect_str = os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    #blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    #blob_data = blob_client.download_blob().content_as_text()
    with open("temp.csv", "wb") as download_file:
       download_file.write(blob_client.download_blob().readall())


    #for row in csv.DictReader(blob_data.splitlines()):
        #training_data.append({"role": row["role"], "content": row["content"]})
    
    converstaions = pd.read_csv("temp.csv") 
    training_data = converstaions['content'].tolist()

    
    return training_data

@cache.cached(timeout=300, key_prefix='training_data')
def get_cached_training_data():
    container_name = current_app.config['AZURE_STORAGE_CONTAINER']
    blob_name = current_app.config['TRAINING_BLOB_DATA_FILE']

    return load_training_data_from_blob(container_name, blob_name)

