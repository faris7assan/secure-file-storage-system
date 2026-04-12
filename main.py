"""
Secure File Storage System Using Hybrid Cryptography
=====================================================

Complete Example with Test Cases

Demonstrates:
1. Key generation (RSA)
2. File encryption with hybrid cryptography
3. File decryption and signature verification
4. Tamper detection
5. Wrong key detection

Author: Cryptography System
Date: 2024
"""

import os
import sys
from key_management import KeyManager
from file_handler import SecureFileHandler


def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_step(step_number, description):
    print(f"\n[Step {step_number}] {description}")
    print("-" * 70)


def test_case_1_valid_encryption_decryption():
    print_header("TEST CASE 1: Valid Encryption and Decryption")
    
    test_dir = "test_case_1"
    os.makedirs(test_dir, exist_ok=True)
    print_step(1, "Creating test file")
    test_file = os.path.join(test_dir, "secret_message.txt")
    test_content = b"This is a highly confidential message that needs encryption."
    with open(test_file, 'wb') as f:
        f.write(test_content)
    print(f"✓ Created test file: {test_file}")
    print(f"  Content: {test_content.decode()}")
    print(f"  Size: {len(test_content)} bytes")
    print_step(2, "Generating RSA key pairs")
    sender_private, sender_public = KeyManager.generate_rsa_keypair()
    receiver_private, receiver_public = KeyManager.generate_rsa_keypair()
    print("✓ Sender private/public keys generated")
    print("✓ Receiver private/public keys generated")
    print_step(3, "Encrypting file")
    encrypted_file = os.path.join(test_dir, "secret_message.enc")
    encrypt_info = SecureFileHandler.encrypt_file(
        test_file,
        encrypted_file,
        receiver_public,
        sender_private
    )
    print("✓ File encrypted successfully")
    print(f"  Original size: {encrypt_info['original_size']} bytes")
    print(f"  Encrypted size: {encrypt_info['ciphertext_size']} bytes")
    print(f"  File hash: {encrypt_info['file_hash'][:16]}...")
    print(f"  Signature size: {encrypt_info['signature_size']} bytes")
    print_step(4, "Decrypting file")
    decrypted_file = os.path.join(test_dir, "secret_message_decrypted.txt")
    decrypt_info = SecureFileHandler.decrypt_file(
        encrypted_file,
        decrypted_file,
        receiver_private,
        sender_public
    )
    print("✓ File decrypted successfully")
    print(f"  Decrypted size: {decrypt_info['decrypted_size']} bytes")
    print(f"  File hash: {decrypt_info['file_hash'][:16]}...")
    print(f"  Signature valid: {decrypt_info['signature_valid']}")
    print_step(5, "Verifying decrypted content")
    with open(decrypted_file, 'rb') as f:
        decrypted_content = f.read()
    
    if decrypted_content == test_content:
        print("✓ Decrypted content matches original")
        print("✓ TEST CASE 1 PASSED")
        return True
    else:
        print("✗ Content mismatch!")
        print("✗ TEST CASE 1 FAILED")
        return False


def test_case_2_tampered_file_detection():
    print_header("TEST CASE 2: Tampered File Detection")
    
    test_dir = "test_case_2"
    os.makedirs(test_dir, exist_ok=True)
    print_step(1, "Creating test file")
    test_file = os.path.join(test_dir, "document.pdf")
    test_content = b"Important financial document: $1,000,000 approved"
    with open(test_file, 'wb') as f:
        f.write(test_content)
    print(f"✓ Created test file: {test_file}")
    print_step(2, "Generating RSA key pairs")
    sender_private, sender_public = KeyManager.generate_rsa_keypair()
    receiver_private, receiver_public = KeyManager.generate_rsa_keypair()
    print("✓ Keys generated")
    print_step(3, "Encrypting file")
    encrypted_file = os.path.join(test_dir, "document.enc")
    SecureFileHandler.encrypt_file(
        test_file,
        encrypted_file,
        receiver_public,
        sender_private
    )
    print("✓ File encrypted")
    print_step(4, "Tampering with encrypted file")
    with open(encrypted_file, 'r+b') as f:
        f.seek(50)
        data = bytearray(f.read(10))
        data[0] ^= 0xFF
        f.seek(50)
        f.write(data)
    print("✓ Encrypted file modified (simulating tampering)")
    print_step(5, "Attempting to decrypt tampered file")
    decrypted_file = os.path.join(test_dir, "document_decrypted.pdf")
    
    try:
        decrypt_info = SecureFileHandler.decrypt_file(
            encrypted_file,
            decrypted_file,
            receiver_private,
            sender_public
        )
        
        if decrypt_info['tampered']:
            print("✓ Tampering detected!")
            print(f"  Signature valid: {decrypt_info['signature_valid']}")
            print("✓ TEST CASE 2 PASSED - Tamper Detection Works")
            return True
        else:
            print("✗ Tampering not detected!")
            print("✗ TEST CASE 2 FAILED")
            return False
    except Exception as e:
        print(f"✓ Decryption failed as expected: {type(e).__name__}")
        print("✓ TEST CASE 2 PASSED - Tampering Prevented")
        return True


