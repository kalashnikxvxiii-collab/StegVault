# Payload Format Specification

Binary format specification for StegVault embedded payloads.

## Format Version

**Current Version**: SPW1 (StegVault Password v1)
**Status**: Stable
**Introduced**: v0.1.0

## Binary Structure

### Complete Layout

```
┌─────────────────────────────────────────────────────────┐
│ Offset │ Size │ Field            │ Type     │ Endian   │
├────────┼──────┼──────────────────┼──────────┼──────────┤
│ 0      │ 4    │ Magic Header     │ bytes    │ N/A      │
│ 4      │ 16   │ Salt             │ bytes    │ N/A      │
│ 20     │ 24   │ Nonce            │ bytes    │ N/A      │
│ 44     │ 4    │ Ciphertext Len   │ uint32   │ Big      │
│ 48     │ N    │ Ciphertext       │ bytes    │ N/A      │
│ 48+N   │ 16   │ AEAD Tag         │ bytes    │ N/A      │
└─────────────────────────────────────────────────────────┘

Total Size: 64 + N bytes
```

## Field Specifications

### Magic Header (4 bytes)

**Purpose**: Format identification and version

**Value**: `0x53 0x50 0x57 0x31` (ASCII "SPW1")

**Validation**:
```python
if magic != b'SPW1':
    raise PayloadFormatError("Invalid magic header")
```

**Why needed**:
- Quickly identify StegVault payloads
- Distinguish from random data or other formats
- Support future format versions (SPW2, SPW3, etc.)

### Salt (16 bytes)

**Purpose**: Key derivation salt for Argon2id

**Generation**: Cryptographically secure random bytes

**Properties**:
- Unique per backup
- Public (embedded in payload)
- Used to derive encryption key from passphrase

**Example**:
```
Hex: B4 7F 2A 19 E3 65 C4 8D F1 23 A7 6B D2 9C 0E 5A
```

### Nonce (24 bytes)

**Purpose**: Initialization vector for XChaCha20-Poly1305

**Generation**: Cryptographically secure random bytes

**Properties**:
- Unique per backup (never reused)
- Public (embedded in payload)
- 192-bit size prevents nonce reuse issues

**Example**:
```
Hex: 3A F7 E2 ... (24 bytes total)
```

### Ciphertext Length (4 bytes)

**Purpose**: Specify ciphertext size

**Encoding**: 32-bit unsigned integer, big-endian

**Range**: 0 to 4,294,967,295 bytes (practical limit: ~10,000)

**Why needed**:
- Allows extraction to read exact amount of data
- Prevents reading beyond payload
- Supports variable-length passwords

**Parsing**:
```python
import struct
ciphertext_len = struct.unpack('>I', length_bytes)[0]
```

### Ciphertext (variable length)

**Purpose**: Encrypted master password

**Content**: XChaCha20-Poly1305 encrypted data

**Length**: Varies based on password length (typically 16-256 bytes)

**Properties**:
- Encrypted using derived key
- Authenticated by AEAD tag
- Contains only the password (no additional metadata)

### AEAD Tag (16 bytes)

**Purpose**: Authentication tag for integrity verification

**Algorithm**: Poly1305 MAC

**Properties**:
- 128-bit security
- Covers entire ciphertext
- Computed during encryption
- Verified during decryption

**Example**:
```
Hex: D8 9A F1 ... (16 bytes total)
```

## Example Payload

### Complete Hex Dump

```
Offset  Hex                                           ASCII
------  --------------------------------------------  ----------------
0000    53 50 57 31 B4 7F 2A 19  E3 65 C4 8D F1 23   SPW1..*..e..#
0010    A7 6B D2 9C 0E 5A 3A F7  E2 C1 6D 8B 44 19   .k...Z:...m.D.
0020    A0 72 E5 3C B8 91 7F 2E  A6 D3 5B 4C 9F 1D   .r.<......[L..
0030    00 00 00 20 7A 8E B2 C4  F1 5D 39 A7 6C D8   ... z....]9.l.
0040    E4 91 3F 2B 5A 7C 1E A0  D6 4F 89 C3 7B 2D   ..?+Z|...O..{-
0050    58 A1 F4 6E 93 D7 2C 80  B5 4A E9 1F 3C 67   X..n..,..J..<g
0060    D8 9A F1 34 7C BE 52 A0  6D C5 8E 3B 71 F2   ...4|.R.m..;q.
0070    9D                                            .
```

### Breakdown

```
Magic:     53 50 57 31                    = "SPW1"
Salt:      B4 7F ... (16 bytes)           = Random salt
Nonce:     3A F7 ... (24 bytes)           = Random nonce
Ctext Len: 00 00 00 20                    = 32 bytes
Ctext:     7A 8E ... (32 bytes)           = Encrypted password
Tag:       D8 9A ... (16 bytes)           = Authentication tag
```

## Serialization

### Encoding (Embedding)

