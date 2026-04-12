"""
Architecture and Design Documentation
=====================================

This document provides in-depth technical details about the hybrid cryptography
system architecture, design decisions, and security analysis.

"""

# ==============================================================================
# 1. SYSTEM ARCHITECTURE OVERVIEW
# ==============================================================================

ARCHITECTURE_OVERVIEW = """
┌─────────────────────────────────────────────────────────────────────┐
│                  SECURE FILE STORAGE SYSTEM                         │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                        USER APPLICATION                              │
└───────────────────────────────────────────────────────────────────────┘
           ↓                                              ↓
┌─────────────────────────────────────────────────────┐
│         SecureFileHandler (Orchestration)          │
│  - encrypt_file()                                  │
│  - decrypt_file()                                  │
│  - File format handling                            │
└─────────────────────────────────────────────────────┘
   ↓              ↓              ↓              ↓
   
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│   Hashing    │ │ Encryption   │ │  Signature   │ │ Public Key Enc   │
│   Module     │ │   Module     │ │   Module     │ │   Module         │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────────┤
│ SHA-256      │ │ AES-256-CBC  │ │ RSA-2048     │ │ RSA-2048 + OAEP  │
│              │ │              │ │ ECDSA        │ │ MGF1-SHA256      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘
   ↓              ↓              ↓              ↓

┌─────────────────────────────────────────────────────────────────────┐
│                   Key Management Module                             │
│  - RSA keypair generation                                           │
│  - ECC keypair generation                                           │
│  - PEM serialization/deserialization                                │
└─────────────────────────────────────────────────────────────────────┘
   ↓

┌─────────────────────────────────────────────────────────────────────┐
│              Cryptography Library (cryptography)                    │
│  - FIPS-compliant algorithms                                        │
│  - Hardware acceleration support                                    │
│  - Timing attack resistant                                          │
└─────────────────────────────────────────────────────────────────────┘
"""

# ==============================================================================
# 2. ENCRYPTION WORKFLOW - DETAILED STEPS
# ==============================================================================

