import os
import uuid

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings


def _client() -> BlobServiceClient:
    account_url = os.environ["BLOB_ACCOUNT_URL"]
    return BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())


def upload_recipe_image(data: bytes, content_type: str = "image/jpeg") -> str:
    container = os.environ["BLOB_CONTAINER"]
    ext = content_type.split("/")[-1] if "/" in content_type else "jpg"
    blob_name = f"{uuid.uuid4()}.{ext}"
    blob_client = _client().get_blob_client(container=container, blob=blob_name)
    blob_client.upload_blob(
        data,
        blob_type="BlockBlob",
        content_settings=ContentSettings(content_type=content_type),
        overwrite=True,
    )
    account_url = os.environ["BLOB_ACCOUNT_URL"].rstrip("/")
    return f"{account_url}/{container}/{blob_name}"
