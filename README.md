# Secure File Storage System

## Hybrid Cryptography & Secure File Handling

Educational Python project demonstrating hybrid file encryption using symmetric encryption for file data, RSA-OAEP for session-key protection, SHA-256 hashing, and RSA-PSS signatures.

> **Project status:** Educational / research software. Not production cryptographic storage.

### Design

File
├── SHA-256 → RSA-PSS Signature
└── Random Session Key → AES-256-CBC → RSA-OAEP → Recipient Public Key

### Cryptographic components

- AES-256-CBC for bulk encryption
- Fresh random session key per file
- RSA-2048 + OAEP/SHA-256 for key wrapping
- SHA-256 hashing
- RSA-PSS digital signatures

### Security limitation

AES-CBC provides confidentiality but **not authenticated encryption**. The current design therefore requires careful integrity verification and error handling.

A production-oriented next version should move to **AES-GCM or ChaCha20-Poly1305**, use a versioned file format, authenticate relevant metadata, and fail closed before writing unverified plaintext.

See SECURITY.md and docs/CRYPTO_REVIEW.md.

### Testing focus

The repository includes test fixtures for encryption/decryption, signatures, incorrect keys, tamper detection, and multiple file sizes. Use only synthetic or non-sensitive files.

### Future work

- AES-GCM / AEAD versioned file format
- Streaming encryption
- Key rotation and stronger key-management controls
- Multiple recipients
- Hardware-backed key storage
- Formal security testing

### My role

**Hassan Faris — Cybersecurity Engineer | Network Security | Cryptography**

Focused on the cryptographic workflow, secure file-handling logic, key-wrapping design, and security review documentation.

### Links

- GitHub: https://github.com/faris7assan
- LinkedIn: https://www.linkedin.com/in/hassan-faris

### Security notice

Do not use this educational implementation to protect production or sensitive data without a formal cryptographic review.