ENCRYPTION_WORKFLOW = """
╔════════════════════════════════════════════════════════════════════════╗
║                    ENCRYPTION WORKFLOW                               ║
╚════════════════════════════════════════════════════════════════════════╝

INPUT:
  - Plaintext file: F
  - Receiver's RSA public key: Kpub
  - Sender's RSA private key: Ksign

STEP 1: Read File
  ┌─────────────────────────┐
  │ F = ReadBinaryFile()    │
  │ len(F) can be MB/GB     │
  └─────────────────────────┘

STEP 2: Compute Cryptographic Hash
  ┌──────────────────────────────────────────┐
  │ h = SHA256(F)                            │
  │ h is 32 bytes (256 bits)                 │
  │ Uniquely identifies file content         │
  │ Any bit change in F → completely         │
  │ different h (avalanche effect)           │
  └──────────────────────────────────────────┘

STEP 3: Create Digital Signature
  ┌──────────────────────────────────────────┐
  │ sig = RSASign(h, Ksign)                  │
  │ sig proves Ksign was used                │
  │ Only holder of Ksign can create sig      │
  │ sig is ~256 bytes for RSA-2048           │
  │ Cannot be replicated by brute force      │
  │ Sender cannot deny creating sig          │
  └──────────────────────────────────────────┘

STEP 4: Generate Unique Session Key
  ┌──────────────────────────────────────────┐
  │ K = RandomBytes(32)                      │
  │ K is 256 bits (32 bytes)                 │
  │ Used for symmetric encryption            │
  │ CRITICAL: Never reused for any file      │
  │ Unique K per file prevents patterns      │
  │ If attacker gets K, only one file        │
  │ compromised (not all files)              │
  └──────────────────────────────────────────┘

STEP 5: Encrypt File + Signature
  ┌──────────────────────────────────────────┐
  │ IV = RandomBytes(16)                     │
  │ Combined = F || sig                      │
  │ (Concatenate file and signature)         │
  │ C = AES256CBC_Encrypt(Combined, K, IV)   │
  │ C is encrypted data (len ≈ len(F))       │
  │ IV is needed for decryption               │
  │ CRITICAL: Never reuse IV with same K     │
  └──────────────────────────────────────────┘

STEP 6: Encrypt Session Key
  ┌──────────────────────────────────────────┐
  │ EK = RSA_Encrypt(K, Kpub)                │
  │ EK is RSA ciphertext (~256 bytes)        │
  │ Only holder of corresponding             │
  │ private key can decrypt EK to get K      │
  │ K stays secret during transmission       │
  │ Even if Kpub is known publicly           │
  │ Kpub alone cannot decrypt EK             │
  └──────────────────────────────────────────┘

STEP 7: Package Everything
  ┌──────────────────────────────────────────┐
  │ EncryptedFile = {                        │
  │   Header: "SECF" (4 bytes),              │
  │   Version: 1,                            │
  │   IV: (16 bytes),                        │
  │   EncKeyLen: sizeof(EK) (2 bytes),       │
  │   EK: (256 bytes),                       │
  │   CipherLen: sizeof(C) (4 bytes),        │
  │   C: (encrypted data),                   │
  │   SigLen: sizeof(sig) (2 bytes),         │
  │   sig: (256 bytes)                       │
  │ }                                        │
  └──────────────────────────────────────────┘

OUTPUT:
  - Encrypted file ready for transmission
  - Only intended receiver can decrypt
  - Authenticity proven by signature

SECURITY PROPERTIES AFTER ENCRYPTION:
  ✓ CONFIDENTIALITY: C encrypted with AES, K encrypted with RSA
  ✓ AUTHENTICITY: sig proves sender created this exact file
  ✓ INTEGRITY: Any bit change in C detected by signature
  ✓ NON-REPUDIATION: Sender cannot deny creating file
  ✓ KEY CONFIDENTIALITY: K protected by RSA encryption
"""

# ==============================================================================
# 3. DECRYPTION WORKFLOW - DETAILED STEPS
# ==============================================================================

DECRYPTION_WORKFLOW = """
╔════════════════════════════════════════════════════════════════════════╗
║                    DECRYPTION WORKFLOW                               ║
╚════════════════════════════════════════════════════════════════════════╝

INPUT:
  - Encrypted file package
  - Receiver's RSA private key: Kpriv
  - Sender's RSA public key: Kverify

STEP 1: Parse Encrypted File
  ┌─────────────────────────────────────┐
  │ {Header, Version, IV,               │
  │  EncKeyLen, EK, CipherLen,          │
  │  C, SigLen, sig} = ParseFile()      │
  │                                     │
  │ Verify Header == "SECF"             │
  │ Verify Version == 1                 │
  └─────────────────────────────────────┘

STEP 2: Decrypt Session Key
  ┌──────────────────────────────────────┐
  │ K = RSA_Decrypt(EK, Kpriv)           │
  │ Only Kpriv can decrypt EK            │
  │ If wrong Kpriv used:                 │
  │   → ValueError (invalid padding)     │
  │   → Decryption fails                 │
  │ If right Kpriv:                      │
  │   → K is correctly recovered         │
  └──────────────────────────────────────┘

STEP 3: Decrypt File Data
  ┌──────────────────────────────────────┐
  │ Combined = AES256CBC_Decrypt(        │
  │             C, K, IV)                │
  │ Uses K and IV from encrypted file    │
  │ Removes PKCS7 padding                │
  │ Result is: F || sig                  │
  │ (File concatenated with signature)   │
  └──────────────────────────────────────┘

STEP 4: Extract Components
  ┌──────────────────────────────────────┐
  │ F = Combined[:-len(sig)]             │
  │ (All but last len(sig) bytes)        │
  │ sig = Combined[-len(sig):]           │
  │ (Last len(sig) bytes)                │
  │                                      │
  │ Now have plaintext F and sig         │
  └──────────────────────────────────────┘

STEP 5: Recompute File Hash
  ┌──────────────────────────────────────┐
  │ h' = SHA256(F)                       │
  │ Deterministic: same F always         │
  │ produces same h'                     │
  │ If even 1 bit changed in F:          │
  │   → completely different h'          │
  │   → Signature verification fails     │
  └──────────────────────────────────────┘

STEP 6: Verify Signature
  ┌──────────────────────────────────────┐
  │ valid = RSA_Verify(sig, h', Kverify) │
  │ Checks: sig was created by           │
  │        corresponding Kpriv           │
  │ Checks: sig is for this exact h'     │
  │ If valid:                            │
  │   ✓ File is from expected sender     │
  │   ✓ File has not been tampered      │
  │   ✓ Sender cannot deny creation      │
  │ If NOT valid:                        │
  │   ✗ File tampering detected          │
  │   ✗ Wrong sender (wrong Kverify)     │
  │   ✗ Signature was forged             │
  └──────────────────────────────────────┘

STEP 7: Accept or Reject
  ┌──────────────────────────────────────┐
  │ IF valid THEN                        │
  │   WriteFile(F, output_path)          │
  │   Return success + metadata          │
  │ ELSE                                 │
  │   Do NOT write file                  │
  │   Return failure + reason            │
  │   Mark as tampered/untrusted         │
  └──────────────────────────────────────┘

OUTPUT:
  - Plaintext file (if valid)
  - OR failure notice (if tampered/invalid)

SECURITY GUARANTEES:
  ✓ File not decryptable without Kpriv
  ✓ Content verified against signature
  ✓ Tampering immediately detected
  ✓ Wrong sender identified
  ✓ Authenticity confirmed
"""