def test_case_3_wrong_receiver_key():
    print_header("TEST CASE 3: Wrong Receiver Private Key")
    
    test_dir = "test_case_3"
    os.makedirs(test_dir, exist_ok=True)
    print_step(1, "Creating test file")
    test_file = os.path.join(test_dir, "secret.txt")
    test_content = b"Secret message for specific receiver"
    with open(test_file, 'wb') as f:
        f.write(test_content)
    print(f"✓ Created test file")
    
    print_step(2, "Generating RSA key pairs")
    sender_private, sender_public = KeyManager.generate_rsa_keypair()
    receiver_private, receiver_public = KeyManager.generate_rsa_keypair()
    wrong_receiver_private, _ = KeyManager.generate_rsa_keypair()
    print("✓ Legitimate receiver keys generated")
    print("✓ Wrong receiver keys generated")
    print_step(3, "Encrypting for legitimate receiver")
    encrypted_file = os.path.join(test_dir, "secret.enc")
    SecureFileHandler.encrypt_file(
        test_file,
        encrypted_file,
        receiver_public,
        sender_private
    )
    print("✓ File encrypted with receiver's public key")
    print_step(4, "Attempting decryption with wrong private key")
    decrypted_file = os.path.join(test_dir, "secret_decrypted.txt")
    
    try:
        decrypt_info = SecureFileHandler.decrypt_file(
            encrypted_file,
            decrypted_file,
            wrong_receiver_private,
            sender_public
        )
        print("✗ Decryption succeeded (should have failed)")
        print("✗ TEST CASE 3 FAILED")
        return False
    except Exception as e:
        print(f"✓ Decryption failed as expected: {type(e).__name__}")
        print("✓ TEST CASE 3 PASSED - Wrong Key Detected")
        return True


def test_case_4_wrong_sender_key():
    print_header("TEST CASE 4: Wrong Sender Public Key")
    
    test_dir = "test_case_4"
    os.makedirs(test_dir, exist_ok=True)
    print_step(1, "Creating test file")
    test_file = os.path.join(test_dir, "contract.txt")
    test_content = b"This contract is signed by Alice"
    with open(test_file, 'wb') as f:
        f.write(test_content)
    print(f"✓ Created test file")
    
    print_step(2, "Generating key pairs")
    sender_private, sender_public = KeyManager.generate_rsa_keypair()
    wrong_sender_private, wrong_sender_public = KeyManager.generate_rsa_keypair()
    receiver_private, receiver_public = KeyManager.generate_rsa_keypair()
    print("✓ Legitimate sender keys generated")
    print("✓ Wrong sender keys generated")
    print("✓ Receiver keys generated")
    print_step(3, "Encrypting file (signed by legitimate sender)")
    encrypted_file = os.path.join(test_dir, "contract.enc")
    SecureFileHandler.encrypt_file(
        test_file,
        encrypted_file,
        receiver_public,
        sender_private
    )
    print("✓ File encrypted and signed")
    print_step(4, "Decrypting with wrong sender's public key")
    decrypted_file = os.path.join(test_dir, "contract_decrypted.txt")
    
    decrypt_info = SecureFileHandler.decrypt_file(
        encrypted_file,
        decrypted_file,
        receiver_private,
        wrong_sender_public
    )
    
    if not decrypt_info['signature_valid'] and decrypt_info['tampered']:
        print(f"✓ Signature verification FAILED (as expected)")
        print(f"  Signature valid: {decrypt_info['signature_valid']}")
        print(f"  File marked as tampered: {decrypt_info['tampered']}")
        print("✓ TEST CASE 4 PASSED - Wrong Signature Key Detected")
        return True
    else:
        print("✗ Signature verification succeeded (should have failed)")
        print("✗ TEST CASE 4 FAILED")
        return False


def test_case_5_file_size_variations():
    print_header("TEST CASE 5: File Size Variations")
    
    test_dir = "test_case_5"
    os.makedirs(test_dir, exist_ok=True)
    print_step(1, "Generating key pairs")
    sender_private, sender_public = KeyManager.generate_rsa_keypair()
    receiver_private, receiver_public = KeyManager.generate_rsa_keypair()
    print("✓ Keys generated")
    file_sizes = [
        (16, "Tiny (16 bytes)"),
        (1024, "Small (1 KB)"),
        (1024 * 100, "Medium (100 KB)"),
    ]
    
    all_passed = True
    for size, description in file_sizes:
        print_step(2, f"Testing {description}")
        test_file = os.path.join(test_dir, f"file_{size}.bin")
        test_content = os.urandom(size)
        with open(test_file, 'wb') as f:
            f.write(test_content)
        encrypted_file = os.path.join(test_dir, f"file_{size}.enc")
        SecureFileHandler.encrypt_file(
            test_file,
            encrypted_file,
            receiver_public,
            sender_private
        )
        decrypted_file = os.path.join(test_dir, f"file_{size}_dec.bin")
        decrypt_info = SecureFileHandler.decrypt_file(
            encrypted_file,
            decrypted_file,
            receiver_private,
            sender_public
        )
        with open(decrypted_file, 'rb') as f:
            decrypted = f.read()
        
        if decrypted == test_content and decrypt_info['signature_valid']:
            print(f"  ✓ {description} - Success")
        else:
            print(f"  ✗ {description} - Failed")
            all_passed = False
    
    if all_passed:
        print("\n✓ TEST CASE 5 PASSED - All sizes handled correctly")
        return True
    else:
        print("\n✗ TEST CASE 5 FAILED")
        return False


def run_all_tests():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + "  SECURE FILE STORAGE SYSTEM - COMPLETE TEST SUITE  ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = []
    results.append(("Valid Encryption/Decryption", test_case_1_valid_encryption_decryption()))
    results.append(("Tampered File Detection", test_case_2_tampered_file_detection()))
    results.append(("Wrong Receiver Key", test_case_3_wrong_receiver_key()))
    results.append(("Wrong Sender Key", test_case_4_wrong_sender_key()))
    results.append(("File Size Variations", test_case_5_file_size_variations()))
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} : {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 70 + "\n")
    
    return passed == total





if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
