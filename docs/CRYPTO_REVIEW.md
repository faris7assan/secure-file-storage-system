# Cryptographic Review

## Current design

The repository currently demonstrates:

- AES-256-CBC for bulk encryption
- RSA-OAEP for wrapping the session key
- RSA-PSS for signatures
- SHA-256 for file hashing

RSA-OAEP and RSA-PSS are appropriate modern padding constructions. The main design concern is AES-CBC: it provides confidentiality but not authenticated encryption.

The project signs the plaintext and verifies the signature after decryption. That provides an integrity/authenticity check when the sender public key is trusted, but it does not turn CBC decryption into an authenticated-encryption interface and does not by itself prevent padding-oracle risks in an exposed service.

## Recommended next version

Use a versioned file format with:

1. Random 256-bit data-encryption key.
2. AES-256-GCM with a fresh 96-bit nonce.
3. RSA-OAEP-SHA-256 to wrap the data key.
4. Optional RSA-PSS or Ed25519 signature over the canonical metadata plus ciphertext.
5. Explicit algorithm/version identifiers in the header.
6. Fail-closed verification before writing decrypted output.

The existing version should be described as a legacy educational format rather than a production storage protocol.
