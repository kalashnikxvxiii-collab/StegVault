# Steganography Techniques

Technical details of StegVault's steganographic methods.

## Overview

StegVault uses **LSB (Least Significant Bit) steganography** with pseudo-random pixel ordering to embed encrypted payloads in images.

## LSB Steganography

### Concept

The least significant bit of each color channel carries minimal visual information. Modifying these bits creates imperceptible changes to the human eye.

### How It Works

#### Image Representation

```
Each pixel in RGB image has 3 color channels:
- Red:   0-255 (8 bits)
- Green: 0-255 (8 bits)
- Blue:  0-255 (8 bits)

Example pixel: (173, 29, 241)
Binary:
  R: 10101101
  G: 00011101
  B: 11110001
     ^      ^  ^
     LSBs (can be modified with minimal visual impact)
```

#### Embedding Process

```
For each bit of payload:
1. Select next pixel from pseudo-random sequence
2. Extract LSB of chosen color channel
3. Replace with payload bit
4. Write modified pixel back to image
```

#### Example

```
Original pixel Red channel: 10101101 (173)
Payload bit to embed: 0

Modified Red channel: 10101100 (172)
Visual change: 173 → 172 (imperceptible)
```

### Capacity Calculation

```
Capacity = (Width × Height × 3 channels × 1 bit per channel) / 8
         = (Width × Height × 3) / 8 bytes

Examples:
- 800×600:    1,440,000 bits = 180,000 bytes
- 1920×1080:  6,220,800 bits = 777,600 bytes
- 3840×2160: 24,883,200 bits = 3,110,400 bytes
```

## Pseudo-Random Pixel Ordering

### Why Random Ordering?

Sequential embedding (top-left to bottom-right) creates detectable patterns. Random ordering distributes payload bits across the entire image.

### Seed-Based PRNG

```python
# Deterministic pseudo-random sequence
seed = derive_seed(salt)  # From encryption salt
rng = PRNG(seed)

# Generate pixel positions
positions = rng.shuffle(all_pixel_positions)

# Embed payload bits at these positions
for bit, position in zip(payload_bits, positions):
    embed_bit_at(image, position, bit)
```

### Properties

- **Deterministic**: Same salt produces same sequence
- **Uniform distribution**: Bits spread evenly across image
- **Reproducible**: Extraction uses same seed to locate bits

### Security Benefits

1. **Pattern resistance**: No sequential patterns in LSBs
2. **Statistical spreading**: Changes distributed uniformly
3. **Analysis resistance**: Harder to detect via chi-square tests

## Image Format Considerations

### PNG (Recommended)

**Characteristics**:
- Lossless compression
- Preserves exact pixel values
- LSBs remain unchanged after save/load

**Reliability**: ✓✓✓ Excellent

**Usage**: Strongly recommended for all production backups

### JPEG (Use with Caution)

**Characteristics**:
- Lossy compression (DCT-based)
- Pixel values approximate after recompression
- LSBs may change during save/load

**Reliability**: ⚠ Risky

**Problems**:
```
Original pixel:    (173, 29, 241)
After JPEG resave: (171, 31, 243)
                    └─ LSB changed!
```

**When JPEG might work**:
- High quality (95+)
- No recompression
- Stored without modification

## Steganographic Algorithms

### Current: LSB Replacement

**Algorithm**: Direct LSB bit replacement

```python
def embed_bit(pixel_value: int, bit: int) -> int:
    """Embed a bit in the LSB of a pixel value."""
    return (pixel_value & 0xFE) | bit  # Clear LSB, set to bit

def extract_bit(pixel_value: int) -> int:
    """Extract the LSB from a pixel value."""
    return pixel_value & 0x01
```

### Future: Advanced Methods

#### LSB Matching

Instead of replacing, increment/decrement to match:

```python
def lsb_match(pixel_value: int, bit: int) -> int:
    if (pixel_value & 0x01) != bit:
        # Randomly +1 or -1 to match bit
        return pixel_value + random.choice([-1, 1])
    return pixel_value
```

**Advantage**: Better statistical properties

#### Adaptive LSB

Embed more bits in complex regions, fewer in smooth regions:

```
High complexity area:  Use 2-3 LSBs per channel
Low complexity area:   Use only 1 LSB
```

**Advantage**: Higher capacity with maintained imperceptibility

## Detectability

### Statistical Attacks

#### Chi-Square Test

Detects abnormal LSB distribution:

```
Normal image: LSBs should be roughly 50/50 (0s and 1s)
Stego image:  May show bias if not properly randomized
```

**StegVault resistance**: Pseudo-random ordering helps distribute bits evenly

#### RS Steganalysis

Analyzes pixel value flips under specific operations.

**StegVault resistance**: Moderate (LSB replacement is detectable by RS analysis)

### Visual Attacks

#### LSB Plane Visualization

Extract and display all LSBs as an image:

```python
# Extract LSB plane
lsb_image = image & 0x01
# Scale to visible range
lsb_visual = lsb_image * 255
```

