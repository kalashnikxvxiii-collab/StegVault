# Testing Guide

Comprehensive testing guide for StegVault.

## Overview

StegVault uses **pytest** for testing with **pytest-cov** for coverage reporting.

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_crypto.py

# Run specific test
pytest tests/test_crypto.py::test_encryption_roundtrip

# Run tests matching pattern
pytest -k "encryption"
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=stegvault

# Generate HTML report
pytest --cov=stegvault --cov-report=html

# View report
open htmlcov/index.html  # macOS/Linux
start htmlcov\index.html # Windows

# Terminal report with missing lines
pytest --cov=stegvault --cov-report=term-missing
```

## Test Structure

### Test Organization

```
tests/
├── test_crypto.py          # Cryptography tests
├── test_stego.py           # Steganography tests
├── test_utils.py           # Utility tests
├── test_cli.py             # CLI tests
├── test_integration.py     # End-to-end tests
└── fixtures/               # Test fixtures
    ├── test_images/
    └── test_data/
```

### Test Categories

#### Unit Tests

Test individual functions in isolation:

```python
# tests/test_crypto.py
def test_derive_key():
    """Test key derivation function."""
    from stegvault.crypto import derive_key

    passphrase = b"testpassphrase"
    salt = b"0" * 16

    key = derive_key(passphrase, salt)

    assert len(key) == 32
    assert isinstance(key, bytes)
```

#### Integration Tests

Test multiple components together:

```python
# tests/test_integration.py
def test_full_backup_restore_cycle(tmp_path):
    """Test complete backup and restore workflow."""
    from PIL import Image
    from stegvault import backup_workflow, restore_workflow

    # Create test image
    cover = Image.new('RGB', (100, 100), color='red')
    cover_path = tmp_path / "cover.png"
    cover.save(cover_path)

    # Backup
    backup_path = tmp_path / "backup.png"
    backup_workflow(
        password="testpass",
        passphrase="testphrase123",
        image_path=str(cover_path),
        output_path=str(backup_path)
    )

    # Restore
    recovered = restore_workflow(
        passphrase="testphrase123",
        image_path=str(backup_path)
    )

    assert recovered == "testpass"
```

#### Property-Based Tests

Test properties that should always hold:

```python
import hypothesis.strategies as st
from hypothesis import given

@given(st.binary(min_size=1, max_size=1000))
def test_encryption_always_reversible(plaintext):
    """Encryption should always be reversible."""
    from stegvault.crypto import encrypt_data, decrypt_data

    passphrase = "testpassphrase"
    salt, nonce, ciphertext = encrypt_data(plaintext, passphrase)
    decrypted = decrypt_data(ciphertext, passphrase, salt, nonce)

    assert decrypted == plaintext
```

## Test Fixtures

### Using pytest Fixtures

```python
import pytest
from PIL import Image

@pytest.fixture
def test_image():
    """Create test image."""
    img = Image.new('RGB', (100, 100), color='blue')
    yield img
    img.close()

@pytest.fixture
def temp_image_path(tmp_path):
    """Create temporary image file."""
    img = Image.new('RGB', (100, 100))
    path = tmp_path / "test.png"
    img.save(path)
    return path

def test_embed_payload(test_image):
    """Test using fixture."""
    from stegvault.stego import embed_payload
    payload = b"test"
    result = embed_payload(test_image, payload)
    assert result is not None
```

### Shared Fixtures

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_password():
    return "MyTestPassword123"

@pytest.fixture
def strong_passphrase():
    return "VeryStrong!Passphrase#2024"
```

## Test Examples

### Testing Cryptography

```python
# tests/test_crypto.py
import pytest
from stegvault.crypto import encrypt_data, decrypt_data, DecryptionError

def test_encryption_produces_different_output():
    """Same plaintext should produce different ciphertext."""
    plaintext = b"secret"
    passphrase = "pass"

    s1, n1, c1 = encrypt_data(plaintext, passphrase)
    s2, n2, c2 = encrypt_data(plaintext, passphrase)

    assert s1 != s2  # Different salts
    assert n1 != n2  # Different nonces
    assert c1 != c2  # Different ciphertexts

def test_wrong_passphrase_fails():
    """Decryption with wrong passphrase should fail."""
    plaintext = b"secret"
    s, n, c = encrypt_data(plaintext, "correct")

    with pytest.raises(DecryptionError):
        decrypt_data(c, "wrong", s, n)

def test_tampered_ciphertext_fails():
    """Tampered ciphertext should fail authentication."""
    plaintext = b"secret"
    s, n, c = encrypt_data(plaintext, "pass")

    # Tamper with ciphertext
    tampered = bytearray(c)
    tampered[0] ^= 1  # Flip a bit
    tampered = bytes(tampered)

    with pytest.raises(DecryptionError):
        decrypt_data(tampered, "pass", s, n)
```

