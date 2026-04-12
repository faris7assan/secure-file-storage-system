import hashlib


class HashModule:
    @staticmethod
    def sha256(data):
        return hashlib.sha256(data).digest()

    @staticmethod
    def sha256_hex(data):
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def compute_file_hash(filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.digest()

    @staticmethod
    def compute_file_hash_hex(filepath):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
