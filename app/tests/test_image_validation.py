"""
Tests para validate_and_sanitize_image en storage.py:
- Archivo demasiado grande → ValueError
- Bytes mágicos incorrectos → ValueError
- Imagen JPEG válida → devuelve bytes JPEG
- Imagen PNG válida → devuelve bytes JPEG (re-codificada)
- Archivo que parece imagen pero es corrupto → ValueError
"""
import io
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from storage import validate_and_sanitize_image


def _make_jpeg_bytes(width=10, height=10) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(100, 150, 200)).save(buf, format="JPEG")
    return buf.getvalue()


def _make_png_bytes(width=10, height=10) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(200, 100, 50)).save(buf, format="PNG")
    return buf.getvalue()


def test_jpeg_valido_devuelve_bytes():
    result = validate_and_sanitize_image(_make_jpeg_bytes())
    assert isinstance(result, bytes)
    assert len(result) > 0
    # El resultado siempre es JPEG
    assert result[:3] == b'\xff\xd8\xff'


def test_png_valido_se_recodifica_a_jpeg():
    result = validate_and_sanitize_image(_make_png_bytes())
    # Aunque la entrada es PNG, la salida debe ser JPEG
    assert result[:3] == b'\xff\xd8\xff'


def test_archivo_demasiado_grande_lanza_error():
    datos_grandes = b'\xff\xd8\xff' + b'\x00' * (5 * 1024 * 1024 + 1)
    with pytest.raises(ValueError, match="demasiado grande"):
        validate_and_sanitize_image(datos_grandes)


def test_bytes_magicos_incorrectos_lanza_error():
    datos_falsos = b'PK\x03\x04' + b'\x00' * 100  # firma de ZIP
    with pytest.raises(ValueError, match="no es una imagen"):
        validate_and_sanitize_image(datos_falsos)


def test_jpeg_corrupto_lanza_error():
    # Bytes mágicos correctos pero contenido inválido
    datos_corruptos = b'\xff\xd8\xff' + b'\x00' * 50
    with pytest.raises(ValueError):
        validate_and_sanitize_image(datos_corruptos)


def test_texto_plano_lanza_error():
    with pytest.raises(ValueError):
        validate_and_sanitize_image(b'esto no es una imagen')
