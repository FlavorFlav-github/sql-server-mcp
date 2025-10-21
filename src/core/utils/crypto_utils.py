from cryptography.fernet import Fernet

from config.settings import PASSWORD_ENCRYPTION_KEY


class CryptoUtils:
    """
    Utility class for encrypting and decrypting sensitive data
    such as server passwords before storing them in the metadata DB.
    """

    def __init__(self, key: str | None = None):
        # Get the encryption key from environment or generate a new one
        raw_key = key or PASSWORD_ENCRYPTION_KEY
        if not raw_key:
            raise ValueError(
                "Missing ENCRYPTION_KEY. Generate one using CryptoUtils.generate_key()"
            )

        # Fernet expects a URL-safe base64 key
        self.fernet = Fernet(raw_key.encode() if not raw_key.startswith("gAAAA") else raw_key)

    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet encryption key (store this securely!)."""
        return Fernet.generate_key().decode()

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64 encoded ciphertext."""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64 encoded ciphertext."""
        return self.fernet.decrypt(ciphertext.encode()).decode()