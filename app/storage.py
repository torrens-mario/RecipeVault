import io
import os
import uuid

from PIL import Image
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

_MAX_BYTES = 5 * 1024 * 1024  # 5 MB

# Firmas de bytes reales de cada formato (no confiamos en el Content-Type del cliente)
_MAGIC = [
    (b'\xff\xd8\xff', 'image/jpeg'),
    (b'\x89PNG\r\n\x1a\n', 'image/png'),
]

# Limitar megapíxeles para evitar ataques de descompresión (decompression bomb)
Image.MAX_IMAGE_PIXELS = 20_000_000  # ~4000×5000 px máximo


def _check_magic_bytes(data: bytes) -> None:
    for magic, _ in _MAGIC:
        if data[:len(magic)] == magic:
            return
    # WebP: bytes 0-3 = RIFF, bytes 8-11 = WEBP
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return
    raise ValueError("El archivo no es una imagen reconocida (se aceptan JPEG, PNG y WebP)")


def validate_and_sanitize_image(data: bytes) -> bytes:
    """
    Valida y re-codifica una imagen a JPEG limpio.

    Capas de seguridad:
    1. Límite de tamaño (5 MB)
    2. Bytes mágicos — verifica la firma real del archivo, no el Content-Type del cliente
    3. Re-codificación con Pillow — fuerza la decodificación completa, elimina todos los
       metadatos (EXIF, ICC, comentarios) y previene archivos políglotas (p. ej. un script
       Python que también sea un JPEG válido)
    4. Límite de megapíxeles — previene ataques de descompresión

    Devuelve bytes JPEG limpios. Lanza ValueError si el archivo no es válido.
    """
    if len(data) > _MAX_BYTES:
        raise ValueError("La imagen es demasiado grande (máximo 5 MB)")

    _check_magic_bytes(data)

    try:
        with Image.open(io.BytesIO(data)) as img:
            # convert("RGB") fuerza la decodificación completa y normaliza el espacio de color.
            # Guardar como JPEG elimina todos los metadatos y payloads embebidos.
            out = io.BytesIO()
            img.convert("RGB").save(out, format="JPEG", quality=85, optimize=True)
            return out.getvalue()
    except ValueError:
        raise
    except Exception:
        raise ValueError("El archivo no es una imagen válida")


def _client() -> BlobServiceClient:
    account_url = os.environ["BLOB_ACCOUNT_URL"]
    return BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())


def upload_recipe_image(data: bytes) -> str:
    """Sube bytes de imagen ya validados a Blob Storage. Siempre almacena como JPEG."""
    container = os.environ["BLOB_CONTAINER"]
    blob_name = f"{uuid.uuid4()}.jpg"
    blob_client = _client().get_blob_client(container=container, blob=blob_name)
    blob_client.upload_blob(
        data,
        blob_type="BlockBlob",
        content_settings=ContentSettings(content_type="image/jpeg"),
        overwrite=True,
    )
    account_url = os.environ["BLOB_ACCOUNT_URL"].rstrip("/")
    return f"{account_url}/{container}/{blob_name}"
