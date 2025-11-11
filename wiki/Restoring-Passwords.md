# Restoring Passwords

Complete guide to recovering passwords from StegVault backups.

## Overview

Password restoration extracts the encrypted payload from a stego image and decrypts it using your passphrase.

## Basic Restore Command

```bash
stegvault restore -i <backup_image>
```

### Required Parameters

- `-i, --image`: Path to stego image containing the backup

### Optional Parameters

- `--passphrase`: Encryption passphrase (prompted if not provided)

## Step-by-Step Restoration

### Step 1: Locate Your Backup Image

Find the stego image containing your encrypted password:

```bash
# List available backup images
ls -lh *_backup.png

# Verify it's a valid StegVault backup (optional)
stegvault check -i suspected_backup.png
```

### Step 2: Run the Restore Command

```bash
$ stegvault restore -i password_backup.png
Encryption passphrase: [enter your passphrase]

Extracting encrypted password...
Decrypting...
✓ Password recovered successfully

Your password: MyVaultMasterPassword2024

⚠ Make sure no one is looking at your screen!
   The password is displayed in plain text.
```

### Step 3: Use Your Recovered Password

The password is displayed on screen. You can:
1. Manually type it where needed
2. Copy-paste it (if displayed in copyable format)
3. Redirect output to a file (not recommended for security)

### Step 4: Clear Your Terminal

After recovery, clear your terminal history to remove the plain text password:

```bash
# Clear screen
clear

# Clear bash history entry (optional)
history -d $(history | tail -n 2 | head -n 1 | awk '{print $1}')
```

## Error Handling

### Error 1: Incorrect Passphrase

```bash
$ stegvault restore -i backup.png
Encryption passphrase: WrongPassphrase

Error: Decryption failed
Cause: AEAD authentication tag verification failed

Possible reasons:
1. Incorrect passphrase
2. Image was modified/corrupted
3. Not a valid StegVault backup
```

**Solution**:
- Double-check your passphrase
- Verify the image hasn't been edited or resaved
- Try a backup copy if available

### Error 2: Corrupted Image

```bash
$ stegvault restore -i corrupted_backup.png

Error: Payload extraction failed
Cause: Invalid magic header

Possible reasons:
1. Image was edited or compressed
2. JPEG recompression destroyed data
3. File corruption
```

**Solution**:
- Use a backup copy stored elsewhere
- Avoid using the corrupted image
- Create fresh backups using PNG format

### Error 3: Invalid Image Format

```bash
$ stegvault restore -i backup.gif

Error: Unsupported image format
Supported formats: PNG, JPEG
```

**Solution**: Use PNG or JPEG format images only.

### Error 4: File Not Found

```bash
$ stegvault restore -i missing_backup.png

Error: Image file not found: missing_backup.png
```

**Solution**: Verify the file path is correct.

## Advanced Usage

### Scripted Restoration

Restore password programmatically:

```bash
#!/bin/bash
# restore_script.sh

BACKUP_IMAGE="backup.png"
PASSPHRASE="MyStrongPassphrase!@#"

# Restore using provided passphrase
PASSWORD=$(stegvault restore -i "$BACKUP_IMAGE" --passphrase "$PASSPHRASE" 2>/dev/null | grep "Your password:" | cut -d':' -f2 | xargs)

if [ -n "$PASSWORD" ]; then
  echo "Password recovered successfully"
  # Use $PASSWORD in automation (be careful with security)
else
  echo "Recovery failed"
  exit 1
fi
```

**Security Warning**: Storing passphrases in scripts exposes them. Use this pattern only in secure, isolated environments.

### Quiet Mode

Suppress extra output (for scripting):

```bash
# Only output the password
stegvault restore -i backup.png --quiet 2>/dev/null
```

### Redirecting Output

```bash
# Save to file (INSECURE - avoid in production)
stegvault restore -i backup.png > recovered_password.txt

# Pipe to clipboard (Linux with xclip)
stegvault restore -i backup.png | grep "Your password:" | cut -d':' -f2 | xargs | xclip -selection clipboard

# Pipe to clipboard (macOS)
stegvault restore -i backup.png | grep "Your password:" | cut -d':' -f2 | xargs | pbcopy
```

## Recovery Strategies

### Strategy 1: Manual Recovery (Recommended)

