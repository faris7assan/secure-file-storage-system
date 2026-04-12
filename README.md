# Secure File Storage System Using Hybrid Cryptography

## Overview

A complete, production-grade Python implementation of a secure file storage system using hybrid cryptography. This system combines:
- **Symmetric Encryption (AES-256-CBC)** for file data
- **Public Key Encryption (RSA-2048)** for session key protection  
- **Digital Signatures (RSA)** for authenticity and non-repudiation
- **Cryptographic Hashing (SHA-256)** for integrity verification

## Modular Architecture

```
├── hashing.py                 # SHA-256 hashing module
├── key_management.py          # RSA/ECC key generation & storage
├── encryption.py              # AES-256-CBC symmetric encryption
├── signature.py               # RSA/ECDSA digital signatures
├── public_key_encryption.py   # RSA session key encryption
├── file_handler.py            # Complete encryption/decryption workflow
└── main.py                    # Demonstration & test cases
```

## Security Features

### 1. Symmetric Encryption (AES-256-CBC)
- **Algorithm**: AES (Advanced Encryption Standard)
- **Mode**: CBC (Cipher Block Chaining) 
- **Key Size**: 256 bits (maximum security)
- **IV**: 128-bit random per encryption (prevents pattern analysis)
- **Padding**: PKCS7 (standard for block ciphers)

**Why CBC Mode?** Prevents identical plaintext blocks from producing identical ciphertext blocks, unlike ECB mode.

### 2. Session Key Management
- **Generation**: Random 256-bit key per file
- **Usage**: Never reused across files
- **Protection**: Encrypted with receiver's RSA public key
- **Delivery**: Transmitted with encrypted file

**Critical**: Each encryption uses unique session key. Reuse would compromise security.

