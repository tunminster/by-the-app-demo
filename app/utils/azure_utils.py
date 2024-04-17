from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

def get_google_cloud_service_account_from_key_vault():
    key_vault_name = os.environ.get('KEY_VAULT_NAME')
    key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_uri, credential=credential)

    secret_name = "google-service-account"
    retrieved_secret = client.get_secret(secret_name)

    return retrieved_secret