Manually type the password where needed without copying/pasting:

1. Run `stegvault restore`
2. View password on screen
3. Manually type it into the target application
4. Clear terminal immediately

**Pros**: No password in clipboard/files
**Cons**: Slower, prone to typos

### Strategy 2: Clipboard Recovery

Copy password to clipboard temporarily:

```bash
# Display password, copy manually
stegvault restore -i backup.png

# (Or use clipboard piping as shown above)
```

**Pros**: Fast and convenient
**Cons**: Password remains in clipboard history

### Strategy 3: Automated Recovery

Integrate into automated workflows:

```bash
#!/bin/bash
# Auto-login script example

PASSWORD=$(stegvault restore -i backup.png --passphrase "$PASSPHRASE" --quiet)
some_app --username myuser --password "$PASSWORD"
```

**Pros**: Full automation
**Cons**: Higher security risk

## Security Best Practices

### Before Restoration

1. **Verify environment security**
   - Ensure no one is physically watching your screen
   - Check for screen recording software
   - Verify you're on a trusted device

2. **Verify image integrity**
   ```bash
   # Check file hasn't changed
   sha256sum backup.png
   ```

3. **Use a secure terminal**
   - Avoid shared computers
   - Use encrypted connections if remote (SSH)

### During Restoration

1. **Shield your screen** from cameras and observers
2. **Type passphrase carefully** (it's hidden)
3. **Don't screenshot** the recovered password

### After Restoration

1. **Clear terminal output**
   ```bash
   clear
   ```

2. **Clear clipboard** (if used)
   ```bash
   # Linux
   xclip -selection clipboard </dev/null

   # macOS
   pbcopy </dev/null
   ```

3. **Close terminal** if it logged output

4. **Delete any temporary files** created

## Testing Backups

Regularly test your backups to ensure they're recoverable:

```bash
#!/bin/bash
# test_backups.sh

BACKUPS=(backup1.png backup2.png backup3.png)
PASSPHRASE="YourPassphrase"

for backup in "${BACKUPS[@]}"; do
  echo "Testing $backup..."

  if stegvault restore -i "$backup" --passphrase "$PASSPHRASE" &>/dev/null; then
    echo "✓ $backup: OK"
  else
    echo "✗ $backup: FAILED - recreate immediately!"
  fi
done
```

Run this monthly to catch any corrupted backups early.

## Troubleshooting

### Problem: Forgot Passphrase

**Symptom**: Decryption fails with every passphrase attempt.

**Solution**:
- There is **no way to recover** the password without the correct passphrase
- Try common variations you might have used
- Check password manager for stored passphrase
- Look for physical passphrase backup (if you made one)
- As last resort, use alternative account recovery methods

### Problem: Image Modified

**Symptom**: Extraction or decryption fails after editing the image.

**Solution**:
- Use an unmodified backup copy
- Never edit/crop/compress stego images
- Always use PNG format to prevent accidental quality loss

### Problem: JPEG Recompression

**Symptom**: Backup created as JPEG, later fails to restore.

**Solution**:
- Use PNG format for all future backups
- Check if you have original JPEG before recompression
- Create new backup immediately if recovery still works

### Problem: Multiple Failed Attempts

**Symptom**: Tried passphrase many times, all failed.

**Solution**:
1. Double-check you're using the right backup image
2. Verify passphrase (check for typos, caps lock)
3. Try on different device (eliminate system issues)
4. Check backup file integrity (corruption check)

## Recovery Checklist

Before attempting recovery:

- [ ] Located correct backup image
- [ ] Verified image file is intact (not 0 bytes)
- [ ] Ensured private environment (no observers)
- [ ] Prepared to clear terminal afterward
- [ ] Have correct passphrase ready
- [ ] Confirmed destination for recovered password

After successful recovery:

- [ ] Password successfully retrieved
- [ ] Password used/stored where needed
- [ ] Terminal cleared of output
- [ ] Clipboard cleared (if used)
- [ ] Backup image still intact (don't delete it!)

## Next Steps

- Review [Security Best Practices](Security-Best-Practices.md)
- Understand [Common Errors](Common-Errors.md)
- Read about [Known Limitations](Known-Limitations.md)
- Learn [Troubleshooting](Troubleshooting.md) techniques
