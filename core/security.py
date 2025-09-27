import json
import base64
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class SecurityManager:
    def __init__(self, encryption_key: str = None):
        """
        Initializes the security manager and secure data store.
        If no encryption key is provided, a new one is generated.
        """
        if encryption_key:
            # Use the provided key after decoding it from base64
            key = base64.urlsafe_b64decode(encryption_key)
        else:
            print("Warning: No encryption key found. Generating a new one. "
                  "Please save this key in your config file for data persistence.")
            key = Fernet.generate_key()

        self.key = key
        self.cipher = Fernet(self.key)
        # In-memory SQLite for now; will be configured later
        self.engine = create_engine('sqlite:///:memory:')

    def get_encryption_key(self) -> str:
        """Returns the current encryption key, base64 encoded."""
        return base64.urlsafe_b64encode(self.key).decode()

    def encrypt_data(self, data: dict) -> str:
        """Encrypts a dictionary into a secure string."""
        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary.")
        json_data = json.dumps(data)
        encrypted_bytes = self.cipher.encrypt(json_data.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def decrypt_data(self, encrypted_data: str) -> dict:
        """Decrypts a secure string back into a dictionary."""
        if not isinstance(encrypted_data, str):
            raise TypeError("Encrypted data must be a string.")
        decrypted_bytes = self.cipher.decrypt(encrypted_data.encode('utf-8'))
        json_data = decrypted_bytes.decode('utf-8')
        return json.loads(json_data)

class DataRecord(Base):
    __tablename__ = 'data_records'

    id = Column(String, primary_key=True)
    source_agent = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    encrypted_content = Column(Text, nullable=False)
    tags = Column(String)  # JSON-formatted tags
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sensitivity_level = Column(String, default='normal')  # e.g., low, normal, high, critical

# Example usage for verification
if __name__ == '__main__':
    # 1. Test with auto-generated key
    print("--- Testing with auto-generated key ---")
    secure_store_auto = SecureDataStore()
    new_key = secure_store_auto.get_encryption_key()
    print(f"Generated Key: {new_key}")

    original_data = {"user": "test", "password": "supersecretpassword", "id": 123}
    print("Original Data:", original_data)

    encrypted = secure_store_auto.encrypt_data(original_data)
    print("Encrypted Data:", encrypted)

    decrypted = secure_store_auto.decrypt_data(encrypted)
    print("Decrypted Data:", decrypted)
    assert original_data == decrypted
    print("Auto-key encryption/decryption test PASSED.")

    # 2. Test with a provided key
    print("\n--- Testing with a provided key ---")
    secure_store_provided = SecureDataStore(encryption_key=new_key)

    encrypted_again = secure_store_provided.encrypt_data(original_data)
    print("Encrypted Again:", encrypted_again)

    decrypted_again = secure_store_provided.decrypt_data(encrypted_again)
    print("Decrypted Again:", decrypted_again)
    assert original_data == decrypted_again
    print("Provided-key encryption/decryption test PASSED.")