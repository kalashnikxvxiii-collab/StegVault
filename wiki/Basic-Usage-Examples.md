# Basic Usage Examples

Practical examples for common StegVault use cases.

## Example 1: Simple Backup and Restore

The most basic workflow:

```bash
# Create backup
$ stegvault backup -i photo.png -o backup.png
Master password: MyVaultPassword2024
Encryption passphrase: StrongPassphrase!@#123

✓ Backup created successfully

# Later: restore the password
$ stegvault restore -i backup.png
Encryption passphrase: StrongPassphrase!@#123

Your password: MyVaultPassword2024
```

## Example 2: Checking Image Capacity

Before creating a backup, verify your image has enough capacity:

```bash
# Check capacity
$ stegvault check -i cover.png
Image: cover.png
Format: PNG
Dimensions: 1920x1080
Capacity: 622080 bytes (622 KB)

Estimated capacity for passwords:
- Short (16 chars): ~5000 backups
- Medium (32 chars): ~2500 backups
- Long (64 chars): ~1200 backups
```

## Example 3: Bypassing Passphrase Strength Check

If you need to use a weak passphrase (not recommended):

```bash
$ stegvault backup -i cover.png -o backup.png --no-check-strength
Master password: test
Encryption passphrase: weak

⚠ Warning: Strength check disabled
✓ Backup created (use strong passphrases in production!)
```

## Example 4: Multiple Backups

Create backups of different passwords using different images:

```bash
# Email account backup
$ stegvault backup -i cover1.png -o email_backup.png
Master password: EmailPassword123

# Bank account backup
$ stegvault backup -i cover2.png -o bank_backup.png
Master password: BankPassword456

# Social media backup
$ stegvault backup -i cover3.png -o social_backup.png
Master password: SocialPassword789
```

## Example 5: Using Different Image Formats

### PNG (Recommended)
```bash
# PNG is lossless - safest option
$ stegvault backup -i vacation.png -o backup.png
✓ Backup created successfully
```

### JPEG (Use with caution)
```bash
# JPEG works but avoid resaving/editing
$ stegvault backup -i photo.jpg -o backup.jpg
⚠ Warning: JPEG format detected
   Avoid resaving or editing this image
   Consider using PNG for better reliability
✓ Backup created
```

## Example 6: Batch Operations

Create multiple backups in one session:

```bash
#!/bin/bash
# backup_all.sh

IMAGES=("img1.png" "img2.png" "img3.png")
PASSWORDS=("Pass1" "Pass2" "Pass3")
OUTPUTS=("backup1.png" "backup2.png" "backup3.png")

for i in ${!IMAGES[@]}; do
  echo "Creating backup $((i+1))..."
  stegvault backup \
    -i "${IMAGES[$i]}" \
    -o "${OUTPUTS[$i]}" \
    --password "${PASSWORDS[$i]}" \
    --passphrase "MyMasterPassphrase"
done

echo "All backups created!"
```

**Security Note**: Never hardcode passwords in scripts for production use. This example is for demonstration only.

## Example 7: Verifying Backup Integrity

Test your backup immediately after creation:

```bash
# Create backup
$ stegvault backup -i cover.png -o backup.png
Master password: TestPassword123
Encryption passphrase: MyPassphrase

# Immediately test restore
$ stegvault restore -i backup.png
Encryption passphrase: MyPassphrase

Your password: TestPassword123

# If it matches, backup is valid
```

## Example 8: Handling Long Passwords

StegVault supports passwords of any length (within image capacity):

```bash
$ stegvault backup -i large_image.png -o backup.png
Master password: ThisIsAVeryLongPasswordWith!@#SpecialChars$%^AndNumbers123456

✓ Password length: 72 characters
✓ Payload size: 156 bytes
✓ Backup created successfully
```

## Example 9: Error Handling

### Insufficient Capacity
```bash
$ stegvault backup -i tiny.png -o backup.png
Master password: MyPassword

Error: Image capacity insufficient
Required: 92 bytes
Available: 48 bytes

Solution: Use a larger image (at least 800x600 recommended)
```

### Wrong Passphrase
```bash
$ stegvault restore -i backup.png
Encryption passphrase: WrongPassphrase

Error: Decryption failed
Possible reasons:
- Incorrect passphrase
- Corrupted image
- Not a StegVault backup
```

## Example 10: Scripted Recovery (Automation)

Recover password programmatically:

```bash
#!/bin/bash
# restore_password.sh

BACKUP_IMAGE="backup.png"
PASSPHRASE="MyPassphrase"

# Restore using environment variable or piped input
echo "$PASSPHRASE" | stegvault restore -i "$BACKUP_IMAGE" --passphrase -

# Parse output
PASSWORD=$(stegvault restore -i "$BACKUP_IMAGE" --passphrase "$PASSPHRASE" 2>/dev/null | grep "Your password:" | cut -d' ' -f3-)

if [ -n "$PASSWORD" ]; then
  echo "Recovery successful"
  # Use $PASSWORD in your automation
else
  echo "Recovery failed"
  exit 1
fi
```

## Common Patterns

### Pattern 1: One Image Per Password
Recommended for maximum security:
```
email_backup.png → Email password
bank_backup.png  → Bank password
work_backup.png  → Work password
```

### Pattern 2: Layered Backups
Store backups in multiple locations:
```bash
# Create backup
stegvault backup -i cover.png -o backup.png

# Copy to multiple locations
cp backup.png ~/usb_drive/backup.png
cp backup.png ~/cloud_sync/backup.png
cp backup.png ~/external_hdd/backup.png
```

### Pattern 3: Periodic Testing
Test backups regularly to ensure they remain intact:
```bash
# Monthly backup test script
#!/bin/bash
for backup in backups/*.png; do
  echo "Testing $backup..."
  stegvault restore -i "$backup" --passphrase "$PASSPHRASE" > /dev/null
  if [ $? -eq 0 ]; then
    echo "✓ $backup OK"
  else
    echo "✗ $backup FAILED - create new backup!"
  fi
done
```

## Advanced Usage

### Using Environment Variables
```bash
# Set passphrase via environment (be careful with shell history)
export STEGVAULT_PASSPHRASE="MyPassphrase"

# Use in scripts
stegvault backup -i cover.png -o backup.png --passphrase "$STEGVAULT_PASSPHRASE"

# Unset when done
unset STEGVAULT_PASSPHRASE
```

### Redirecting Output
```bash
# Silent mode (suppress output)
stegvault backup -i cover.png -o backup.png 2>/dev/null

# Log output
stegvault backup -i cover.png -o backup.png 2>&1 | tee backup.log
```

## Best Practices

1. **Always test recovery** immediately after creating a backup
2. **Use PNG images** whenever possible
3. **Store backups in multiple locations**
4. **Never share backup images publicly**
5. **Use strong, unique passphrases**
6. **Document your backup strategy** (but not passwords/passphrases!)

## Next Steps

- Learn about [Creating Backups](Creating-Backups.md) in detail
- Read about [Restoring Passwords](Restoring-Passwords.md)
- Understand [Security Best Practices](Security-Best-Practices.md)
- Review [Troubleshooting Guide](Troubleshooting.md) for common issues
