# API Reference

Complete API documentation for StegVault modules.

## stegvault.crypto

Cryptographic operations module.

### encrypt_data()

```python
def encrypt_data(
    plaintext: bytes,
    passphrase: str
) -> tuple[bytes, bytes, bytes]:
    """Encrypt data using XChaCha20-Poly1305 AEAD.

    Args:
        plaintext: Data to encrypt (typically password as bytes)
        passphrase: Encryption passphrase for key derivation

    Returns:
        Tuple of (salt, nonce, ciphertext) where:
        - salt (bytes): 16-byte Argon2id salt
        - nonce (bytes): 24-byte XChaCha20 nonce
        - ciphertext (bytes): Encrypted data including AEAD tag

    Raises:
        CryptoError: If encryption fails
        ValueError: If inputs are invalid

    Example:
        >>> plaintext = b"my secret password"
        >>> passphrase = "strongpassphrase123"
        >>> salt, nonce, ciphertext = encrypt_data(plaintext, passphrase)
    """
```

### decrypt_data()

```python
def decrypt_data(
    ciphertext: bytes,
    passphrase: str,
    salt: bytes,
    nonce: bytes
) -> bytes:
    """Decrypt data encrypted with encrypt_data().

    Args:
        ciphertext: Encrypted data (including AEAD tag)
        passphrase: Encryption passphrase
        salt: 16-byte Argon2id salt from encryption
        nonce: 24-byte nonce from encryption

    Returns:
        Decrypted plaintext as bytes

    Raises:
        DecryptionError: If decryption/authentication fails
        ValueError: If inputs have invalid sizes

    Example:
        >>> plaintext = decrypt_data(ciphertext, passphrase, salt, nonce)
    """
```

### verify_passphrase_strength()

```python
def verify_passphrase_strength(
    passphrase: str
) -> tuple[bool, str]:
    """Check passphrase strength.

    Args:
        passphrase: Passphrase to check

    Returns:
        Tuple of (is_strong, message) where:
        - is_strong (bool): True if passphrase meets criteria
        - message (str): Description of strength or weakness

    Example:
        >>> is_strong, msg = verify_passphrase_strength("weak")
        >>> print(msg)
        "Passphrase too short (minimum 12 characters)"
    """
```

## stegvault.stego

Steganography operations module.

### embed_payload()

```python
def embed_payload(
    image: PIL.Image.Image,
    payload: bytes
) -> PIL.Image.Image:
    """Embed payload into image using LSB steganography.

    Args:
        image: PIL Image object (RGB or RGBA)
        payload: Binary payload to embed

    Returns:
        New PIL Image with embedded payload

    Raises:
        StegoError: If embedding fails
        CapacityError: If image too small for payload
        ValueError: If image format unsupported

    Example:
        >>> from PIL import Image
        >>> img = Image.open("cover.png")
        >>> payload = b"secret data"
        >>> stego_img = embed_payload(img, payload)
        >>> stego_img.save("backup.png")
    """
```

### extract_payload()

```python
def extract_payload(
    image: PIL.Image.Image,
    payload_size: int
) -> bytes:
    """Extract payload from stego image.

    Args:
        image: PIL Image containing embedded payload
        payload_size: Expected payload size in bytes

    Returns:
        Extracted payload as bytes

    Raises:
        StegoError: If extraction fails
        ValueError: If payload_size invalid

    Example:
        >>> img = Image.open("backup.png")
        >>> payload = extract_payload(img, 92)
    """
```

### calculate_capacity()

```python
def calculate_capacity(
    image: PIL.Image.Image
) -> int:
    """Calculate embedding capacity of image.

    Args:
        image: PIL Image object

    Returns:
        Maximum payload size in bytes

    Example:
        >>> img = Image.open("cover.png")
        >>> capacity = calculate_capacity(img)
        >>> print(f"Can store {capacity} bytes")
    """
```

## stegvault.utils

Utility functions module.

### serialize_payload()

```python
def serialize_payload(
    salt: bytes,
    nonce: bytes,
    ciphertext: bytes,
    tag: bytes
) -> bytes:
    """Serialize payload components into binary format.

    Args:
        salt: 16-byte Argon2id salt
        nonce: 24-byte XChaCha20 nonce
        ciphertext: Encrypted data
        tag: 16-byte AEAD authentication tag

    Returns:
        Complete binary payload (SPW1 format)

    Example:
        >>> payload = serialize_payload(salt, nonce, ciphertext, tag)
        >>> len(payload)  # 64 + len(ciphertext)
    """
```

### parse_payload()

```python
def parse_payload(
    payload: bytes
) -> dict:
    """Parse binary payload into components.

    Args:
        payload: Binary payload in SPW1 format

    Returns:
        Dictionary with keys:
        - 'salt' (bytes): 16-byte salt
        - 'nonce' (bytes): 24-byte nonce
        - 'ciphertext' (bytes): Encrypted data
        - 'tag' (bytes): 16-byte authentication tag

    Raises:
        PayloadFormatError: If payload format invalid

    Example:
        >>> components = parse_payload(payload)
        >>> salt = components['salt']
    """
```

