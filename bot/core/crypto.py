from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import json
import os


class SecureURLManager:
    def __init__(self, token: bytes):
        self.key = token

    
    def encrypt(self, data: dict) -> str:
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        payload = json.dumps(data, separators=(',', ':')).encode()
        ciphertext = aesgcm.encrypt(nonce, payload, None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()
    

    def decrypt(self, token: str) -> dict:
        raw = base64.urlsafe_b64decode(token.encode())
        nonce, ciphertext = raw[:12], raw[12:]
        aesgcm = AESGCM(self.key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(decrypted)
    