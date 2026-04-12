"""
Quick Start Guide - Basic Usage Examples
=========================================

This file demonstrates simple usage patterns for the secure file storage system.
"""

from key_management import KeyManager
from file_handler import SecureFileHandler
import os


# ==============================================================================
# EXAMPLE 1: Simple File Encryption and Decryption
# ==============================================================================

print("\n" + "="*70)
print("EXAMPLE 1: Simple File Encryption and Decryption")
print("="*70)

# Step 1: Generate key pairs (normally done once and stored securely)
print("\n[1] Generating RSA-2048 key pairs...")
sender_private, sender_public = KeyManager.generate_rsa_keypair()
receiver_private, receiver_public = KeyManager.generate_rsa_keypair()
print("✓ Keys generated")

# Step 2: Create a sample file to encrypt
print("\n[2] Creating sample file...")
sample_file = "example1_secret.txt"
with open(sample_file, 'wb') as f:
    f.write(b"This is my secret message that needs encryption!")
print(f"✓ Created: {sample_file}")

# Step 3: Encrypt the file
print("\n[3] Encrypting file...")
encrypted_file = "example1_secret.enc"
info = SecureFileHandler.encrypt_file(
    sample_file,
    encrypted_file,
    receiver_public,
    sender_private
)
print(f"✓ Encrypted: {info['encrypted_filepath']}")
print(f"  File size: {info['original_size']} → {info['ciphertext_size']} bytes")

# Step 4: Decrypt the file
print("\n[4] Decrypting file...")
decrypted_file = "example1_secret_decrypted.txt"
result = SecureFileHandler.decrypt_file(
    encrypted_file,
    decrypted_file,
    receiver_private,
    sender_public
)

if result['signature_valid']:
    print(f"✓ Decrypted: {result['decrypted_filepath']}")
    print("✓ Signature verified - file is authentic")
    with open(decrypted_file, 'rb') as f:
        print(f"✓ Content: {f.read().decode()}")
else:
    print("✗ Signature verification failed - file may be tampered")

# Cleanup
os.remove(sample_file)
os.remove(encrypted_file)
os.remove(decrypted_file)
print("\n✓ Example 1 complete")


# ==============================================================================
# EXAMPLE 2: Key Storage and Reuse
# ==============================================================================

print("\n" + "="*70)
print("EXAMPLE 2: Saving and Loading Keys")
print("="*70)

# Generate keys
print("\n[1] Generating keys...")
alice_private, alice_public = KeyManager.generate_rsa_keypair()
bob_private, bob_public = KeyManager.generate_rsa_keypair()
print("✓ Keys generated")

# Save keys (without password for simplicity)
print("\n[2] Saving keys...")
KeyManager.save_private_key(alice_private, "alice_private.pem")
KeyManager.save_public_key(alice_public, "alice_public.pem")
KeyManager.save_private_key(bob_private, "bob_private.pem")
KeyManager.save_public_key(bob_public, "bob_public.pem")
print("✓ Keys saved to PEM files")

# Load keys back
print("\n[3] Loading keys from files...")
alice_priv_loaded = KeyManager.load_private_key("alice_private.pem")
bob_pub_loaded = KeyManager.load_public_key("bob_public.pem")
print("✓ Keys loaded successfully")

# Use loaded keys for encryption
print("\n[4] Encrypting with loaded keys...")
test_file = "example2_test.txt"
with open(test_file, 'wb') as f:
    f.write(b"Message from Alice to Bob")

encrypted = "example2_test.enc"
SecureFileHandler.encrypt_file(
    test_file,
    encrypted,
    bob_pub_loaded,
    alice_priv_loaded
)
print(f"✓ File encrypted using loaded keys")

# Decrypt with loaded keys
print("\n[5] Decrypting with loaded keys...")
bob_priv_loaded = KeyManager.load_private_key("bob_private.pem")
alice_pub_loaded = KeyManager.load_public_key("alice_public.pem")

decrypted = "example2_test_decrypted.txt"
result = SecureFileHandler.decrypt_file(
    encrypted,
    decrypted,
    bob_priv_loaded,
    alice_pub_loaded
)

if result['signature_valid']:
    print("✓ Successfully decrypted with loaded keys")
    with open(decrypted, 'rb') as f:
        print(f"✓ Message: {f.read().decode()}")
else:
    print("✗ Decryption failed")

# Cleanup
for f in [test_file, encrypted, decrypted, 
          "alice_private.pem", "alice_public.pem",
          "bob_private.pem", "bob_public.pem"]:
    if os.path.exists(f):
        os.remove(f)

print("\n✓ Example 2 complete")


# ==============================================================================
# EXAMPLE 3: Detecting Tampering
# ==============================================================================

print("\n" + "="*70)
print("EXAMPLE 3: Detecting File Tampering")
print("="*70)

# Generate keys
print("\n[1] Generating keys...")
sender_private, sender_public = KeyManager.generate_rsa_keypair()
receiver_private, receiver_public = KeyManager.generate_rsa_keypair()
print("✓ Keys generated")

# Create and encrypt a file
print("\n[2] Creating and encrypting file...")
important_file = "example3_important.txt"
with open(important_file, 'wb') as f:
    f.write(b"CONFIDENTIAL: This is important data")

