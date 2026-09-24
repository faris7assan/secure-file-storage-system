# Secure File Storage System

## Hybrid Cryptography & Secure File Handling

Educational Python project demonstrating hybrid file encryption: symmetric encryption for file data, RSA-OAEP for session-key protection, SHA-256 hashing, and RSA-PSS signatures.

> Important: Educational/research software, not production cryptographic storage.

## Current construction

~~~text
File → SHA-256 → RSA-PSS Signature
     └→ Random Session Key → AES-256-CBC
                              └→ RSA-OAEP → Receiver Public Key
~~~

## Cryptographic components

- AES-256-CBC for bulk encryption
- Fresh random session key per file
- RSA-2048 + OAEP/SHA-256 for key wrapping
- SHA-256 for hashing
- RSA-PSS for digital signatures

## Security limitation

AES-CBC is not authenticated encryption. The current design verifies a signature after decryption, but CBC should not be exposed through a production decryption service without careful oracle/error handling.

A production-oriented next version should use AES-GCM or ChaCha20-Poly1305, version the file format, authenticate relevant metadata, and fail closed before writing unverified plaintext.

See SECURITY.md and docs/CRYPTO_REVIEW.md.

## Demonstration

The repository contains test fixtures for encryption/decryption, signatures, incorrect keys, tamper detection, and multiple file sizes. Use only synthetic/non-sensitive files.

## Future work

- [ ] AES-GCM/AEAD versioned file format
- [ ] Streaming encryption
- [ ] Key rotation and stronger key-management controls
- [ ] Multiple recipients
- [ ] Hardware-backed key storage
- [ ] Formal security testing

## Author

Hassan Faris — Cybersecurity Engineer | Network Security | Cryptography

- GitHub: https://github.com/faris7assan
- LinkedIn: https://www.linkedin.com/in/hassan-faris
