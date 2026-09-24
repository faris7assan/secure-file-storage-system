# Security Policy

This repository is an educational cryptography project. It is not a production file-storage service.

## Important cryptographic note

The current legacy implementation uses AES-256-CBC plus a digital signature. CBC encryption is not authenticated encryption and should not be exposed through an error-distinguishing decryption service.

For a new production design, prefer an AEAD construction such as AES-256-GCM or ChaCha20-Poly1305, with RSA-OAEP used only to wrap the randomly generated file key and RSA-PSS/Ed25519 for signatures where signatures are actually required.

## Key handling

- Never commit private keys or real credentials.
- Prefer encrypted private-key storage.
- Use unique keys/nonces as required by the chosen construction.
- Treat example ciphertext/plaintext files as test fixtures, not secrets.

## Testing

Use only synthetic or non-sensitive files in the repository.
