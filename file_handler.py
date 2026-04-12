import os
import struct
from hashing import HashModule
from encryption import EncryptionModule
from signature import SignatureModule
from public_key_encryption import PublicKeyEncryption


class SecureFileHandler:
    HEADER = b"SECF"
    VERSION = 1

    @staticmethod
    def encrypt_file(input_file, output_file, receiver_public_key, sender_private_key):
        with open(input_file, 'rb') as f:
            plaintext = f.read()
        
        file_hash = HashModule.sha256(plaintext)
        
        signature = SignatureModule.sign(file_hash, sender_private_key)
        
        data_to_encrypt = plaintext + signature
        
        session_key = EncryptionModule.generate_session_key()
        ciphertext, iv = EncryptionModule.encrypt_aes256_cbc(data_to_encrypt, session_key)
        
        encrypted_session_key = PublicKeyEncryption.encrypt(session_key, receiver_public_key)
        
        with open(output_file, 'wb') as f:
            f.write(SecureFileHandler.HEADER)
            f.write(bytes([SecureFileHandler.VERSION]))
            f.write(iv)
            f.write(struct.pack('>H', len(encrypted_session_key)))
            f.write(encrypted_session_key)
            f.write(struct.pack('>I', len(ciphertext)))
            f.write(ciphertext)
        
        return {
            'input_file': input_file,
            'encrypted_filepath': output_file,
            'original_size': len(plaintext),
            'ciphertext_size': len(ciphertext),
            'file_hash': file_hash.hex(),
            'signature_size': len(signature)
        }

    @staticmethod
    def decrypt_file(input_file, output_file, receiver_private_key, sender_public_key):
        with open(input_file, 'rb') as f:
            header = f.read(4)
            if header != SecureFileHandler.HEADER:
                raise ValueError("Invalid file format")
            
            version = ord(f.read(1))
            if version != SecureFileHandler.VERSION:
                raise ValueError("Invalid file version")
            
            iv = f.read(16)
            
            encrypted_session_key_len = struct.unpack('>H', f.read(2))[0]
            encrypted_session_key = f.read(encrypted_session_key_len)
            
            ciphertext_len = struct.unpack('>I', f.read(4))[0]
            ciphertext = f.read(ciphertext_len)
        
        session_key = PublicKeyEncryption.decrypt(encrypted_session_key, receiver_private_key)
        
        decrypted_data = EncryptionModule.decrypt_aes256_cbc(ciphertext, session_key, iv)
        
        plaintext = decrypted_data[:-256]
        signature = decrypted_data[-256:]
        
        file_hash = HashModule.sha256(plaintext)
        signature_valid = SignatureModule.verify(file_hash, signature, sender_public_key)
        
        with open(output_file, 'wb') as f:
            f.write(plaintext)
        
        return {
            'decrypted_filepath': output_file,
            'decrypted_size': len(plaintext),
            'file_hash': file_hash.hex(),
            'signature_valid': signature_valid,
            'tampered': not signature_valid
        }