### validate_payload_capacity()

```python
def validate_payload_capacity(
    image_capacity: int,
    payload_size: int
) -> None:
    """Validate image has sufficient capacity.

    Args:
        image_capacity: Available capacity in bytes
        payload_size: Required payload size in bytes

    Raises:
        CapacityError: If capacity insufficient

    Example:
        >>> validate_payload_capacity(1000, 500)  # OK
        >>> validate_payload_capacity(100, 500)   # Raises CapacityError
    """
```

## Exception Classes

### CryptoError

```python
class CryptoError(Exception):
    """Base exception for cryptographic errors."""
```

### DecryptionError

```python
class DecryptionError(CryptoError):
    """Raised when decryption or authentication fails."""
```

### StegoError

```python
class StegoError(Exception):
    """Base exception for steganography errors."""
```

### CapacityError

```python
class CapacityError(StegoError):
    """Raised when image capacity is insufficient."""
```

### PayloadFormatError

```python
class PayloadFormatError(Exception):
    """Raised when payload format is invalid."""
```

## Complete Usage Example

```python
from PIL import Image
from stegvault import (
    encrypt_data,
    decrypt_data,
    embed_payload,
    extract_payload,
    calculate_capacity,
    serialize_payload,
    parse_payload
)

# 1. Load cover image
cover_img = Image.open("cover.png")

# 2. Check capacity
capacity = calculate_capacity(cover_img)
print(f"Image can store {capacity} bytes")

# 3. Encrypt password
password = b"MySecretPassword123"
passphrase = "StrongEncryptionPassphrase!@#"
salt, nonce, ciphertext = encrypt_data(password, passphrase)

# 4. Serialize payload
# Note: encrypt_data already returns ciphertext with tag
# For manual serialization:
from stegvault.crypto import derive_key
from nacl.secret import SecretBox

key = derive_key(passphrase.encode(), salt)
box = SecretBox(key)
encrypted = box.encrypt(password, nonce)
tag = encrypted[-16:]

payload = serialize_payload(salt, nonce, ciphertext, tag)

# 5. Embed in image
stego_img = embed_payload(cover_img, payload)

# 6. Save backup
stego_img.save("backup.png")

# --- Later: Recovery ---

# 7. Load backup image
backup_img = Image.open("backup.png")

# 8. Extract payload
extracted_payload = extract_payload(backup_img, len(payload))

# 9. Parse payload
components = parse_payload(extracted_payload)

# 10. Decrypt password
recovered_password = decrypt_data(
    components['ciphertext'],
    passphrase,
    components['salt'],
    components['nonce']
)

print(f"Recovered: {recovered_password.decode()}")
```

## Constants

### Cryptography Constants

```python
ARGON2_TIME_COST = 3        # Argon2id iterations
ARGON2_MEMORY_COST = 65536  # Argon2id memory (KB)
ARGON2_PARALLELISM = 4      # Argon2id threads
SALT_SIZE = 16              # Salt size (bytes)
NONCE_SIZE = 24             # Nonce size (bytes)
KEY_SIZE = 32               # Key size (bytes)
TAG_SIZE = 16               # AEAD tag size (bytes)
```

### Payload Constants

```python
MAGIC_HEADER = b'SPW1'      # Format magic header
HEADER_SIZE = 4             # Magic header size
FIXED_OVERHEAD = 64         # Fixed payload overhead (bytes)
```

## Type Definitions

```python
from typing import Tuple

# Encryption result
EncryptionResult = Tuple[bytes, bytes, bytes]  # (salt, nonce, ciphertext)

# Payload components
PayloadDict = dict[str, bytes]  # {'salt': ..., 'nonce': ..., ...}

# Passphrase strength check
StrengthCheck = Tuple[bool, str]  # (is_strong, message)
```

## Internal APIs

These are internal functions not meant for public use:

```python
# stegvault.crypto.kdf
def derive_key(passphrase: bytes, salt: bytes) -> bytes:
    """Derive encryption key (internal)."""

# stegvault.stego.png_lsb
def _get_pixel_sequence(seed: bytes, size: tuple) -> list:
    """Generate pseudo-random pixel positions (internal)."""
```

## CLI Interface

For command-line usage, see:

```python
# stegvault.cli
def main():
    """CLI entry point."""

# Commands:
# - backup
# - restore
# - check
```

See [Quick Start Tutorial](Quick-Start-Tutorial.md) for CLI examples.

## Next Steps

- Try [Basic Usage Examples](Basic-Usage-Examples.md)
- Read [Developer Guide](Developer-Guide.md)
- Review [Architecture Overview](Architecture-Overview.md)
- Check [Testing Guide](Testing-Guide.md)