# ==============================================================================
# 4. ATTACK SCENARIOS AND DEFENSES
# ==============================================================================

ATTACK_SCENARIOS = """
╔════════════════════════════════════════════════════════════════════════╗
║                    ATTACK SCENARIOS & DEFENSES                        ║
╚════════════════════════════════════════════════════════════════════════╝

ATTACK 1: Eavesdropping (Passive)
────────────────────────────────
Attacker: Intercepts encrypted file during transmission
Threat: Read original file content

Defense: AES-256 encryption
  - File encrypted with strong symmetric cipher
  - Attacker has ciphertext C but not key K
  - K is encrypted with RSA (EK is also ciphertext)
  - Both C and EK are encrypted
  - No attack breaks AES-256 in polynomial time
  - Brute force requires 2^256 attempts (infeasible)
Result: ✓ PROTECTED
  - Attacker cannot decrypt file
  - Information remains confidential


ATTACK 2: File Tampering
────────────────────────
Attacker: Modifies encrypted ciphertext
Example: Changes bits in C to alter plaintext

Defense: Digital Signature Verification
  - If any bit in C changes → decrypted plaintext changes
  - Changes in F cause hash h' to completely change
  - sig was created for original hash h
  - h' ≠ h → signature verification fails
  - File is rejected as untrusted
Result: ✓ PROTECTED
  - Tampering is detected 100% of time
  - Corrupted file is rejected
  - Integrity guaranteed


ATTACK 3: Forgery (Impersonation)
─────────────────────────────────
Attacker: Creates fake signature claiming to be Alice
Fraud: Send disguised message as Alice

Defense: Only Alice's private key can create valid sig
  - Attacker has only Alice's public key (Kverify)
  - Cannot use public key to create signatures
  - RSA assumes private key is kept secret
  - Without Alice's private Kpriv, cannot forge sig
  - sig + h' + Kverify: signature verification fails
Result: ✓ PROTECTED
  - Only actual sender can create valid signatures
  - Impersonation impossible
  - Non-repudiation guaranteed


ATTACK 4: Key Substitution (Man-in-Middle for Keys)
───────────────────────────────────────────────────
Attacker: Replaces Bob's public key with own fake key
Scenario: Intercepts key distribution, substitutes fake key
Result: Alice encrypts with attacker's fake public key

Defense: Out-of-band key verification
  - This system assumes Bob's public key is authentic
  - Key distribution is out of scope
  - In production: use PKI, certificate authorities
  - Or: verify key fingerprints through secure channel
  - Or: pre-share keys through trusted method
Note: Not specific to this system - general crypto issue
Mitigation: ✓ Certificates, PKI, key fingerprints


ATTACK 5: Wrong Session Key Decryption
──────────────────────────────────────
Attacker: Attempts to guess or brute force session key K
Threat: Decrypt file without receiver's private key

Defense: RSA encryption of session key
  - Session key K is encrypted as EK = RSA_Encrypt(K, public)
  - To get K, must decrypt EK with private key
  - Brute force RSA-2048: requires private key
  - Without private key, cannot recover K
  - Even if attacker has EK, cannot decrypt K
Result: ✓ PROTECTED
  - Only authorized receiver can get K
  - Brute force infeasible (no known RSA break)


ATTACK 6: Replay Attack (Reused Message)
────────────────────────────────────────
Attacker: Captures encrypted file, resends it
Concern: Receiver thinks it's new message

Defense: Content-based integrity verification
  - System doesn't include timestamps
  - File content verified via signature
  - If replayed identical file: signature still valid
  - If modified file added with timestamp: sig fails
Usage: Add application-level encryption/metadata
  - System guarantees content integrity
  - App can add timestamp/nonce if needed
  - This system focuses on file integrity
Note: Application-level concern beyond core crypto


ATTACK 7: Bit Flipping in Ciphertext
───────────────────────────────────
Attacker: Flips specific bits in C hoping to cause specific plaintext
Example: Tries to flip "$1000000" to "$9999999" by bit manipulation

Defense: Signature verification + Hash determinism
  - Flipping bit in C affects decrypted plaintext
  - But changes appear random (encryption property)
  - Recomputed hash completely changes
  - signature verification fails
  - Attacker cannot predict result of bit flip
Result: ✓ PROTECTED
  - Random change detection
  - Cannot forge matching signature
  - Attempted manipulation detected


ATTACK 8: IV Reuse with Same Key
────────────────────────────────
Threat: If same K used with same IV twice: streams XOR
        Reveals plaintext patterns

Defense: Random IV generation per encryption
  - Each encryption generates new random IV
  - System enforces unique session key per file
  - Combination of unique K + unique IV per use
  - Two encryptions: either different K or different IV
  - IV reuse attack impossible with this system
Result: ✓ PROTECTED
  - No IV reuse with same key
  - IV reuse vulnerabilities cannot occur


ATTACK 9: Side-Channel Attacks
──────────────────────────────
Threat: Timing analysis, power analysis, cache attacks

Defense: Use timing-resistant crypto library
  - cryptography library uses constant-time ops
  - Hash comparison resistant to timing attacks
  - Library hardened against side channels
  - Runs on CPU with hardware acceleration
  - Hardware crypto (AES-NI) resists side channels
Result: ✓ PROTECTED (at library level)
  - Implementations use best practices
  - Hardware acceleration prevents many attacks


ATTACK 10: Key Exposure (Private Key Compromised)
─────────────────────────────────────────────────
Worst Case: Attacker obtains receiver's private key
Impact: All past and future files can be decrypted

Mitigation Strategies (not in core system):
  - Regular key rotation
  - Use Hardware Security Module (HSM)
  - Separate keys per time period
  - Perfect Forward Secrecy (ephemeral keys)
  - Hierarchical key derivation
Note: Once private key is compromised, no crypto helps
Better Practice: Protect private keys with OS security
  - Filesystem encryption
  - OS access controls
  - Secure key storage
Result: ⚠ MANAGED (at infrastructure level)
  - System provides strong crypto
  - Private key protection is user responsibility
"""

