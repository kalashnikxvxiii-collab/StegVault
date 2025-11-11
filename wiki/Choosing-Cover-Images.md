# Choosing Cover Images

Guide to selecting optimal cover images for StegVault backups.

## Why Cover Image Selection Matters

The cover image you choose affects:
1. **Capacity**: How much data can be embedded
2. **Security**: How detectable the steganography is
3. **Reliability**: Whether the backup survives storage/transmission

## Best Practices

### Format Selection

#### PNG (Strongly Recommended)

**Pros:**
- Lossless compression - data never corrupted
- Works with any storage/transmission
- Can be edited without data loss (if saving as PNG)
- Reliable for long-term storage

**Cons:**
- Larger file sizes
- More obvious as a "preserved" image

**Use PNG for**: All production backups

#### JPEG (Use with Caution)

**Pros:**
- Smaller file sizes
- More common format (less suspicious)

**Cons:**
- Lossy compression - can destroy embedded data
- Recompression during upload/download may corrupt backup
- Editing and resaving destroys payload
- Quality settings affect reliability

**Use JPEG only if**:
- You understand the risks
- You'll never edit/resave the image
- You can prevent automatic compression

### Image Size Requirements

#### Minimum Requirements

For a typical password backup (~100 bytes payload):

- **Absolute minimum**: 300x300 pixels
- **Recommended minimum**: 800x600 pixels
- **Comfortable size**: 1920x1080 pixels or larger

#### Capacity Calculation

```
Capacity (bytes) ≈ (Width × Height × 3) / 8

Examples:
- 800x600 PNG:   1,440,000 bits = 180,000 bytes capacity
- 1920x1080 PNG: 6,220,800 bits = 777,600 bytes capacity
```

Check capacity before creating backup:
```bash
stegvault check -i candidate.png
```

### Image Content Guidelines

#### Good Cover Images

**Natural photos with high complexity:**
- Landscapes (mountains, forests, beaches)
- Cityscapes with varied details
- Portraits with textured backgrounds
- Nature macro photography
- Group photos with diverse elements

**Why**: High visual complexity makes LSB changes imperceptible.

#### Poor Cover Images

**Simple images with low complexity:**
- Solid color backgrounds
- Simple graphics or logos
- Screenshots of text
- Heavily compressed images
- Images with large uniform areas

**Why**: LSB changes may be more detectable in uniform regions.

## Selection Criteria Checklist

Before using an image as cover:

- [ ] **Format**: PNG preferred (or JPEG if necessary)
- [ ] **Resolution**: At least 800x600 pixels
- [ ] **Capacity**: Sufficient for payload (check with `stegvault check`)
- [ ] **Content**: Natural photo with good visual complexity
- [ ] **Source**: Not publicly shared or reverse-searchable
- [ ] **Quality**: Not heavily compressed or artifact-ridden
- [ ] **Metadata**: Consider removing EXIF data

## Finding Cover Images

### Option 1: Your Own Photos (Recommended)

