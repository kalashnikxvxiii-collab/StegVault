# Cryptography Details

Technical documentation of StegVault's cryptographic implementation.

## Overview

StegVault uses industry-standard cryptographic primitives:
- **Encryption**: XChaCha20-Poly1305 (AEAD cipher)
- **Key Derivation**: Argon2id (password hashing)
- **Random Number Generation**: OS-provided CSPRNG

## Encryption Scheme

### XChaCha20-Poly1305 AEAD

**Algorithm**: XChaCha20-Poly1305
**Type**: Authenticated Encryption with Associated Data (AEAD)
**Library**: libsodium (via PyNaCl)

#### Why XChaCha20-Poly1305?

1. **Modern and secure**: Recommended by cryptography experts
2. **Fast**: Efficient on all platforms
3. **Large nonce**: 192-bit nonce prevents reuse issues
4. **Authenticated**: Poly1305 MAC detects tampering
5. **No patents**: Freely implementable

#### Parameters

```python
ALGORITHM = "XChaCha20-Poly1305"
KEY_SIZE = 32 bytes (256 bits)
NONCE_SIZE = 24 bytes (192 bits)
TAG_SIZE = 16 bytes (128 bits)
```

#### Encryption Process

```
1. Generate random 24-byte nonce
2. Derive 32-byte key from passphrase (see KDF section)
3. Encrypt plaintext:
   ciphertext || tag = XChaCha20-Poly1305.Encrypt(key, nonce, plaintext, ad=[])
4. Return: (nonce, ciphertext, tag)
```

#### Decryption Process

```
1. Extract nonce, ciphertext, and tag from payload
2. Derive key from passphrase
3. Decrypt and verify:
   plaintext = XChaCha20-Poly1305.Decrypt(key, nonce, ciphertext, tag, ad=[])
4. If tag verification fails → raise DecryptionError
```

### Security Properties

#### Confidentiality

- **Semantic security**: Identical plaintexts produce different ciphertexts (due to random nonce)
- **IND-CPA secure**: Indistinguishable under chosen-plaintext attack

#### Integrity

- **Authentication tag**: 128-bit Poly1305 MAC
- **Tamper detection**: Any modification to ciphertext causes decryption failure
- **Forgery resistance**: Cannot forge valid ciphertexts without the key

#### Implementation

```python
# Encryption example (simplified)
from nacl.secret import SecretBox
from nacl.utils import random

# Generate nonce
nonce = random(SecretBox.NONCE_SIZE)  # 24 bytes

# Derive key from passphrase (see KDF section)
key = derive_key(passphrase, salt)

# Create cipher
box = SecretBox(key)

# Encrypt
ciphertext = box.encrypt(plaintext, nonce)
# ciphertext contains: nonce || encrypted_data || tag
```

## Key Derivation Function (KDF)

### Argon2id

**Algorithm**: Argon2id
**Version**: 1.3 (Argon2 v1.3)
**Library**: argon2-cffi

#### Why Argon2id?

1. **Winner of Password Hashing Competition (PHC)**
2. **Resistant to**:
   - GPU cracking attacks
   - Side-channel attacks
   - Time-memory trade-off attacks
3. **Hybrid mode**: Combines Argon2i (data-independent) and Argon2d (data-dependent)
4. **Configurable**: Tunable memory, time, and parallelism costs

#### Parameters

```python
TIME_COST = 3       # Number of iterations
MEMORY_COST = 65536 # Memory usage in KB (64 MB)
PARALLELISM = 4     # Number of parallel threads
SALT_SIZE = 16      # Salt size in bytes
KEY_SIZE = 32       # Output key size in bytes
```

#### Derivation Process

```
1. Generate random 16-byte salt (per backup)
2. Derive key:
   key = Argon2id(
       password=passphrase,
       salt=salt,
       time_cost=3,
       memory_cost=65536,  # 64 MB
       parallelism=4,
       hash_len=32
   )
3. Return: (salt, key)
```

#### Security Properties

- **Slow by design**: Makes brute-force attacks expensive
- **Memory-hard**: Requires significant RAM (64 MB default)
- **Salted**: Unique salt per backup prevents precomputation attacks

#### Implementation

```python
from argon2.low_level import hash_secret_raw, Type

def derive_key(passphrase: bytes, salt: bytes) -> bytes:
    """Derive encryption key from passphrase using Argon2id."""
    return hash_secret_raw(
        secret=passphrase,
        salt=salt,
        time_cost=3,
        memory_cost=65536,  # 64 MB
        parallelism=4,
        hash_len=32,
        type=Type.ID  # Argon2id
    )
```

## Random Number Generation

### Cryptographically Secure RNG

**Source**: Operating system's CSPRNG
- Linux/macOS: `/dev/urandom`
- Windows: `CryptGenRandom`

