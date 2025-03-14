from google.cloud import texttospeech
from azure.storage.blob import BlobServiceClient, ContentSettings
from app.utils.azure_utils import get_google_cloud_service_account_from_key_vault
from google.oauth2.service_account import Credentials
import os
import json
import re

def get_credentials():
    service_account_info = json.loads(get_google_cloud_service_account_from_key_vault())
    credentials = Credentials.from_service_account_info(service_account_info)
    return credentials

def synthesize_speech(text, language_code="en-US", voice_name="en-US-Wavenet-D"):
    credentials = get_credentials()
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    # Configure the request
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    # Synthesize speech
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Handle Azure blob Storage upload
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING'))
    container_name = os.getenv('AZURE_STORAGE_VOICE_CONTAINER')  # Using environment variable for container name

    sanitized_text = re.sub(r'[^a-zA-Z0-9]', '', text[:10])

    # Generate a unique filename for the audio file
    blob_name = f"{sanitized_text}-{os.urandom(4).hex()}.mp3"
    
    # Get the blob client for uploading the file
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Ensure to set the correct content settings for MP3
    content_settings = ContentSettings(content_type='audio/mpeg')

    # Upload the audio content to Azure Blob Storage
    blob_client.upload_blob(response.audio_content, overwrite=True, content_settings=content_settings)

    # Assuming the container is configured to allow public access
    audio_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}"

    return audio_url
