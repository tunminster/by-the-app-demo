from azure.storage.blob import BlobServiceClient
import os
import pandas as pd
from fastapi import FastAPI
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache.decorator import cache

# FastAPI app instance
app = FastAPI()

# Use environment variables or directly set the config values
AZURE_STORAGE_CONNECTION_STRING = os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER')
TRAINING_BLOB_DATA_FILE = os.getenv('TRAINING_BLOB_DATA_FILE')

# Initialize cache - Make sure Redis is running and accessible
# cache_backend = RedisBackend("redis://localhost:6379")  # Example Redis connection
# FastAPICache.init(cache_backend, prefix="fastapi-cache")

async def load_training_data_from_blob(container_name: str, blob_name: str):
    """Load training data from Azure Blob Storage."""
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    # Download the file from blob storage and s
