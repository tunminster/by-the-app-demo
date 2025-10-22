from azure.identity import EnvironmentCredential, ClientSecretCredential, AzureCliCredential
from azure.keyvault.secrets import SecretClient
import os

def get_google_cloud_service_account_from_key_vault():
    key_vault_name = os.environ.get('KEY_VAULT_NAME')
    key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"

    azure_client_id = os.environ.get('AZURE_CLIENT_ID')
    azure_client_secret = os.environ.get('AZURE_CLIENT_SECRET')
    azure_tenant_id = os.environ.get('AZURE_TENANT_ID')

    credential = ClientSecretCredential(tenant_id=azure_tenant_id, client_id=azure_client_id, client_secret=azure_client_secret)

    client = SecretClient(vault_url=key_vault_uri, credential=credential)

    secret_name = "google-service-account"
    retrieved_secret = client.get_secret(secret_name)

    return retrieved_secret.value

def get_jwt_secret_key():
    key_vault_name = os.environ.get('KEY_VAULT_NAME')
    key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"

    azure_client_id = os.environ.get('AZURE_CLIENT_ID')
    print(" azure_client_id ", azure_client_id)
    azure_client_secret = os.environ.get('AZURE_CLIENT_SECRET')
    azure_tenant_id = os.environ.get('AZURE_TENANT_ID')

    credential = ClientSecretCredential(tenant_id=azure_tenant_id, client_id=azure_client_id, client_secret=azure_client_secret)

    client = SecretClient(vault_url=key_vault_uri, credential=credential)

    secret_name = "Jwt-Secret-Key"

    retrieved_secret = client.get_secret(secret_name)

    return retrieved_secret.value