# ==============================================================================
# 5. CRYPTOGRAPHIC STANDARDS AND PARAMETERS
# ==============================================================================

CRYPTO_STANDARDS = """
╔════════════════════════════════════════════════════════════════════════╗
║              CRYPTOGRAPHIC STANDARDS & PARAMETERS                     ║
╚════════════════════════════════════════════════════════════════════════╝

AES-256-CBC ENCRYPTION
─────────────────────
Standard: FIPS 197 (Federal Information Processing Standards)
Algorithm: Advanced Encryption Standard
Key Size: 256 bits (32 bytes) - AES-256 variant
  - 128-bit keys: acceptable, good security
  - 192-bit keys: good balance
  - 256-bit keys: maximum, recommended for long-term
IV Size: 128 bits (16 bytes) = AES block size
  - IV must be random and unpredictable
  - IV does NOT need to be secret (transmitted in plaintext)
  - IV prevents pattern analysis (different ciphertexts for same plaintext)
Mode: CBC (Cipher Block Chaining)
  - Ciphertext block depends on previous block
  - Prevents ECB weakness (identical plaintext → identical ciphertext)
  - Semantic security: CPA-secure (indistinguishable ciphertexts)
Padding: PKCS#7
  - Handles non-block-size plaintexts
  - Adds n bytes of value n (where n = padding length)
  - Removes ambiguity at decryption
Authentication: Digital signature provides integrity (not AEAD)
  - Note: CBC mode alone doesn't provide authentication
  - System uses separate signature for authentication
  - Consider AES-GCM for future (provides both)

Performance: 
  - Modern CPUs: AES-NI hardware acceleration
  - Throughput: several GB/second certified
  - Suitable for large file encryption


RSA-2048 KEY ENCRYPTION & SIGNING
──────────────────────────────────
Standard: PKCS #1 v2.2 (RFC 8017)
Algorithm: RSA (Rivest-Shamir-Adleman)
Key Size: 2048 bits
  - 1024-bit: deprecated (factorizable)
  - 2048-bit: recommended minimum (secure until ~2030-2040)
  - 3072-bit: future-proof
  - 4096-bit: maximum practical (slow, rarely needed)
RSA-n: n = p × q (two large primes)
  - Private key: (d, n)
  - Public key: (e, n) where e = 65537 (typical)
  - e chosen for efficiency and security

Encryption Padding: OAEP (Optimal Asymmetric Encryption Padding)
  - Standard: RFC 8017 (PKCS#1 v2.2)
  - Hash: SHA-256
  - MGF: MGF1 with SHA-256
  - Label: empty string
  - Advantages: 
    * Semantic security (randomized encryption)
    * Resistant to chosen-ciphertext attacks (CCA)
    * Superior to PKCS#1 v1.5 (which has known attacks)

Signature Padding: PKCS#1 v1.5
  - Deterministic signing
  - Hash: SHA-256 (input is pre-computed hash)
  - Compatible with FIPS standards
  - Alternative: PSS (probabilistic) - see Future

Signature Hash: SHA-256
  - Input to signature: hash of plaintext
  - NOT plaintext directly
  - Why: efficiency and security properties

Security Level:
  - 2048-bit RSA ≈ 112 bits security (classical)
  - Against quantum: much weaker (see Future Enhancement)


SHA-256 HASHING
───────────────
Standard: FIPS 180-4 (Secure Hash Algorithm)
Algorithm: SHA-256 (part of SHA-2 family)
Output Size: 256 bits (32 bytes)
  - 128-bit SHA-1: DEPRECATED (collision attacks found)
  - 160-bit SHA-1: DO NOT USE
  - 256-bit SHA-256: RECOMMENDED
  - 384-bit SHA-384: Also good
  - 512-bit SHA-512: Also good

Properties:
  - Cryptographically secure: one-way function
  - Collision resistant: cannot find two inputs → same output
  - Avalanche effect: 1 bit change → completely different output
  - Deterministic: same input → always same output
  - Fast: suitable for large files

Use Cases in System:
  - File integrity verification
  - Digital signature input (hash of file)
  - OAEP hash in RSA encryption
  - MGF1 hash for key derivation (OAEP)

Security: 
  - 256-bit output resistant to birthday attacks
  - No practical attacks known
  - Expected security life: decades


RANDOM NUMBER GENERATION
────────────────────────
Sources:
  - cryptography.hazmat.primitives.os.urandom()
  - Uses OS /dev/urandom (Linux) or CryptGenRandom (Windows)
  - Cryptographically secure RNG

Used For:
  - Session key generation: 32 random bytes
  - IV generation: 16 random bytes per encryption
  - RSA key generation: seed for prime generation

Critical Properties:
  - Unpredictable: attacker cannot guess next bytes
  - Non-repeating: sequences never repeat
  - Sufficient entropy: random pool well-seeded
  - Hardware sources: USB randomness devices optional


SUMMARY OF SECURITY LEVELS
──────────────────────────
AES-256:        256 bits equivalent symmetric
RSA-2048:       ~112 bits equivalent strength
SHA-256:        128 bits collision resistance
Combined:       Bottleneck is RSA-2048 (112 bits)
Equivalent To:  AES-112 security
Practical:      Secure for 20-30 years
Will Break:     Quantum computers with large n
                (Shor's algorithm: polynomial RSA)

Recommendation:
  - For long-term (20+ years): consider RSA-3072 or 4096
  - For institutional data: use RSA-3072
  - For research: plan quantum-resistant migration
"""

