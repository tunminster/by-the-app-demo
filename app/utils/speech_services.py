from google.cloud import texttospeech
from azure.storage.blob import BlobServiceClient
from flask import current_app
from app.utils.azure_utils import get_google_cloud_service_account_from_key_vault
from google.oauth2.service_account import Credentials
import os
import json

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
    response =client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)


    # Handle Azure blob Storage upload
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('BYTHEAPP_AZURE_STORAGE_CONNECTION_STRING'))
    container_name = current_app.config['AZURE_STORAGE_VOICE_CONTAINER']

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{text[:10]}-{os.urandom(4).hex().mp3}")

    # Upload the audio content
    blob_client.upload_blob(response.audio_content, overwrite=True)
    blob_client.set_blob_properties(content_type="audio/mp3")

    # Assuming the container is configured to allow public access
    return blob_client.url