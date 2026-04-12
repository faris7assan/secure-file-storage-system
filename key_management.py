import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class KeyManager:
    @staticmethod
    def generate_rsa_keypair(key_size=2048):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def save_private_key(private_key, filepath, password=None):
        if password:
            encryption = serialization.BestAvailableEncryption(password)
        else:
            encryption = serialization.NoEncryption()
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        
        with open(filepath, 'wb') as f:
            f.write(pem)

    @staticmethod
    def save_public_key(public_key, filepath):
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(filepath, 'wb') as f:
            f.write(pem)

    @staticmethod
    def load_private_key(filepath, password=None):
        with open(filepath, 'rb') as f:
            pem = f.read()
        
        return serialization.load_pem_private_key(
            pem, 
            password=password,
            backend=default_backend()
        )

    @staticmethod
    def load_public_key(filepath):
        with open(filepath, 'rb') as f:
            pem = f.read()
        
        return serialization.load_pem_public_key(
            pem,
            backend=default_backend()
        )
