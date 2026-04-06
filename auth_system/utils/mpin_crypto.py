import base64 
from drive.settings import SECRET_KEY

def _xor_bytes(data: bytes, key: str) -> bytes:
    key_bytes = key.encode()
    return bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data)])

def encrypt_mpin(mpin: str) -> str:
    xored = _xor_bytes(mpin.encode(), SECRET_KEY)
    return base64.urlsafe_b64encode(xored).decode()

def decrypt_mpin(encrypted_mpin: str) -> str:
    decoded = base64.urlsafe_b64decode(encrypted_mpin)
    return _xor_bytes(decoded, SECRET_KEY).decode()