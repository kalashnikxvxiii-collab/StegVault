# Basic Usage Examples

Practical examples for common StegVault use cases (v0.6.1).

## Table of Contents

- [Single Password Mode](#single-password-mode) - Quick backup/restore
- [Vault Mode](#vault-mode) - Full password manager
- [Gallery Mode](#gallery-mode) - Multi-vault management
- [Headless Mode](#headless-mode) - Automation & CI/CD

## Single Password Mode

Quick backup of a single master password.

### Example 1: Simple Backup and Restore

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

### Example 2: Checking Image Capacity

```bash
# Check PNG capacity
$ stegvault check -i cover.png
Image: cover.png
Format: PNG
Dimensions: 1920x1080
Capacity: 622080 bytes (622 KB)

# Check JPEG capacity
$ stegvault check -i photo.jpg
Image: photo.jpg
Format: JPEG
Dimensions: 800x600
Capacity: 18432 bytes (18 KB)
```

## Vault Mode

Full password manager with multiple credentials.

### Example 3: Create Vault with First Entry

```bash
$ stegvault vault create -i cover.png -o myvault.png \
  -k gmail \
  -p MyGmailPass2024 \
  -u user@gmail.com \
  --url https://gmail.com \
  --tags email,personal

Enter vault passphrase: ********
Confirm passphrase: ********

✓ Created vault with 1 entry
✓ Saved to: myvault.png
```

### Example 4: Add More Entries

```bash
# Add GitHub credentials
$ stegvault vault add -i myvault.png \
  -k github \
  -p GitHubToken123 \
  -u githubuser \
  --url https://github.com \
  --tags work,dev

Enter passphrase: ********
✓ Added entry: github
✓ Vault now has 2 entries
```

### Example 5: Retrieve Password

```bash
# Get password
$ stegvault vault get -i myvault.png -k gmail
Enter passphrase: ********

Key: gmail
Password: MyGmailPass2024
Username: user@gmail.com
URL: https://gmail.com
Tags: email, personal

# Copy to clipboard (auto-clear after 30s)
$ stegvault vault get -i myvault.png -k gmail --clipboard
Enter passphrase: ********
✓ Password copied to clipboard (clears in 30s)
```

### Example 6: List All Entries

```bash
$ stegvault vault list -i myvault.png
Enter passphrase: ********

Vault entries (3):
1. gmail (email, personal)
2. github (work, dev)
3. aws (work, cloud)
```

### Example 7: Update Entry

```bash
$ stegvault vault update -i myvault.png -k gmail \
  -p NewPassword123 \
  --notes "Updated password on 2025-01-15"

Enter passphrase: ********
✓ Updated entry: gmail
```

### Example 8: Search and Filter

```bash
# Search by keyword
$ stegvault vault search -i myvault.png -q "email"
Enter passphrase: ********
Found 2 entries: gmail, outlook

# Filter by tag
$ stegvault vault filter -i myvault.png --tag work
Enter passphrase: ********
Entries with tag 'work': github, aws, slack
```

## Gallery Mode

Manage multiple vaults in one gallery.

### Example 9: Create Gallery

```bash
$ stegvault gallery init -d ~/.stegvault/my-gallery.db \
  --name "My Passwords" \
  --description "Personal password vaults"

✓ Gallery created: My Passwords
```

### Example 10: Add Vaults to Gallery

```bash
# Add personal vault
$ stegvault gallery add -d ~/.stegvault/my-gallery.db \
  -i myvault.png \
  --alias "Personal" \
  --tags personal,email

Enter vault passphrase: ********
✓ Added vault: Personal (3 entries cached)

# Add work vault
$ stegvault gallery add -d ~/.stegvault/my-gallery.db \
  -i work-vault.png \
  --alias "Work" \
  --tags work,corporate

Enter vault passphrase: ********
✓ Added vault: Work (5 entries cached)
```

### Example 11: Cross-Vault Search

```bash
# Search across all vaults
$ stegvault gallery search -d ~/.stegvault/my-gallery.db \
  -q "github"

Found 2 entries:
- Personal: github (work, dev)
- Work: github-corp (work, enterprise)

# Filter by tag
$ stegvault gallery search -d ~/.stegvault/my-gallery.db \
  --tag work

Found 7 entries across 2 vaults
```

### Example 12: List Vaults in Gallery

```bash
$ stegvault gallery list -d ~/.stegvault/my-gallery.db

Gallery: My Passwords
Vaults: 2

1. Personal
   Path: ~/vaults/myvault.png
   Entries: 3
   Tags: personal, email
   Last accessed: 2025-01-15 10:30

2. Work
   Path: ~/vaults/work-vault.png
   Entries: 5
   Tags: work, corporate
   Last accessed: 2025-01-14 16:45
```

## TOTP/2FA Mode

Built-in authenticator for 2FA codes.

### Example 13: Add TOTP Secret

```bash
$ stegvault vault add -i myvault.png \
  -k github-2fa \
  -p MyPassword \
  --totp-secret "JBSWY3DPEHPK3PXP"

Enter passphrase: ********
✓ Added entry with TOTP: github-2fa
```

### Example 14: Generate TOTP Code

```bash
$ stegvault vault totp -i myvault.png -k github-2fa
Enter passphrase: ********

TOTP Code: 123456
Valid for: 25 seconds
```

### Example 15: Scan QR Code

```bash
# Scan QR code from screenshot
$ stegvault vault add -i myvault.png \
  -k aws-2fa \
  -p AwsPassword \
  --totp-qr qrcode.png

Enter passphrase: ********
✓ Scanned QR code and added TOTP secret
```

## Headless Mode

Automation-friendly with JSON output.

### Example 16: JSON Output

```bash
# Get password in JSON format
$ stegvault vault get -i myvault.png -k gmail --json \
  --passphrase-file ~/.vault_pass

{
  "status": "success",
  "data": {
    "key": "gmail",
    "password": "MyGmailPass2024",
    "username": "user@gmail.com",
    "url": "https://gmail.com",
    "tags": ["email", "personal"],
    "created": "2025-01-10T14:30:00Z",
    "modified": "2025-01-15T10:15:00Z"
  }
}
```

### Example 17: CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
- name: Retrieve database password
  run: |
    PASSWORD=$(stegvault vault get secrets.png \
      -k db_password \
      --passphrase-file ${{ secrets.VAULT_PASSPHRASE_FILE }} \
      --json | jq -r '.data.password')

    echo "::add-mask::$PASSWORD"
    echo "DB_PASSWORD=$PASSWORD" >> $GITHUB_ENV
```

### Example 18: Environment Variables

```bash
# Set passphrase via environment
export STEGVAULT_PASSPHRASE="MyVaultPass"

# Non-interactive retrieval
$ stegvault vault get -i myvault.png -k gmail --json
{
  "status": "success",
  "data": { ... }
}
```

### Example 19: Automated Backup Script

```bash
#!/bin/bash
# backup-passwords.sh

# Load passphrase from secure file
export STEGVAULT_PASSPHRASE=$(cat ~/.vault_passphrase)

# Check capacity
CAPACITY=$(stegvault check -i vault.png --json | jq -r '.data.capacity')

if [ "$CAPACITY" -lt 5000 ]; then
    echo "Warning: Low capacity"
    exit 1
fi

# Backup vault to multiple locations
cp vault.png ~/backup/vault-$(date +%Y%m%d).png
cp vault.png /mnt/usb/vault-backup.png
cp vault.png ~/Dropbox/vault-encrypted.png

echo "Backup completed: $CAPACITY bytes available"
```

## Password Generation

Cryptographically secure password generation.

### Example 20: Generate Password

```bash
# Generate 32-character password
$ stegvault generate -l 32 --no-ambiguous
Generated password: Kp9@mX4nQ!rT2vB#wL7cZ@hD8sF$yE3j

Strength: Very Strong (entropy: 208 bits)
Contains: uppercase, lowercase, numbers, symbols
```

### Example 21: Custom Character Sets

```bash
# Alphanumeric only (no symbols)
$ stegvault generate -l 24 --no-symbols
Generated password: Kp9mX4nQ2rTvB7cZhD8s

# Letters only
$ stegvault generate -l 20 --no-numbers --no-symbols
Generated password: KpjmXtnQrTvBwLcZ
```

## Import/Export

Vault backup and migration.

### Example 22: Export Vault to JSON

```bash
$ stegvault vault export -i myvault.png -o backup.json
Enter passphrase: ********

✓ Exported 15 entries to: backup.json
Warning: File contains plaintext passwords!
```

### Example 23: Import Vault from JSON

```bash
$ stegvault vault import -i newvault.png \
  --json-file backup.json

Enter passphrase for new vault: ********
✓ Imported 15 entries
✓ Vault saved to: newvault.png
```

### Example 24: Redact Sensitive Data

```bash
# Export with passwords redacted
$ stegvault vault export -i myvault.png -o safe-backup.json --redact
Enter passphrase: ********

✓ Exported 15 entries (passwords redacted)
✓ Safe to store in version control
```

## Batch Operations

Process multiple operations at once.

### Example 25: Batch Add Entries

```bash
# Create batch file
$ cat entries.json
{
  "entries": [
    {"key": "gmail", "password": "pass1", "username": "user@gmail.com"},
    {"key": "github", "password": "pass2", "username": "githubuser"},
    {"key": "aws", "password": "pass3", "url": "https://aws.amazon.com"}
  ]
}

# Import batch
$ stegvault vault batch-add -i myvault.png --batch-file entries.json
Enter passphrase: ********

✓ Added 3 entries in batch mode
```

## Advanced Use Cases

### Example 26: Vault Migration

```bash
# Step 1: Export from old vault
$ stegvault vault export -i old-vault.png -o migration.json
Enter passphrase: ********

# Step 2: Import to new vault with different passphrase
$ stegvault vault import -i new-vault.png --json-file migration.json
Enter passphrase for new vault: ********

# Step 3: Verify
$ stegvault vault list -i new-vault.png
Enter passphrase: ********
Vault entries (15): ✓ All imported
```

### Example 27: Multi-Device Sync

```bash
# On Device 1: Export vault
$ stegvault vault export -i local-vault.png -o sync.json
$ cp sync.json ~/Dropbox/vault-sync/

# On Device 2: Import vault
$ stegvault vault import -i ~/vaults/synced.png \
  --json-file ~/Dropbox/vault-sync/sync.json
```

## See Also

- [Quick Start Tutorial](Quick-Start-Tutorial.md) - Step-by-step guide
- [CLI Reference](../README.md#usage) - Complete command reference
- [Security Best Practices](Security-Best-Practices.md) - Usage guidelines
- [Troubleshooting](Troubleshooting.md) - Common issues
