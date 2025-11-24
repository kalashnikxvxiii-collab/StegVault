# StegVault - Development Guide

## Setup Development Environment

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install in development mode
```bash
pip install -e ".[dev]"
```

## Development Commands

### Run tests
```bash
pytest
```

### Run tests with coverage
```bash
pytest --cov=stegvault --cov-report=html
```

### Format code
```bash
black stegvault tests
```

### Type checking
```bash
mypy stegvault
```

## Project Structure

```
stegvault/
├── crypto/          # Cryptography: Argon2id + XChaCha20-Poly1305
├── stego/           # Steganography: PNG LSB embedding
├── utils/           # Payload format, config handling
├── vault/           # Password vault management (v0.4.0+)
│   ├── core.py       # Vault and VaultEntry classes
│   ├── operations.py # Vault CRUD operations + import
│   ├── generator.py  # Password generator
│   └── totp.py       # TOTP/2FA support (v0.5.0+)
├── batch/           # Batch operations processor
└── cli.py           # Command-line interface

tests/
├── unit/            # Unit tests (275 tests, 80% coverage)
│   ├── test_crypto.py              # 26 tests
│   ├── test_payload.py             # 22 tests
│   ├── test_stego.py               # 16 tests
│   ├── test_config.py              # 28 tests
│   ├── test_batch.py               # 20 tests
│   ├── test_vault.py               # 49 tests
│   ├── test_cli.py                 # 53 tests
│   ├── test_vault_cli.py           # 38 tests (vault CLI)
│   ├── test_totp.py                # 19 tests (TOTP/2FA)
│   └── test_password_strength.py   # 24 tests (password validation)

examples/            # Example cover images and usage demos
docs/                # Additional documentation
```

## CLI Usage (once implemented)

### Create backup
```bash
stegvault backup \
  --password "my-master-password" \
  --passphrase "encryption-passphrase" \
  --image cover.png \
  --output backup.png
```

### Restore backup
```bash
stegvault restore \
  --image backup.png \
  --passphrase "encryption-passphrase"
```