# ==============================================================================
# 6. MODULE REFERENCE AND DEPENDENCIES
# ==============================================================================

MODULE_REFERENCE = """
╔════════════════════════════════════════════════════════════════════════╗
║                      MODULE REFERENCE                                 ║
╚════════════════════════════════════════════════════════════════════════╝

hashing.py
──────────
Functions:
  - compute_hash(data: bytes) → bytes
    Input: Any bytes
    Output: 32-byte SHA-256 hash
    Used for file integrity verification

  - compute_hash_hex(data: bytes) → str
    Input: Any bytes
    Output: 64-character hex string representation
    Used for display/logging

  - verify_hash(data: bytes, expected_hash: bytes) → bool
    Input: Data and expected hash
    Output: True if match, False otherwise
    Security: Constant-time comparison (resistant to timing attacks)

Dependencies: hashlib (standard library)
Threats: Does not verify data integrity by itself
         Must use with signatures


key_management.py
─────────────────
Functions:
  - generate_rsa_keypair() → (private, public)
    Generates RSA-2048 key pair
    Private key: contains p, q, d, dp, dq, qinv
    Public key: contains n, e
    Slow operation (1-2 seconds)
    Should be done once per identity

  - generate_ecc_keypair() → (private, public)
    Generates ECC key pair (P-256 curve)
    Smaller keys than RSA (256 bits vs 2048)
    Faster operations
    Not used in signatures in this system (for future use)

  - save_private_key(key, filepath, password=None)
    Saves private key in PEM format
    Optional password encryption (PKCS8)
    Should be stored securely (filesystem encryption, HSM)

  - load_private_key(filepath, password=None)
    Loads private key from PEM file
    Requires correct password if encrypted
    Should only load when needed

  - save_public_key(key, filepath)
    Saves public key in PEM format
    Can be distributed publicly
    Necessary for receivers to decrypt

  - load_public_key(filepath)
    Loads public key from PEM file
    Fast operation

Dependencies: cryptography.hazmat.primitives.asymmetric


encryption.py
──────────────
Functions:
  - generate_session_key() → bytes
    Returns 32 random bytes (256-bit AES key)
    CRITICAL: Use different key for each file
    Reuse would compromise security

  - generate_iv() → bytes
    Returns 16 random bytes (128-bit IV)
    Required for each encryption operation
    Can be sent in plaintext with ciphertext

  - encrypt(plaintext: bytes, session_key: bytes) → (iv, ciphertext)
    Encrypts data with AES-256-CBC
    Automatically generates random IV
    Returns IV and ciphertext (both needed for decryption)

  - decrypt(ciphertext: bytes, session_key: bytes, iv: bytes) → bytes
    Decrypts AES-256-CBC ciphertext
    Removes PKCS7 padding automatically
    Raises exception if padding is invalid

Dependencies: cryptography.hazmat.primitives.ciphers,
              cryptography.hazmat.primitives.padding


signature.py
─────────────
Functions:
  - rsa_sign(data_hash: bytes, private_key) → bytes
    Creates RSA signature of hash
    Input: SHA-256 hash (32 bytes), private key
    Output: Signature (~256 bytes for RSA-2048)

  - rsa_verify(data_hash: bytes, signature: bytes, public_key) → bool
    Verifies RSA signature
    True if signature is valid, False otherwise
    Does not raise exception

  - ecdsa_sign(data_hash: bytes, private_key) → bytes
    Creates ECDSA signature of hash
    For ECC keys (P-256 produces ~64-byte sig)

  - ecdsa_verify(data_hash: bytes, signature: bytes, public_key) → bool
    Verifies ECDSA signature
    Returns boolean result

  - sign(data_hash: bytes, private_key) → bytes
    Auto-detects key type (RSA or ECC) and signs
    Convenient for generic code

  - verify(data_hash: bytes, signature: bytes, public_key) → bool
    Auto-detects key type (RSA or ECC) and verifies
    Convenient for generic code

Dependencies: cryptography.hazmat.primitives.asymmetric


public_key_encryption.py
────────────────────────
Functions:
  - encrypt_session_key(session_key: bytes, public_key) → bytes
    Encrypts AES session key with RSA public key
    Uses OAEP padding (resistant to attacks)
    Output: ~256 bytes for RSA-2048

  - decrypt_session_key(encrypted_key: bytes, private_key) → bytes
    Decrypts AES session key with RSA private key
    Recovers original session key
    Only holder of private key can decrypt

Dependencies: cryptography.hazmat.primitives.asymmetric.padding


file_handler.py
────────────────
Functions:
  - encrypt_file(filepath, output, receiver_pub, sender_priv) → dict
    Complete encryption workflow
    Reads file, computes hash, signs, encrypts
    Returns metadata (size, hash, status)

  - decrypt_file(filepath, output, receiver_priv, sender_pub) → dict
    Complete decryption workflow
    Decrypts, verifies signature, writes file
    Returns status (valid, tampered, etc)

  - _write_encrypted_package(filepath, iv, enc_key, ciphertext, sig)
    Internal: Writes encrypted data to file
    Follows format specification

  - _read_encrypted_package(filepath) → (iv, enc_key, ct, sig)
    Internal: Reads encrypted data from file
    Validates format header

  - _extract_file_and_signature(data, sig_size) → (file, sig)
    Internal: Separates file from signature
    Uses signature size to split data

Dependencies: All other modules (hashing, encryption, etc)


══════════════════════════════════════════════════════════════════════════

DEPENDENCY CHAIN
────────────────

Users
  ↓
main.py / examples.py
  ↓
SecureFileHandler (file_handler.py)
  ├─→ HashModule (hashing.py)
  ├─→ EncryptionModule (encryption.py)
  ├─→ SignatureModule (signature.py)
  ├─→ PublicKeyEncryption (public_key_encryption.py)
  └─→ KeyManager (key_management.py)
        ↓
        cryptography library
              ↓
              OpenSSL / Hardware crypto
"""

# ==============================================================================
# Print all documentation
# ==============================================================================

if __name__ == "__main__":
    print(ARCHITECTURE_OVERVIEW)
    print("\n" + "="*75)
    print(ENCRYPTION_WORKFLOW)
    print("\n" + "="*75)
    print(DECRYPTION_WORKFLOW)
    print("\n" + "="*75)
    print(ATTACK_SCENARIOS)
    print("\n" + "="*75)
    print(CRYPTO_STANDARDS)
    print("\n" + "="*75)
    print(MODULE_REFERENCE)
