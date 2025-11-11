# Developer Guide

Guide for developers contributing to StegVault or integrating it into other projects.

## Getting Started

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/kalashnikxvxiii-collab/StegVault.git
cd StegVault

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e .[dev]

# Verify installation
python -m pytest
```

### Project Structure

```
StegVault/
├── stegvault/              # Main package
│   ├── __init__.py         # Package exports
│   ├── cli.py              # Command-line interface
│   ├── crypto/             # Cryptography module
│   │   ├── __init__.py
│   │   └── core.py         # Encryption/decryption
│   ├── stego/              # Steganography module
│   │   ├── __init__.py
│   │   └── png_lsb.py      # LSB embedding/extraction
│   └── utils/              # Utilities
│       ├── __init__.py
│       └── payload.py      # Payload serialization
├── tests/                  # Test suite
│   ├── test_crypto.py
│   ├── test_stego.py
│   └── test_utils.py
├── docs/                   # Documentation
├── examples/               # Example scripts
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── README.md
```

## Development Workflow

### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make your changes**
   - Write code following style guidelines
   - Add/update tests
   - Update documentation

3. **Run tests**
   ```bash
   pytest
   ```

4. **Run linters**
   ```bash
   black stegvault tests
   mypy stegvault
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature
   ```

### Code Style

**Follow PEP 8** with these specifics:

```python
# Line length
MAX_LINE_LENGTH = 100

# Import order
import os              # Standard library
import sys

import click           # Third-party
from PIL import Image

from stegvault.crypto import encrypt_data  # Local

# Function documentation
def encrypt_data(plaintext: bytes, passphrase: str) -> tuple[bytes, bytes, bytes]:
    """Encrypt data using XChaCha20-Poly1305.

    Args:
        plaintext: Data to encrypt
        passphrase: Encryption passphrase

    Returns:
        Tuple of (salt, nonce, ciphertext)

    Raises:
        CryptoError: If encryption fails
    """
    pass
```

**Run Black formatter**:
```bash
black stegvault tests
```

### Type Hints

Use type hints for all functions:

```python
from typing import Tuple, Optional

def process_image(
    image_path: str,
    output_path: Optional[str] = None
) -> Tuple[int, int]:
    """Process image and return dimensions."""
    pass
```

**Run mypy**:
```bash
mypy stegvault
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_crypto.py

# Run with coverage
pytest --cov=stegvault --cov-report=html

# Run verbose
pytest -v
```

### Writing Tests

```python
# tests/test_example.py
import pytest
from stegvault.crypto import encrypt_data, decrypt_data

def test_encryption_roundtrip():
    """Test encryption and decryption roundtrip."""
    plaintext = b"secret password"
    passphrase = "strongpassphrase123"

    # Encrypt
    salt, nonce, ciphertext = encrypt_data(plaintext, passphrase)

    # Decrypt
    decrypted = decrypt_data(ciphertext, passphrase, salt, nonce)

    # Verify
    assert decrypted == plaintext

def test_wrong_passphrase():
    """Test decryption with wrong passphrase fails."""
    plaintext = b"secret"
    passphrase = "correct"

    salt, nonce, ciphertext = encrypt_data(plaintext, passphrase)

    with pytest.raises(DecryptionError):
        decrypt_data(ciphertext, "wrong", salt, nonce)
```

### Test Coverage

Maintain **>90% test coverage**:

```bash
pytest --cov=stegvault --cov-report=term-missing
```

## API Usage

### Core API

```python
from stegvault import (
    encrypt_data,
    decrypt_data,
    embed_payload,
    extract_payload,
    calculate_capacity
)

# Encryption
plaintext = b"my password"
passphrase = "strong passphrase"
salt, nonce, ciphertext = encrypt_data(plaintext, passphrase)

# Embedding
from PIL import Image
img = Image.open("cover.png")
payload = serialize_payload(salt, nonce, ciphertext)
stego_img = embed_payload(img, payload)
stego_img.save("backup.png")

