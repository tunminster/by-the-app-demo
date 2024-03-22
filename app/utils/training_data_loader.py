from azure.storage.blob import BlobServiceClient
import csv
import os
from flask import current_app
from .. import config as app

def load_training_data_from_blob(container_name, blob_name):
    
    connect_str = os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    blob_data = blob_client.download_blob().content_as_text()

    training_data = []

    for row in csv.reader(blob_data.splitlines()):
        training_data.append({"role": row["role"], "content": row["content"]})
    
    return training_data

def get_cached_training_data():
    cache = current_app.extensions['cache']
    container_name = app.config['AZURE_STORAGE_CONTAINER']
    blob_name = app.config['TRAINING_BLOB_DATA_FILE']

    key_prefix = 'training_data_{}'.format(blob_name)

    return cache.cached(timeout=300, key_prefix=key_prefix)(lambda: load_training_data_from_blob(container_name, blob_name))()

