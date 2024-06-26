from azure.storage.blob import BlobServiceClient
import csv
import os
from flask import current_app
from app.extensions import cache

def load_training_data_from_blob(container_name, blob_name):
    
    connect_str = os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    blob_data = blob_client.download_blob().content_as_text()

    training_data = []

    for row in csv.DictReader(blob_data.splitlines()):
        training_data.append({"role": row["role"], "content": row["content"]})

    print(training_data)
    
    return training_data

@cache.cached(timeout=300, key_prefix='training_data')
def get_cached_training_data():
    container_name = current_app.config['AZURE_STORAGE_CONTAINER']
    blob_name = current_app.config['TRAINING_BLOB_DATA_FILE']

    return load_training_data_from_blob(container_name, blob_name)