# Extraction
stego_img = Image.open("backup.png")
extracted_payload = extract_payload(stego_img, payload_size=len(payload))
parsed = parse_payload(extracted_payload)

# Decryption
decrypted = decrypt_data(
    parsed['ciphertext'],
    passphrase,
    parsed['salt'],
    parsed['nonce']
)
```

See [API Reference](API-Reference.md) for complete documentation.

## Adding New Features

### Example: Adding JPEG DCT Support

1. **Create new module**
   ```python
   # stegvault/stego/jpeg_dct.py

   def embed_payload_dct(image, payload):
       """Embed payload using DCT coefficients."""
       # Implementation
       pass
   ```

2. **Add tests**
   ```python
   # tests/test_stego_dct.py

   def test_dct_embedding():
       """Test DCT embedding."""
       # Test implementation
       pass
   ```

3. **Update exports**
   ```python
   # stegvault/stego/__init__.py

   from .jpeg_dct import embed_payload_dct
   __all__ = [..., 'embed_payload_dct']
   ```

4. **Document**
   - Add docstrings
   - Update wiki
   - Add examples

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run StegVault
from stegvault import encrypt_data
```

### Common Issues

**Import errors**:
```bash
# Reinstall in editable mode
pip install -e .
```

**Test failures**:
```bash
# Run with verbose output
pytest -vv --tb=short
```

**Type checking errors**:
```bash
# Check specific file
mypy stegvault/crypto/core.py
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

cProfile.run('your_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Benchmarking

```python
import timeit

def benchmark_encryption():
    setup = "from stegvault import encrypt_data"
    stmt = "encrypt_data(b'test', 'passphrase')"
    time = timeit.timeit(stmt, setup, number=100)
    print(f"Average time: {time/100:.4f}s")
```

## Security Considerations

### Security Review Checklist

Before merging crypto/security changes:

- [ ] Reviewed by security-focused contributor
- [ ] No hardcoded secrets or test keys
- [ ] Constant-time comparisons for sensitive data
- [ ] Proper error handling (no info leaks)
- [ ] Random number generation uses CSPRNG
- [ ] Input validation on all external data
- [ ] Documentation includes security notes

### Secure Coding Practices

```python
# ✓ Good: Use CSPRNG
from nacl.utils import random
salt = random(16)

# ✗ Bad: Use predictable RNG
import random
salt = bytes([random.randint(0, 255) for _ in range(16)])

# ✓ Good: Constant-time comparison
from nacl.bindings import sodium_memcmp
if sodium_memcmp(mac1, mac2):
    pass

# ✗ Bad: Timing attack vulnerable
if mac1 == mac2:
    pass
```

## Releasing

### Version Bumping

```bash
# Update version
# Edit stegvault/__init__.py
__version__ = "0.2.0"

# Edit pyproject.toml
version = "0.2.0"

# Commit
git commit -am "chore: bump version to 0.2.0"
git tag v0.2.0
git push && git push --tags
```

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Tagged release
- [ ] GitHub Release created
- [ ] PyPI package published

## Contributing Guidelines

See [CONTRIBUTING.md](../CONTRIBUTING.md) for full guidelines.

### Pull Request Process

1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Ensure CI passes
5. Submit PR with description
6. Address review feedback
7. Merge when approved

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
```
feat(crypto): add AES-GCM support
fix(stego): correct capacity calculation for small images
docs(wiki): update API reference
test(crypto): add edge case tests for KDF
```

## Resources

- [Architecture Overview](Architecture-Overview.md)
- [API Reference](API-Reference.md)
- [Testing Guide](Testing-Guide.md)
- [Security Best Practices](Security-Best-Practices.md)

## Getting Help

- **Discussions**: GitHub Discussions
- **Issues**: GitHub Issues

## Next Steps

- Review [API Reference](API-Reference.md)
- Read [Testing Guide](Testing-Guide.md)
- Check [Architecture Overview](Architecture-Overview.md)
- See [Contributing Guidelines](../CONTRIBUTING.md)