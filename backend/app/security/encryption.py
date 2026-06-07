import os
import base64
import hashlib
from app.config import settings


def _derive_key() -> bytes:
    key = settings.encryption_key or 'default-dev-key-change-in-prod'
    return hashlib.sha256(key.encode()).digest()


def encrypt_api_key(plaintext: str) -> str:
    key = _derive_key()
    data = plaintext.encode()
    xor_bytes = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
    return base64.b64encode(xor_bytes).decode()


def decrypt_api_key(encrypted: str) -> str:
    key = _derive_key()
    data = base64.b64decode(encrypted)
    plain_bytes = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
    return plain_bytes.decode()
