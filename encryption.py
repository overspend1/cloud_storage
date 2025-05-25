#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Encryption Module for Cloud Storage Bot

This module provides encryption and decryption functionality for the Cloud Storage Bot.
It uses Fernet symmetric encryption from the cryptography library to secure files.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class FileEncryption:
    """Handles file encryption and decryption operations."""

    def __init__(self, password):
        """Initialize with a password for encryption/decryption.

        Args:
            password (str): The password used for encryption/decryption.
        """
        self.password = password.encode()
        self.salt = os.urandom(16)  # Generate a random salt
        self.key = self._generate_key()
        self.cipher = Fernet(self.key)

    def _generate_key(self):
        """Generate a key from the password using PBKDF2.

        Returns:
            bytes: The generated key for encryption/decryption.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key

    def encrypt_file(self, file_path, output_path=None):
        """Encrypt a file using the generated key.

        Args:
            file_path (str): Path to the file to encrypt.
            output_path (str, optional): Path to save the encrypted file.
                If not provided, appends '.encrypted' to the original filename.

        Returns:
            str: Path to the encrypted file.
            bytes: The salt used for encryption (should be stored securely).
        """
        if not output_path:
            output_path = f"{file_path}.encrypted"

        # Read the file content
        with open(file_path, 'rb') as file:
            file_data = file.read()

        # Encrypt the data
        encrypted_data = self.cipher.encrypt(file_data)

        # Write the encrypted data to the output file
        with open(output_path, 'wb') as file:
            file.write(encrypted_data)

        return output_path, self.salt

    def decrypt_file(self, file_path, output_path=None, salt=None):
        """Decrypt a file using the generated key.

        Args:
            file_path (str): Path to the encrypted file.
            output_path (str, optional): Path to save the decrypted file.
                If not provided, removes '.encrypted' from the filename if present.
            salt (bytes, optional): The salt used during encryption.
                If provided, regenerates the key with this salt.

        Returns:
            str: Path to the decrypted file.
        """
        if salt:
            # Regenerate the key with the provided salt
            self.salt = salt
            self.key = self._generate_key()
            self.cipher = Fernet(self.key)

        if not output_path:
            if file_path.endswith('.encrypted'):
                output_path = file_path[:-10]  # Remove '.encrypted' suffix
            else:
                output_path = f"{file_path}.decrypted"

        # Read the encrypted file content
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()

        # Decrypt the data
        decrypted_data = self.cipher.decrypt(encrypted_data)

        # Write the decrypted data to the output file
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)

        return output_path


# Example usage
def encrypt_user_file(file_path, password, output_path=None):
    """Encrypt a user file with the provided password.

    Args:
        file_path (str): Path to the file to encrypt.
        password (str): Password for encryption.
        output_path (str, optional): Path to save the encrypted file.

    Returns:
        tuple: (encrypted_file_path, salt)
    """
    encryption = FileEncryption(password)
    return encryption.encrypt_file(file_path, output_path)


def decrypt_user_file(file_path, password, salt, output_path=None):
    """Decrypt a user file with the provided password and salt.

    Args:
        file_path (str): Path to the encrypted file.
        password (str): Password for decryption.
        salt (bytes): Salt used during encryption.
        output_path (str, optional): Path to save the decrypted file.

    Returns:
        str: Path to the decrypted file.
    """
    encryption = FileEncryption(password)
    return encryption.decrypt_file(file_path, output_path, salt)