Use personal photos that:
- Haven't been shared online
- Were taken specifically for this purpose
- Have no sentimental value (you'll store the stego version)

**Example sources**:
```bash
# Take photos specifically for backups
camera_app --resolution 1920x1080 --format PNG

# Use existing private photos
ls ~/Pictures/vacation_2023/*.png
```

### Option 2: Stock Photography

Use copyright-free stock photos from:
- Unsplash.com
- Pexels.com
- Pixabay.com

**Download as PNG** when possible.

**Considerations**:
- These images are publicly available (not unique)
- Others could potentially use the same cover image
- Still secure due to encryption, but less ideal

### Option 3: Generated Images

Create images specifically for steganography:

```bash
# Generate random noise image using ImageMagick
convert -size 1920x1080 xc: +noise Random cover.png

# Generate procedural texture
convert -size 1920x1080 plasma: cover.png
```

**Pros**: Maximum capacity, no metadata
**Cons**: Obviously synthetic (stands out)

## Image Preparation

### Step 1: Format Conversion

Convert JPEG to PNG for safety:

```bash
# Using ImageMagick
convert photo.jpg photo.png

# Using Pillow (Python)
from PIL import Image
img = Image.open('photo.jpg')
img.save('photo.png', 'PNG')
```

### Step 2: Metadata Removal (Optional)

Remove EXIF data for privacy:

```bash
# Using exiftool
exiftool -all= cover.png

# Using ImageMagick
convert cover.png -strip cover_clean.png

# Using Python
from PIL import Image
img = Image.open('cover.png')
data = list(img.getdata())
clean_img = Image.new(img.mode, img.size)
clean_img.putdata(data)
clean_img.save('cover_clean.png')
```

### Step 3: Resize if Necessary

Resize images that are too large or too small:

```bash
# Resize to 1920x1080 using ImageMagick
convert large.png -resize 1920x1080 resized.png

# Maintain aspect ratio
convert large.png -resize 1920x1080\> resized.png
```

## Common Mistakes

### Mistake 1: Using Logos or Simple Graphics

```
❌ BAD: company_logo.png (flat colors, simple shapes)
✓ GOOD: office_photo.png (complex scene)
```

### Mistake 2: Tiny Images

```
❌ BAD: icon_64x64.png (insufficient capacity)
✓ GOOD: photo_1920x1080.png (ample capacity)
```

### Mistake 3: Reusing Public Images

```
❌ BAD: famous_stock_photo_12345.jpg (everyone has seen it)
✓ GOOD: my_private_vacation_photo.png (unique to you)
```

### Mistake 4: Heavily Compressed JPEGs

```
❌ BAD: compressed_quality_20.jpg (artifacts, unreliable)
✓ GOOD: high_quality.png or quality_95.jpg
```

## Security Considerations

### Cover Image Uniqueness

**Question**: Should I use a unique cover image for each backup?

**Answer**: Yes, if possible:
- Prevents pattern analysis across multiple backups
- Reduces risk if one cover is compromised
- Each backup is independent

### Public Sharing

**Never**:
- Post your cover images to social media
- Use images you've already posted online
- Share the same image used for different backups

**Why**: If an attacker knows your cover image, statistical analysis becomes easier.

### Cover-Stego Pairs

**Never**:
- Store the original cover image alongside the stego image
- Share both versions
- Keep cover and stego in the same public location

**Why**: Comparing cover vs. stego reveals the steganography.

## Testing Cover Images

Before committing to a cover image:

```bash
# 1. Check capacity
stegvault check -i candidate.png

# 2. Test backup creation
stegvault backup -i candidate.png -o test_backup.png

# 3. Verify visual similarity
# (View both images side-by-side - should look identical)

# 4. Test recovery
stegvault restore -i test_backup.png

# 5. If all tests pass, use it for production backup
```

## Recommended Workflow

```bash
#!/bin/bash
# prepare_cover.sh - Prepare optimal cover image

INPUT_IMAGE="$1"
OUTPUT_COVER="cover_prepared.png"

echo "Preparing cover image..."

# Convert to PNG
convert "$INPUT_IMAGE" -format PNG temp.png

# Strip metadata
exiftool -all= temp.png

# Resize if needed (optional)
convert temp.png -resize 1920x1080\> "$OUTPUT_COVER"

# Verify capacity
stegvault check -i "$OUTPUT_COVER"

# Clean up
rm temp.png

echo "Cover image ready: $OUTPUT_COVER"
```

## Quick Reference

| Criterion | Requirement | Ideal |
|-----------|-------------|-------|
| Format | PNG or JPEG | PNG |
| Resolution | 800x600+ | 1920x1080+ |
| Content | Natural photo | Complex scene |
| File Size | 100KB+ | 500KB+ |
| Public Availability | Private | Never shared |
| Compression | Minimal | None (PNG) |
| Metadata | Optional removal | Stripped |

## Next Steps

- Read [Creating Backups](Creating-Backups.md)
- Review [Security Best Practices](Security-Best-Practices.md)
- Understand [Steganography Techniques](Steganography-Techniques.md)
- Learn about [Known Limitations](Known-Limitations.md)