**Usage**: Generate salts, nonces, and other secrets

#### Implementation

```python
from nacl.utils import random

# Generate random bytes
salt = random(16)   # 16-byte salt
nonce = random(24)  # 24-byte nonce
```

### Entropy Sources

- Hardware random number generators (when available)
- OS entropy pool
- Timing jitter
- Hardware events

## Payload Structure

### Binary Format

```
Offset | Size | Field
-------|------|----------------
0      | 4    | Magic header ("SPW1")
4      | 16   | Salt (for Argon2id)
20     | 24   | Nonce (for XChaCha20)
44     | 4    | Ciphertext length (big-endian)
48     | N    | Ciphertext
48+N   | 16   | AEAD authentication tag
```

### Format Version

**Current version**: SPW1 (StegVault Password v1)

**Magic header**: `0x53 0x50 0x57 0x31` ("SPW1" in ASCII)

**Why versioning?**
- Allows future algorithm upgrades
- Maintains backward compatibility
- Clearly identifies StegVault payloads

## Security Analysis

### Threat Model

#### Protected Against

1. **Passive attacks**: Eavesdropping on stored images
2. **Offline brute-force**: With strong passphrase (16+ chars)
3. **Dictionary attacks**: Argon2id makes each guess expensive
4. **Rainbow tables**: Unique salt per backup
5. **Tampering detection**: AEAD tag ensures integrity

#### Not Protected Against

1. **Weak passphrases**: Short/common passphrases remain vulnerable
2. **Keyloggers**: If passphrase is captured during entry
3. **Memory dumps**: While password is decrypted in RAM
4. **Quantum computers**: XChaCha20 not post-quantum secure
5. **Rubber-hose cryptanalysis**: Physical coercion

### Attack Complexity

#### Brute Force Attack Cost

Assuming attacker has the stego image:

```
Time per guess = Argon2id computation time ≈ 100ms (on modern CPU)

For 16-character random passphrase:
- Entropy: ~95 bits (using alphanumeric + symbols)
- Guesses needed: 2^95 ≈ 4×10^28
- Time required: 2^95 × 100ms ≈ 10^21 years

For 8-character weak password (lowercase only):
- Entropy: ~38 bits
- Guesses needed: 2^38 ≈ 274 billion
- Time required: 274B × 100ms ≈ 868 years (single CPU)
- Time with GPU cluster: Potentially days/weeks
```

**Conclusion**: Strong passphrase (16+ random characters) makes brute-force infeasible.

### Side-Channel Resistance

- **Constant-time operations**: libsodium uses constant-time crypto primitives
- **No timing leaks**: Argon2id designed to resist timing attacks
- **Memory access patterns**: Argon2id resists cache-timing attacks

## Cryptographic Libraries

### PyNaCl (libsodium)

**Version**: ≥1.5.0
**Audit status**: libsodium is well-audited and widely used
**Algorithms provided**:
- XChaCha20-Poly1305 encryption
- Secure random number generation

### argon2-cffi

**Version**: ≥23.1.0
**Binding**: Python CFFI bindings to reference Argon2 C implementation
**Algorithms provided**:
- Argon2id key derivation

## Standards and References

### Algorithm Standards

- **XChaCha20**: [RFC 8439](https://tools.ietf.org/html/rfc8439) + extended nonce
- **Poly1305**: [RFC 8439](https://tools.ietf.org/html/rfc8439)
- **Argon2**: [RFC 9106](https://tools.ietf.org/html/rfc9106)

### Security References

- [NaCl: Networking and Cryptography library](https://nacl.cr.yp.to/)
- [libsodium documentation](https://doc.libsodium.org/)
- [Argon2 specification](https://github.com/P-H-C/phc-winner-argon2)

## Future Considerations

### Post-Quantum Cryptography

**Current status**: XChaCha20 is vulnerable to quantum attacks

**Future plans**:
- Evaluate NIST post-quantum candidates
- Implement hybrid encryption (classical + post-quantum)
- Version bump to "SPW2" when migrating

### Algorithm Agility

Payload format supports future algorithm changes:
- Magic header identifies algorithm version
- New versions can coexist with old backups
- Smooth migration path

## Security Recommendations

For developers and advanced users:

1. **Never implement crypto yourself**: Use vetted libraries
2. **Keep libraries updated**: Security fixes are critical
3. **Use random nonces**: Never reuse nonces
4. **Verify AEAD tags**: Always check authentication before using plaintext
5. **Use strong KDFs**: Argon2id with high cost parameters
6. **Constant-time comparisons**: Prevent timing attacks

## Next Steps

- Understand [Steganography Techniques](Steganography-Techniques.md)
- Review [Payload Format Specification](Payload-Format-Specification.md)
- Read [Security Model](Security-Model.md)
- See [Threat Model](Threat-Model.md)
