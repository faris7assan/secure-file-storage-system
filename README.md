# Secure File Storage System Using Hybrid Cryptography

### Educational Cryptography & Secure File Handling Project

A Python implementation of a secure file-storage workflow demonstrating **hybrid cryptography**: symmetric encryption for file data, public-key encryption for session-key protection, digital signatures for authenticity, and SHA-256 hashing for integrity verification.

> **Security note:** This is an educational/research project. It is not presented as production-ready cryptographic software. Review and harden the design before using it for real sensitive data.

## Security Design

```text
Plaintext File
      │
      ├── SHA-256 ──→ File Hash ──→ RSA Signature
      │
      └── AES-256-CBC + Random Session Key
                         │
                         ▼
                  Encrypted File
                         │
                  Session Key
                         │
                    RSA-OAEP
                         │
                         ▼
               Receiver Public Key
```

## Implemented Components

- **AES-256-CBC** for file-data encryption
- **Random per-file session keys**
- **RSA-2048 + OAEP/SHA-256** for protecting session keys
- **SHA-256** for file hashing
- **RSA digital signatures** for authenticity and integrity verification
- Modular key-management, encryption, signing, and file-handling components

## Important Cryptographic Consideration

AES-CBC provides confidentiality but is **not an authenticated-encryption mode**. The project uses digital signatures to provide authenticity/integrity, but a production implementation should consider a modern AEAD construction such as **AES-GCM** and a carefully reviewed key-management design.

The project itself identifies authenticated encryption and other hardening steps as future enhancements.

## Encryption Workflow

1. Hash the plaintext file with SHA-256.
2. Sign the hash with the sender's private key.
3. Generate a fresh 256-bit session key.
4. Encrypt the file data and signature using AES-256-CBC with a random IV.
5. Encrypt the session key with the receiver's RSA public key using OAEP.
6. Package the encrypted content, protected session key, IV, and signature.

## Decryption Workflow

1. Parse the encrypted file structure.
2. Recover the session key using the receiver's private RSA key.
3. Decrypt the file using AES-256-CBC.
4. Recompute the SHA-256 hash.
5. Verify the digital signature with the sender's public key.
6. Accept the file only when verification succeeds.

## Project Structure

```text
├── hashing.py
├── key_management.py
├── encryption.py
├── signature.py
├── public_key_encryption.py
├── file_handler.py
└── main.py
```

## Installation

### Requirements

- Python 3.8+
- `cryptography`
- `pycryptodome`

```bash
pip install -r requirements.txt
```

## Usage

The project includes examples for:

- Encrypting and decrypting files
- Generating sender/receiver key pairs
- Verifying digital signatures
- Detecting modified ciphertext/files
- Testing incorrect receiver or sender keys

Run the demonstration/test workflow with:

```bash
python main.py
```

## Test Scenarios

The project includes demonstrations covering:

- Valid encryption/decryption
- Tampered-file detection
- Wrong receiver key
- Wrong sender verification key
- Multiple file sizes

## Future Improvements

- [ ] Replace CBC-based construction with AES-GCM or another AEAD design
- [ ] Streaming encryption for large files
- [ ] Stronger key-management and rotation mechanisms
- [ ] Multiple-recipient support
- [ ] Hardware-backed key storage / HSM integration
- [ ] Formal security review and threat modeling

## Author

**Hassan Faris**  
Cybersecurity Graduate | Network Security | Cryptography

- GitHub: https://github.com/faris7assan
- Portfolio: https://hassanhamedfaris69.base44.app/

## License

Educational / Research Purpose