```python
def serialize_payload(salt, nonce, ciphertext, tag):
    """Serialize payload for embedding."""
    payload = bytearray()

    # Magic header
    payload.extend(b'SPW1')

    # Salt (16 bytes)
    payload.extend(salt)

    # Nonce (24 bytes)
    payload.extend(nonce)

    # Ciphertext length (4 bytes, big-endian)
    payload.extend(struct.pack('>I', len(ciphertext)))

    # Ciphertext
    payload.extend(ciphertext)

    # AEAD tag (16 bytes)
    payload.extend(tag)

    return bytes(payload)
```

### Decoding (Extraction)

```python
def parse_payload(payload_bytes):
    """Parse extracted payload."""
    if len(payload_bytes) < 64:
        raise PayloadFormatError("Payload too short")

    # Parse header
    magic = payload_bytes[0:4]
    salt = payload_bytes[4:20]
    nonce = payload_bytes[20:44]
    ctext_len = struct.unpack('>I', payload_bytes[44:48])[0]

    # Validate
    if magic != b'SPW1':
        raise PayloadFormatError("Invalid magic header")

    if len(payload_bytes) < 64 + ctext_len:
        raise PayloadFormatError("Incomplete payload")

    # Parse ciphertext and tag
    ciphertext = payload_bytes[48:48+ctext_len]
    tag = payload_bytes[48+ctext_len:48+ctext_len+16]

    return {
        'salt': salt,
        'nonce': nonce,
        'ciphertext': ciphertext,
        'tag': tag
    }
```

## Validation Rules

### Format Validation

```python
def validate_payload(payload):
    """Validate payload format."""

    # Check minimum size
    if len(payload) < 64:
        raise PayloadFormatError("Payload too short")

    # Check magic header
    if payload[0:4] != b'SPW1':
        raise PayloadFormatError("Invalid magic")

    # Check ciphertext length field
    ctext_len = struct.unpack('>I', payload[44:48])[0]
    expected_size = 64 + ctext_len

    if len(payload) < expected_size:
        raise PayloadFormatError("Truncated payload")

    if len(payload) > expected_size:
        # Warning: extra data (not critical)
        pass

    return True
```

## Size Calculations

### Minimum Payload Size

```
Fixed overhead: 64 bytes
Minimum password: 1 character = 1 byte encrypted
Total minimum: 65 bytes
```

### Typical Payload Sizes

```
8-char password:   64 + 8  = 72 bytes
16-char password:  64 + 16 = 80 bytes
32-char password:  64 + 32 = 96 bytes
64-char password:  64 + 64 = 128 bytes
```

### Maximum Payload Size

Limited by image capacity, not format (format supports up to 4GB).

## Version Migration

### Future Versions

When introducing new algorithms:

```
SPW1: XChaCha20-Poly1305 + Argon2id (current)
SPW2: (future) post-quantum cipher + Argon2id
SPW3: (future) alternative cipher suite
```

### Backward Compatibility

```python
def parse_versioned_payload(payload):
    """Parse payload with version detection."""
    magic = payload[0:4]

    if magic == b'SPW1':
        return parse_spw1_payload(payload)
    elif magic == b'SPW2':
        return parse_spw2_payload(payload)
    else:
        raise PayloadFormatError(f"Unknown version: {magic}")
```

## Error Handling

### Common Errors

```python
class PayloadFormatError(Exception):
    """Invalid payload format."""
    pass

class CapacityError(Exception):
    """Image capacity insufficient."""
    pass

class ExtractionError(Exception):
    """Failed to extract payload."""
    pass
```

### Error Messages

```
"Invalid magic header"        → Not a StegVault payload
"Payload too short"            → Corrupted or incomplete
"Truncated payload"            → Missing data
"Ciphertext length mismatch"  → Corruption detected
```

## Testing Payloads

### Valid Test Payload

```python
# Minimal valid payload
magic = b'SPW1'
salt = b'\x00' * 16
nonce = b'\x00' * 24
ctext_len = struct.pack('>I', 8)
ctext = b'encrypted'
tag = b'\x00' * 16

valid_payload = magic + salt + nonce + ctext_len + ctext + tag
assert len(valid_payload) == 72
```

### Invalid Test Payloads

```python
# Too short
invalid_short = b'SPW1' + b'\x00' * 50  # Only 54 bytes

# Wrong magic
invalid_magic = b'XXXX' + b'\x00' * 60

# Length mismatch
invalid_len = b'SPW1' + b'\x00' * 40 + struct.pack('>I', 999) + b'\x00' * 16
```

## Security Considerations

### Public Fields

All fields except ciphertext are public:
- Salt: Used for key derivation (must be public)
- Nonce: Used for encryption (must be public)
- Lengths: Metadata (low sensitivity)

### Sensitive Fields

Only ciphertext contains sensitive data:
- Protected by encryption (XChaCha20-Poly1305)
- Authenticated by AEAD tag
- Cannot be read without passphrase

### Metadata Leakage

Format reveals:
- StegVault usage (magic header)
- Password length (ciphertext length field)
- Algorithm version (magic header)

Does NOT reveal:
- Actual password
- Passphrase
- Any plaintext

## Next Steps

- Understand [Cryptography Details](Cryptography-Details.md)
- Read [Steganography Techniques](Steganography-Techniques.md)
- Review [Security Model](Security-Model.md)
- See [API Reference](API-Reference.md) for implementation