**StegVault resistance**: Pseudo-random ordering creates noise pattern (no visible payload structure)

### File Analysis

#### File Size Analysis

Comparing original vs. stego:

```
PNG: Identical or near-identical size (LSB changes compress well)
JPEG: May differ if quality settings changed
```

**StegVault resistance**: PNG stego images have nearly identical size to originals

## Implementation Details

### Embedding Algorithm

```python
def embed_payload(image, payload_bytes):
    # 1. Convert payload to bits
    payload_bits = bytes_to_bits(payload_bytes)

    # 2. Generate pseudo-random pixel sequence
    seed = derive_seed_from_salt(payload_salt)
    pixel_positions = generate_random_sequence(seed, image.size)

    # 3. Embed bits
    for bit, (x, y, channel) in zip(payload_bits, pixel_positions):
        pixel = image[x, y]
        pixel[channel] = embed_bit(pixel[channel], bit)
        image[x, y] = pixel

    return image
```

### Extraction Algorithm

```python
def extract_payload(image, payload_size):
    # 1. Read header to get salt and payload size
    header = extract_header(image)  # First 64 bytes

    # 2. Generate same pseudo-random sequence
    seed = derive_seed_from_salt(header.salt)
    pixel_positions = generate_random_sequence(seed, image.size)

    # 3. Extract bits
    payload_bits = []
    for (x, y, channel) in pixel_positions[:payload_size * 8]:
        pixel = image[x, y]
        bit = extract_bit(pixel[channel])
        payload_bits.append(bit)

    # 4. Convert bits back to bytes
    return bits_to_bytes(payload_bits)
```

## Capacity Management

### Overhead Calculation

```
Fixed overhead:
- Magic header: 4 bytes
- Salt: 16 bytes
- Nonce: 24 bytes
- Ciphertext length: 4 bytes
- AEAD tag: 16 bytes
Total: 64 bytes

Variable overhead:
- Ciphertext: len(password) + padding

Total payload size = 64 + len(ciphertext)
```

### Capacity Check

```python
required_bits = payload_size * 8
available_bits = width * height * 3  # 3 channels

if required_bits > available_bits:
    raise CapacityError("Image too small for payload")
```

## Security Considerations

### Steganography ≠ Encryption

**Important**: Steganography provides obscurity, NOT security.

**Security comes from**:
- Encryption (XChaCha20-Poly1305)
- Strong passphrase (Argon2id KDF)

**Steganography provides**:
- Hiding the existence of encrypted data
- Making backups look like ordinary photos

### Known Limitations

1. **Detectable by experts**: Steganalysis tools can detect LSB steganography
2. **Not invisible**: Statistical analysis can reveal payload presence
3. **Format-dependent**: JPEG recompression destroys payload

## Best Practices

For users:
1. Use PNG format always
2. Don't share cover images publicly
3. Avoid editing stego images
4. Store originals and stegos separately

For developers:
1. Use cryptographically secure PRNG for pixel ordering
2. Validate image capacity before embedding
3. Test with steganalysis tools during development
4. Document detectability limitations clearly

## Implemented Techniques (v0.5.1+)

### Dual Steganography

StegVault now supports **two steganography methods** with automatic format detection:

1. **PNG LSB** (Sequential): High capacity (~90KB for 400x600), lossless
2. **JPEG DCT** (Coefficient modification): Lower capacity (~18KB), robust to recompression

### JPEG DCT Steganography ✅

**Implemented in v0.5.1**: Embeds data in DCT coefficients

**Technique**:
- ±1 modification of AC DCT coefficients
- Avoids coefficients with |value| ≤ 1 (prevents shrinkage)
- Processes 8x8 DCT blocks across Y, Cb, Cr channels

**Benefits**:
- ✅ Robust against mild JPEG recompression
- ✅ Survives quality adjustments (within reason)
- ✅ More reliable than LSB for JPEG images

**Trade-offs**:
- Lower capacity (~20% of PNG LSB)
- Requires jpeglib library
- Not 100% invisible to steganalysis

## Future Enhancements

### Advanced Techniques (Planned)

1. **Adaptive LSB**: Higher capacity in complex regions
2. **Spread spectrum**: More robust to modifications
3. **Model-based**: Using ML for better imperceptibility
4. **GIF/BMP Support**: Additional image formats

### Research Areas

- Further post-processing resilience
- Capacity vs. detectability trade-offs
- Encrypted container formats

## References

- [Steganography Overview](https://en.wikipedia.org/wiki/Steganography)
- [LSB Steganography](https://ieeexplore.ieee.org/document/4428630)
- [Steganalysis Techniques](https://dl.acm.org/doi/10.1145/2756539)

## Next Steps

- Read [Payload Format Specification](Payload-Format-Specification.md)
- Understand [Cryptography Details](Cryptography-Details.md)
- Review [Security Model](Security-Model.md)
- Learn about [Known Limitations](Known-Limitations.md)
