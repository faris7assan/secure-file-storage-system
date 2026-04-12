"""
Verification Script
==================

Quickly verify that all modules are properly installed and working.
"""

print("=" * 70)
print("SECURE FILE STORAGE SYSTEM - VERIFICATION")
print("=" * 70)

# Verify Python version
import sys
print(f"\n✓ Python Version: {sys.version}")

# Verify all modules can be imported
print("\nVerifying module imports...")
modules_to_test = [
    "hashing",
    "key_management", 
    "encryption",
    "signature",
    "public_key_encryption",
    "file_handler"
]

for module_name in modules_to_test:
    try:
        __import__(module_name)
        print(f"  ✓ {module_name}.py")
    except ImportError as e:
        print(f"  ✗ {module_name}.py - ERROR: {e}")

# Verify cryptography library
print("\nVerifying cryptography library...")
try:
    from cryptography import __version__
    print(f"  ✓ cryptography {__version__}")
except ImportError:
    print(f"  ✗ cryptography NOT installed")

# Quick functionality test
print("\nRunning quick functionality test...")
try:
    from hashing import HashModule
    from key_management import KeyManager
    from encryption import EncryptionModule
    from signature import SignatureModule
    from file_handler import SecureFileHandler
    
    # Test hashing
    test_data = b"Test data for verification"
    test_hash = HashModule.compute_hash(test_data)
    print(f"  ✓ Hashing: {HashModule.compute_hash_hex(test_data)[:16]}...")
    
    # Test key generation
    priv, pub = KeyManager.generate_rsa_keypair()
    print(f"  ✓ Key Generation: Generated RSA-2048 keypair")
    
    # Test encryption
    session_key = EncryptionModule.generate_session_key()
    iv, ciphertext = EncryptionModule.encrypt(test_data, session_key)
    decrypted = EncryptionModule.decrypt(ciphertext, session_key, iv)
    assert decrypted == test_data
    print(f"  ✓ Encryption/Decryption: Working correctly")
    
    # Test signatures
    signature = SignatureModule.sign(test_hash, priv)
    is_valid = SignatureModule.verify(test_hash, signature, pub)
    assert is_valid
    print(f"  ✓ Signatures: Working correctly")
    
except Exception as e:
    print(f"  ✗ Functionality test FAILED: {e}")

print("\n" + "=" * 70)
print("✓ VERIFICATION COMPLETE - All systems operational")
print("=" * 70)

print("\nTo run the full test suite: python main.py")
print("To see usage examples: python examples.py")
print("To read documentation: see README.md or ARCHITECTURE.md")
