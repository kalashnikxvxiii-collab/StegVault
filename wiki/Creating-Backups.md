# Creating Backups

Comprehensive guide to creating password backups with StegVault.

## Overview

Creating a backup involves three main steps:
1. Encrypting your master password with a strong passphrase
2. Embedding the encrypted payload in a cover image
3. Saving the resulting stego image

## Basic Backup Command

```bash
stegvault backup -i <cover_image> -o <output_image>
```

### Required Parameters

- `-i, --image`: Path to cover image (PNG or JPEG)
- `-o, --output`: Path for output stego image

### Optional Parameters

- `--password`: Master password (prompted if not provided)
- `--passphrase`: Encryption passphrase (prompted if not provided)
- `--check-strength / --no-check-strength`: Enable/disable passphrase strength checking (default: enabled)

## Step-by-Step Process

### Step 1: Select a Cover Image

Choose an appropriate cover image:

```bash
# Check image capacity first
stegvault check -i candidate_image.png
```

**Good candidates:**
- PNG format (lossless)
- At least 800x600 resolution
- Natural photos (landscapes, portraits)
- File size > 100KB

**Avoid:**
- Images with solid colors
- Very small images
- Previously compressed JPEGs
- Images you've shared publicly

### Step 2: Choose a Strong Master Password

This is the password you're protecting (e.g., your password manager's master password).

**Tips:**
- Use your actual password vault's master password
- Can be any length (practical limit: ~1000 characters)
- Include special characters, numbers, uppercase/lowercase

### Step 3: Choose a Strong Encryption Passphrase

This passphrase encrypts your master password before embedding.

**Requirements:**
- Minimum 12 characters (16+ recommended)
- Mix of uppercase, lowercase, numbers, symbols
- Not a dictionary word
- Unique to this backup

**Example strong passphrases:**
```
- Correct-Horse-Battery-Staple-92!
- MyD0g@teMyH0m3w0rk#2024
- 7r0ub4dor&3$unnyDays*
```

### Step 4: Run the Backup Command

```bash
$ stegvault backup -i vacation_photo.png -o password_backup.png
Master password:
Repeat for confirmation:
Encryption passphrase:
Repeat for confirmation:

Creating encrypted backup...
Checking passphrase strength...
✓ Passphrase is strong

Image capacity: 76800 bytes
Payload size: 92 bytes (0.12% of capacity)
Encrypting password...
Embedding in image...
✓ Encrypted password embedded successfully

Backup saved to: password_backup.png

⚠ IMPORTANT REMINDERS:
   1. Store your passphrase securely (memorize or use password manager)
   2. Keep multiple copies of the backup image
   3. Test recovery immediately: stegvault restore -i password_backup.png
   4. Never upload the backup image to public websites
```

### Step 5: Verify the Backup

Immediately test recovery:

```bash
$ stegvault restore -i password_backup.png
Encryption passphrase: [enter your passphrase]

✓ Password recovered successfully
Your password: [should match your master password]
```

## Advanced Options

### Scripted Backups

For automation (use cautiously):

```bash
#!/bin/bash
# automated_backup.sh

PASSWORD="MyMasterPassword123"
PASSPHRASE="StrongEncryptionPassphrase!@#"
COVER_IMAGE="cover.png"
OUTPUT_IMAGE="backup_$(date +%Y%m%d).png"

echo "$PASSWORD" | stegvault backup \
  -i "$COVER_IMAGE" \
  -o "$OUTPUT_IMAGE" \
  --password - \
  --passphrase "$PASSPHRASE"

# Test recovery
echo "$PASSPHRASE" | stegvault restore -i "$OUTPUT_IMAGE" --passphrase -
```

**Security Warning**: Never store passwords/passphrases in plain text files or scripts in production environments.

### Disabling Strength Checks

For testing or advanced use:

```bash
stegvault backup \
  -i cover.png \
  -o backup.png \
  --no-check-strength
```

## Backup Strategies

### Strategy 1: Single Master Password Backup

Store one critical password (e.g., password manager master password):

```
master_backup.png → Password manager master password
```

### Strategy 2: Multiple Password Backups

Create separate backups for different accounts:

```
email_backup.png  → Email password
bank_backup.png   → Banking password
crypto_backup.png → Cryptocurrency wallet password
```

### Strategy 3: Layered Backup Copies

Create one backup, store multiple copies:

```bash
# Create backup
stegvault backup -i cover.png -o master_backup.png

# Distribute copies
cp master_backup.png ~/Dropbox/master_backup.png
cp master_backup.png /mnt/usb_drive/master_backup.png
cp master_backup.png ~/Documents/Photos/vacation2024.png  # Camouflaged name
```

## Common Pitfalls and Solutions

### Pitfall 1: Weak Passphrases

**Problem:**
```
stegvault backup -i cover.png -o backup.png
Encryption passphrase: 123456
Warning: Passphrase is too weak (only digits)
```

**Solution**: Use a passphrase with 16+ characters, mixing character types.

### Pitfall 2: Insufficient Capacity

**Problem:**
```
Error: Image capacity insufficient
Required: 250 bytes
Available: 200 bytes
```

**Solution**: Use a larger cover image (higher resolution).

### Pitfall 3: JPEG Quality Loss

**Problem**: Using JPEG and later editing/resaving destroys the backup.

**Solution**: Always use PNG format for production backups.

### Pitfall 4: Forgetting the Passphrase

**Problem**: No way to recover password without the passphrase.

**Solution**:
- Store passphrase in a trusted password manager
- Use a memorable but strong passphrase
- Consider physical backup of passphrase in secure location

## Security Considerations

### What Gets Encrypted

1. Your master password (plaintext → ciphertext)
2. Encrypted using XChaCha20-Poly1305 AEAD
3. Key derived from passphrase using Argon2id

### What Is Not Encrypted

- The cover image itself
- Image metadata (EXIF data)
- The fact that steganography was used (if analyzed)

### Threat Model

**Protected against:**
- Casual observers viewing the image
- Automated scanning for known file signatures
- Brute force attacks (if strong passphrase used)

**Not protected against:**
- Targeted forensic analysis revealing steganography presence
- Quantum computer attacks (post-quantum crypto not yet implemented)
- Rubber-hose cryptanalysis (physical coercion)

## Backup Checklist

Before creating a production backup:

- [ ] Selected PNG format cover image
- [ ] Image is at least 800x600 pixels
- [ ] Verified image capacity is sufficient
- [ ] Chosen strong master password
- [ ] Chosen strong encryption passphrase (16+ characters)
- [ ] Tested passphrase memorability
- [ ] Prepared to store backup in multiple locations
- [ ] Prepared to test recovery immediately

After creating backup:

- [ ] Tested recovery successfully
- [ ] Stored backup in at least 2 physical locations
- [ ] Stored passphrase securely (memory or password manager)
- [ ] Documented backup strategy (without passwords!)
- [ ] Deleted any temporary files

## Next Steps

- Learn about [Restoring Passwords](Restoring-Passwords.md)
- Read [Choosing Cover Images](Choosing-Cover-Images.md)
- Review [Security Best Practices](Security-Best-Practices.md)
- Understand [Known Limitations](Known-Limitations.md)