encrypted_file = "example3_important.enc"
SecureFileHandler.encrypt_file(
    important_file,
    encrypted_file,
    receiver_public,
    sender_private
)
print(f"✓ File encrypted")

# Intentionally corrupt the encrypted file
print("\n[3] Tampering with encrypted file by flipping some bits...")
with open(encrypted_file, 'r+b') as f:
    f.seek(100)  # Seek to middle of file
    data = bytearray(f.read(4))
    for i in range(len(data)):
        data[i] ^= 0x01  # Flip every bit
    f.seek(100)
    f.write(data)
    
print("✓ File has been tampered with")

# Try to decrypt the tampered file
print("\n[4] Attempting to decrypt tampered file...")
decrypted_file = "example3_important_decrypted.txt"

try:
    result = SecureFileHandler.decrypt_file(
        encrypted_file,
        decrypted_file,
        receiver_private,
        sender_public
    )
    
    if result['signature_valid']:
        print("✗ ERROR: Signature verified despite tampering!")
    else:
        print("✓ SUCCESS: Tampering detected!")
        print(f"  Signature valid: {result['signature_valid']}")
        print(f"  File rejected: YES")
        
except Exception as e:
    print(f"✓ Decryption failed (tampering detected)")
    print(f"  Error type: {type(e).__name__}")

# Cleanup
for f in [important_file, encrypted_file]:
    if os.path.exists(f):
        os.remove(f)

print("\n✓ Example 3 complete")


# ==============================================================================
# EXAMPLE 4: Multi-User Scenarios
# ==============================================================================

print("\n" + "="*70)
print("EXAMPLE 4: Multi-User Secure Communication")
print("="*70)

print("\n[Scenario] A company wants to send confidential documents:")
print("  - Alice (HR) sends private documents to Charlie (CEO)")
print("  - Charlie wants to verify it's from Alice")
print("  - No one else should be able to read it")

# Generate keys for three users
print("\n[1] Generating keys for all users...")
alice_private, alice_public = KeyManager.generate_rsa_keypair()
bob_private, bob_public = KeyManager.generate_rsa_keypair()
charlie_private, charlie_public = KeyManager.generate_rsa_keypair()
print("✓ Alice, Bob, and Charlie have secure key pairs")

# Alice wants to send a file to Charlie
print("\n[2] Alice encrypts sensitive document for Charlie...")
document = "example4_hr_document.txt"
with open(document, 'wb') as f:
    f.write(b"CONFIDENTIAL - Employee Salary Information for CEO Review")

encrypted_doc = "example4_hr_document.enc"
SecureFileHandler.encrypt_file(
    document,
    encrypted_doc,
    charlie_public,  # Only Charlie can decrypt
    alice_private    # Alice signs it
)
print(f"✓ Document encrypted for Charlie, signed by Alice")

# Try: Bob tries to read it (should fail - wrong private key)
print("\n[3] TEST: Bob tries to read the encrypted document...")
try:
    result = SecureFileHandler.decrypt_file(
        encrypted_doc,
        "attempt_fail.txt",
        bob_private,      # Bob's key won't work
        alice_public
    )
    print("✗ Bob was able to decrypt (BAD!)")
except:
    print("✓ Bob cannot decrypt (correct - only Charlie can)")

# Charlie receives and decrypts the file
print("\n[4] Charlie receives and opens the document...")
charlie_doc = "example4_hr_document_decrypted.txt"
result = SecureFileHandler.decrypt_file(
    encrypted_doc,
    charlie_doc,
    charlie_private,   # Only Charlie can decrypt
    alice_public       # Verify it's from Alice
)

if result['signature_valid']:
    print("✓ Document decrypted and authenticated")
    with open(charlie_doc, 'rb') as f:
        content = f.read().decode()
    print(f"✓ Content: {content}")
    print("✓ Charlie is confident this is from Alice")
else:
    print("✗ Signature verification failed - reject document")

# Cleanup
for f in [document, encrypted_doc, charlie_doc]:
    if os.path.exists(f):
        os.remove(f)
try:
    os.remove("attempt_fail.txt")
except:
    pass

print("\n✓ Example 4 complete - Multi-user scenario works correctly")


print("\n" + "="*70)
print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
print("="*70 + "\n")

print("""
SUMMARY OF USAGE PATTERNS:

1. ONE-TIME SETUP:
   - Generate keys: KeyManager.generate_rsa_keypair()
   - Save keys: KeyManager.save_private_key(key, "file.pem")

2. ENCRYPTION:
   - Encrypt: SecureFileHandler.encrypt_file(input, output, receiver_pub, sender_priv)

3. DECRYPTION:
   - Decrypt: SecureFileHandler.decrypt_file(input, output, receiver_priv, sender_pub)
   - Check: if result['signature_valid']: ...

4. KEY MANAGEMENT:
   - Load: key = KeyManager.load_private_key("file.pem")
   - Reuse keys across multiple encryption operations

5. SECURITY PROPERTIES GUARANTEED:
   ✓ Only intended receiver can decrypt (asymmetric encryption)
   ✓ Sender cannot deny creating file (digital signature)
   ✓ Any tampering is detected (signature verification)
   ✓ Each encryption uses unique session key and IV
   ✓ Support for large files efficiently
""")
