# Quick Start Tutorial

Get started with StegVault in 5 minutes! This tutorial walks you through creating your first encrypted backup and recovering it.

## Prerequisites

- StegVault installed (see [Installation Guide](Installation-Guide.md))
- A PNG or JPEG image file
- Basic command-line familiarity

## Step 1: Prepare Your Cover Image

Find or download an image to use as a cover. Requirements:
- **Format**: PNG (recommended) or JPEG
- **Size**: At least 100KB for adequate capacity
- **Resolution**: 800x600 pixels or larger recommended

Example: Download a sample image or use your own photo.

```bash
# Check your image size
ls -lh cover.png
```

## Step 2: Create Your First Backup

Use the `backup` command to encrypt and embed a password:

```bash
stegvault backup -i cover.png -o backup.png
```

You'll be prompted for:
1. **Master Password**: The sensitive password you want to protect (e.g., your vault master password)
2. **Encryption Passphrase**: The key used to encrypt the master password (memorize this!)

### Example Session

```
$ stegvault backup -i cover.png -o backup.png
Master password: ****************
Repeat for confirmation: ****************
Encryption passphrase: ********************
Repeat for confirmation: ********************

Creating encrypted backup...
Image capacity: 76800 bytes
Payload size: 92 bytes (0.12% of capacity)
✓ Encrypted password embedded successfully
Backup saved to: backup.png

⚠ IMPORTANT: Store your passphrase securely!
   Without it, the password cannot be recovered.
```

## Step 3: Verify the Backup

Check that the backup image looks identical to the original:

```bash
# View the backup image - it should look unchanged
# (Use any image viewer)

# Check file size (should be nearly identical to original)
ls -lh cover.png backup.png
```

The backup image contains your encrypted password but is visually indistinguishable from the original.

## Step 4: Test Password Recovery

Recover your password from the backup image:

```bash
stegvault restore -i backup.png
```

Enter your encryption passphrase when prompted:

```
$ stegvault restore -i backup.png
Encryption passphrase: ********************

Extracting encrypted password...
✓ Password recovered successfully

Your password: MySecretPassword123

⚠ Make sure no one is looking at your screen!
```

## Step 5: Secure Storage

Now that you've verified the backup works:

1. **Keep the backup image safe**: Store it on USB drives, cloud storage, or multiple locations
2. **Memorize your passphrase**: Without it, recovery is impossible
3. **Delete the original cover.png** if desired (optional)
4. **Test recovery periodically** to ensure backups remain intact

## Common First-Time Questions

### Can I see the password without special tools?

No. The password is encrypted with modern cryptography (XChaCha20-Poly1305) before embedding. Without the passphrase, it's computationally infeasible to recover.

### Will image compression destroy my backup?

- **PNG**: Safe for any storage (lossless format)
- **JPEG**: Risky - resaving/editing may corrupt the embedded data

Always use PNG for production backups.

### Can I use the same image multiple times?

Each backup should use a fresh cover image. Reusing images may create detectable patterns.

### What happens if I forget my passphrase?

The password is permanently unrecoverable. There is no "password reset" by design - this is zero-knowledge security.

## Next Steps

Now that you've mastered the basics:

- Read [Security Best Practices](Security-Best-Practices.md)
- Learn about [Choosing Cover Images](Choosing-Cover-Images.md)
- Explore [Basic Usage Examples](Basic-Usage-Examples.md)
- Understand the [Security Model](Security-Model.md)

## Quick Reference

```bash
# Create backup
stegvault backup -i cover.png -o backup.png

# Restore password
stegvault restore -i backup.png

# Check image capacity
stegvault check -i cover.png

# Get help
stegvault --help
stegvault backup --help
```

## Troubleshooting

If something goes wrong, see:
- [Troubleshooting Guide](Troubleshooting.md)
- [Common Errors](Common-Errors.md)
- [FAQ](FAQ.md)