### Testing Steganography

```python
# tests/test_stego.py
import pytest
from PIL import Image
from stegvault.stego import embed_payload, extract_payload, CapacityError

def test_embed_extract_roundtrip():
    """Embed and extract should recover original payload."""
    img = Image.new('RGB', (100, 100))
    payload = b"test data"

    stego = embed_payload(img, payload)
    extracted = extract_payload(stego, len(payload))

    assert extracted == payload

def test_capacity_error():
    """Should raise error if payload too large."""
    tiny_img = Image.new('RGB', (10, 10))  # Very small
    large_payload = b"x" * 10000

    with pytest.raises(CapacityError):
        embed_payload(tiny_img, large_payload)

def test_visual_similarity():
    """Stego image should look similar to cover."""
    import numpy as np

    cover = Image.new('RGB', (100, 100), color='red')
    payload = b"secret"
    stego = embed_payload(cover, payload)

    # Convert to arrays
    cover_arr = np.array(cover)
    stego_arr = np.array(stego)

    # Should differ by at most 1 per pixel (LSB change)
    diff = np.abs(cover_arr.astype(int) - stego_arr.astype(int))
    assert np.max(diff) <= 1
```

### Testing CLI

```python
# tests/test_cli.py
from click.testing import CliRunner
from stegvault.cli import main

def test_cli_backup(tmp_path):
    """Test CLI backup command."""
    from PIL import Image

    # Create test image
    cover = Image.new('RGB', (100, 100))
    cover_path = tmp_path / "cover.png"
    cover.save(cover_path)

    backup_path = tmp_path / "backup.png"

    runner = CliRunner()
    result = runner.invoke(main, [
        'backup',
        '-i', str(cover_path),
        '-o', str(backup_path)
    ], input="password\npassword\npassphrase\npassphrase\n")

    assert result.exit_code == 0
    assert backup_path.exists()
```

## Mocking and Patching

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mocks."""
    with patch('stegvault.crypto.random') as mock_random:
        mock_random.return_value = b'0' * 16

        from stegvault.crypto import generate_salt
        salt = generate_salt()

        assert salt == b'0' * 16
        mock_random.assert_called_once()
```

## Continuous Integration

### GitHub Actions

Tests run automatically on push/PR via GitHub Actions:

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: pytest --cov=stegvault --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v4
```

### Local Pre-commit

Run tests before committing:

```bash
#!/bin/bash
# .git/hooks/pre-commit

pytest
if [ $? -ne 0 ]; then
    echo "Tests failed, commit aborted"
    exit 1
fi
```

## Test Coverage Goals

### Target Coverage

- **Overall**: >90%
- **Critical modules** (crypto, stego): >95%
- **Utilities**: >85%
- **CLI**: >80%

### Viewing Coverage

```bash
pytest --cov=stegvault --cov-report=term-missing
```

## Performance Testing

### Benchmarking

```python
# tests/test_performance.py
import time

def test_encryption_performance():
    """Encryption should complete in reasonable time."""
    from stegvault.crypto import encrypt_data

    plaintext = b"test" * 100
    passphrase = "testpass"

    start = time.time()
    encrypt_data(plaintext, passphrase)
    duration = time.time() - start

    assert duration < 1.0  # Should take < 1 second
```

## Best Practices

1. **Write tests first** (TDD approach)
2. **One assertion per test** (when possible)
3. **Use descriptive test names**
4. **Test edge cases** (empty input, max size, etc.)
5. **Mock external dependencies**
6. **Keep tests fast** (< 1s per test)
7. **Use fixtures** for common setup
8. **Test error conditions**
9. **Maintain high coverage**
10. **Run tests frequently**

## Troubleshooting

### Tests Fail Locally

```bash
# Clean and reinstall
pip install -e .[dev]
pytest --cache-clear
```

### Import Errors

```bash
# Ensure installed in editable mode
pip install -e .
```

### Slow Tests

```bash
# Run with duration report
pytest --durations=10
```

## Next Steps

- Read [Developer Guide](Developer-Guide.md)
- Review [API Reference](API-Reference.md)
- Check [Contributing Guidelines](../CONTRIBUTING.md)