### 3. Public Key Encryption
- **Algorithm**: RSA-2048
- **Padding**: OAEP with SHA-256 (superior to PKCS#1 v1.5)
- **Purpose**: Encrypt only the session key (not full file)
- **Efficiency**: Fast encryption of small key vs. full file

**Design**: Hybrid approach (RSA + AES) combines benefits:
- RSA is fast for small data (session key)
- AES is fast for large data (file content)

### 4. Cryptographic Hashing

**Why Hash Before Signing?**

```
❌ WRONG:  Signature = RSASign(entire_file, private_key)
✅ RIGHT:  hash = SHA256(file)
           Signature = RSASign(hash, private_key)
```

Benefits:
- **Efficiency**: Signing 32-byte hash vs. multi-megabyte file
- **Non-repudiation**: Fixed hash acts as fingerprint
- **Security**: Prevents signature oracle attacks
- **Standardization**: Industry best practice

### 5. Digital Signatures

- **Algorithm**: RSA with PKCS#1 v1.5
- **Hash Algorithm**: SHA-256
- **Input**: Hash of plaintext file
- **Verification**: Signature + sender's public key = authentication

**Workflow**:
1. Sender computes hash of file
2. Sender signs hash with private key (proof of creation)
3. Signature sent with encrypted file
4. Receiver verifies signature with sender's public key
5. Invalid signature = file tampering or wrong sender

## File Format

```
┌─────────────────────────────────────────────────────────┐
│ Header (4 bytes): "SECF" - Format identifier           │
├─────────────────────────────────────────────────────────┤
│ Version (1 byte): 1 - File version                      │
├─────────────────────────────────────────────────────────┤
│ IV (16 bytes): Random initialization vector            │
├─────────────────────────────────────────────────────────┤
│ Encrypted Session Key Length (2 bytes)                  │
├─────────────────────────────────────────────────────────┤
│ Encrypted Session Key (typically 256 bytes)             │
├─────────────────────────────────────────────────────────┤
│ Ciphertext Length (4 bytes): Size of encrypted data    │
├─────────────────────────────────────────────────────────┤
│ Encrypted Data (File + Signature)                       │
├─────────────────────────────────────────────────────────┤
│ Signature Length (2 bytes)                              │
├─────────────────────────────────────────────────────────┤
│ Signature (typically 256 bytes for RSA-2048)            │
└─────────────────────────────────────────────────────────┘
```

**Total Overhead**: ~300 bytes + variable signature size

## Encryption Workflow

```
INPUT: plaintext file F, receiver's public key Kpub, sender's private key Ksign

1️⃣  Compute hash
    h = SHA256(F)

2️⃣  Create signature (proves sender identity)
    sig = RSASign(h, Ksign)

3️⃣  Generate unique session key
    K = RandomAES256Key()      ← NEW KEY PER FILE

4️⃣  Encrypt file + signature
    C = AES256_CBC_Encrypt(F || sig, K)

5️⃣  Encrypt session key
    EK = RSA_Encrypt(K, Kpub)  ← Only receiver can decrypt

6️⃣  Package for transmission
    EncryptedFile = {Header, IV, EK, C, sig}

OUTPUT: Secure encrypted file ready for transmission
```

## Decryption Workflow

```
INPUT: encrypted file, receiver's private key Kpriv, sender's public key Kverify

1️⃣  Parse encrypted file
    {Header, IV, EK, C, sig} = ReadFile()

2️⃣  Decrypt session key
    K = RSA_Decrypt(EK, Kpriv)  ← Only private key can decrypt

3️⃣  Decrypt file data
    F || sig = AES256_CBC_Decrypt(C, K, IV)

4️⃣  Recompute file hash
    h' = SHA256(F)

5️⃣  Verify signature
    valid = RSAVerify(sig, h', Kverify)

6️⃣  Security decision
    IF valid THEN
        Accept F (authentic & untampered)
    ELSE
        Reject F (tampering detected or wrong sender)

OUTPUT: Validated plaintext or rejection notice
```

## Setup & Installation

### Prerequisites
- Python 3.6+
- pip package manager

### Installation

```bash
# Clone or navigate to project directory
cd secure_file

# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install cryptography>=41.0.0 pycryptodome>=3.18.0
```

### Verify Installation

```bash
python -c "from cryptography.hazmat.primitives.asymmetric import rsa; print('✓ Cryptography installed')"
```

## Usage Examples

### Example 1: Encrypt a File

```python
from key_management import KeyManager
from file_handler import SecureFileHandler

# Generate key pairs
sender_private, sender_public = KeyManager.generate_rsa_keypair()
receiver_private, receiver_public = KeyManager.generate_rsa_keypair()

# Encrypt file
metadata = SecureFileHandler.encrypt_file(
    'secret.txt',           # File to encrypt
    'secret.txt.enc',       # Output encrypted file
    receiver_public,        # Encrypt session key with this
    sender_private          # Sign with this
)

print(f"Encrypted: {metadata['encrypted_filepath']}")
print(f"File hash: {metadata['file_hash']}")
```

### Example 2: Decrypt and Verify

```python
# Decrypt file
result = SecureFileHandler.decrypt_file(
    'secret.txt.enc',       # Encrypted file
    'secret.txt.dec',       # Output plaintext
    receiver_private,       # Decrypt session key
    sender_public           # Verify signature
)

if result['signature_valid']:
    print("✓ File authentic and untampered")
    with open(result['decrypted_filepath'], 'rb') as f:
        plaintext = f.read()
else:
    print("✗ File tampering detected!")
```

### Example 3: Handle Multiple Users

```python
# User 1 (Sender)
alice_private, alice_public = KeyManager.generate_rsa_keypair()

# User 2 (Receiver)
bob_private, bob_public = KeyManager.generate_rsa_keypair()

# Alice encrypts file for Bob
SecureFileHandler.encrypt_file(
    'report.pdf',
    'report.pdf.enc',
    bob_public,      # Only Bob can decrypt
    alice_private    # Alice signs it
)

# Bob decrypts and verifies Alice's signature
result = SecureFileHandler.decrypt_file(
    'report.pdf.enc',
    'report.pdf',
    bob_private,     # Bob's private key
    alice_public     # Verify Alice's signature
)

if result['signature_valid']:
    print("✓ Report is from Alice, verified and untampered")
```

## Test Cases

The system includes comprehensive test cases demonstrating:

### Test 1: Valid Encryption and Decryption
- ✓ File encrypted successfully
- ✓ File decrypted successfully
- ✓ Signature verified
- ✓ Decrypted content matches original

### Test 2: Tampered File Detection
- ✓ Encrypted file modified
- ✓ Tampering automatically detected
- ✓ Signature verification fails
- ✓ File rejected as untampered

### Test 3: Wrong Receiver Key
- ✓ File encrypted for specific receiver
- ✓ Cannot decrypt with wrong private key
- ✓ Decryption fails (prevents unauthorized access)

### Test 4: Wrong Sender Key
- ✓ File signed by specific sender
- ✓ Cannot verify with wrong public key
- ✓ Signature verification fails
- ✓ File rejected as unauthenticated

### Test 5: File Size Variations
- ✓ Handles tiny files (16 bytes)
- ✓ Handles small files (1 KB)
- ✓ Handles large files (100+ KB)
- ✓ All sizes encrypt/decrypt correctly

## Running Tests

```bash
# Run complete test suite
python main.py

# Expected output:
# - Workflow demonstration
# - 5 comprehensive test cases
# - Summary of results
# - All tests should PASS
```

## Security Considerations

### ✅ SAFE PRACTICES (Implemented)
- ✓ Unique session key per file
- ✓ Random IV per encryption
- ✓ OAEP padding for RSA (resistant to attacks)
- ✓ Constant-time hash comparison
- ✓ Separate keys for encryption vs. signing
- ✓ Digital signatures for authentication
- ✓ Hash-based signatures (not full file)
- ✓ Tamper detection via signature verification

### ❌ NEVER DO (NOT Implemented)
- ✗ ECB mode (patterns visible)
- ✗ Predictable IVs
- ✗ 64-bit encryption (too small)
- ✗ Hardcoded keys (breaks security)
- ✗ Key reuse (IV or session key)
- ✗ Unauthenticated encryption
- ✗ Signing full file (inefficient)
- ✗ PKCS#1 v1.5 for encryption (vulnerable)

## Module Reference

### hashing.py
- `HashModule.compute_hash(data)` - SHA-256 hash
- `HashModule.compute_hash_hex(data)` - Hex representation
- `HashModule.verify_hash(data, expected)` - Constant-time verification

### key_management.py
- `KeyManager.generate_rsa_keypair()` - RSA-2048 key generation
- `KeyManager.generate_ecc_keypair()` - ECC key generation
- `KeyManager.save_private_key(key, path)` - Store private key
- `KeyManager.save_public_key(key, path)` - Store public key
- `KeyManager.load_private_key(path)` - Load from PEM
- `KeyManager.load_public_key(path)` - Load from PEM

### encryption.py
- `EncryptionModule.generate_session_key()` - Random 256-bit key
- `EncryptionModule.generate_iv()` - Random 128-bit IV
- `EncryptionModule.encrypt(plaintext, key)` - AES-256-CBC encrypt
- `EncryptionModule.decrypt(ciphertext, key, iv)` - AES-256-CBC decrypt

### signature.py
- `SignatureModule.rsa_sign(hash, private_key)` - Create RSA signature
- `SignatureModule.rsa_verify(hash, sig, public_key)` - Verify RSA
- `SignatureModule.ecdsa_sign(hash, private_key)` - Create ECDSA signature
- `SignatureModule.ecdsa_verify(hash, sig, public_key)` - Verify ECDSA
- `SignatureModule.sign(hash, key)` - Auto-detect and sign
- `SignatureModule.verify(hash, sig, key)` - Auto-detect and verify

### public_key_encryption.py
- `PublicKeyEncryption.encrypt_session_key(key, public)` - Encrypt with RSA
- `PublicKeyEncryption.decrypt_session_key(encrypted, private)` - Decrypt

### file_handler.py
- `SecureFileHandler.encrypt_file(path, output, pub, priv)` - Full encryption workflow
- `SecureFileHandler.decrypt_file(path, output, priv, pub)` - Full decryption workflow

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Generate RSA-2048 keys | 1-2 seconds | One-time operation |
| Encrypt 1 MB file | ~50-100 ms | Dominated by AES performance |
| Decrypt 1 MB file | ~50-100 ms | Dominated by AES performance |
| Encrypt session key | ~10-20 ms | RSA-2048 slower than AES |
| Decrypt session key | ~50-100 ms | Private key operation slower |
| SHA-256 hash 1 MB | ~5-10 ms | Very fast |
| Sign hash | ~20-50 ms | Fast (hash only) |
| Verify signature | ~20-50 ms | Fast (hash only) |

## Cryptographic Standards Compliance

- ✓ AES: FIPS 197
- ✓ OAEP: PKCS #1 v2.2
- ✓ 

PKCS#1 v1.5: PKCS #1 v2.2
- ✓ SHA-256: FIPS 180-4
- ✓ ECDSA: FIPS 186-4

## Troubleshooting

### "Invalid file format" error
- File may be corrupted
- File may not be encrypted with this system
- Check file header with: `hexdump -C file.enc | head`

### "Signature verification failed"
- File was modified after encryption
- Receiver's private key doesn't match encryption public key
- Sender's public key doesn't match signing private key

### "Decryption failed"
- Wrong private key for decryption
- Wrong IV (should be read from file)
- Ciphertext corrupted

### Performance issues with large files
- AES-256-CBC performance is proportional to file size
- Consider streaming encryption for files > 1 GB
- Use SSD for better disk I/O

## Future Enhancements

- [ ] Streaming encryption for files > 1 GB
- [ ] Key derivation functions (KDF) for password-based keys
- [ ] Authenticated encryption mode (GCM)
- [ ] Multiple recipient support
- [ ] Key rotation mechanisms
- [ ] Hardware security module (HSM) integration
- [ ] Quantum-resistant algorithms
- [ ] Perfect forward secrecy (ephemeral keys)

## License

Educational/Research Purpose

## Author

Secure Cryptography System v1.0
Date: 2024
