# StegVault Wiki

Welcome to the StegVault documentation wiki!

## What is StegVault?

StegVault is a secure password manager that uses steganography to hide encrypted passwords within ordinary images. It combines modern cryptography (XChaCha20-Poly1305 + Argon2id) with dual steganography (PNG LSB + JPEG DCT) to create a portable, zero-knowledge backup system.

## Quick Links

### Getting Started
- [Installation Guide](Installation-Guide.md)
- [Quick Start Tutorial](Quick-Start-Tutorial.md)
- [Basic Usage Examples](Basic-Usage-Examples.md)

### User Guides
- [Creating Backups](Creating-Backups.md)
- [Restoring Passwords](Restoring-Passwords.md)
- [Choosing Cover Images](Choosing-Cover-Images.md)
- [Security Best Practices](Security-Best-Practices.md)

### Technical Documentation
- [Architecture Overview](Architecture-Overview.md)
- [Cryptography Details](Cryptography-Details.md)
- [Steganography Techniques](Steganography-Techniques.md)
- [Payload Format Specification](Payload-Format-Specification.md)

### Development
- [Developer Guide](Developer-Guide.md)
- [API Reference](API-Reference.md)
- [Testing Guide](Testing-Guide.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

### Security
- [Security Model](Security-Model.md)
- [Threat Model](Threat-Model.md)
- [Known Limitations](Known-Limitations.md)
- [Vulnerability Disclosure](Vulnerability-Disclosure.md)

### FAQ & Troubleshooting
- [Frequently Asked Questions](FAQ.md)
- [Troubleshooting Guide](Troubleshooting.md)
- [Common Errors](Common-Errors.md)

## Project Status

- **Version**: 0.6.1 (Application Layer)
- **Status**: Beta - Production-ready features
- **License**: MIT
- **Language**: Python 3.9+
- **Tests**: 614 passing (92% coverage)

## Key Features

- ✅ XChaCha20-Poly1305 AEAD encryption
- ✅ Argon2id key derivation
- ✅ Dual steganography (PNG LSB + JPEG DCT)
- ✅ Full vault mode with CRUD operations
- ✅ TOTP/2FA authenticator
- ✅ Gallery multi-vault management
- ✅ Headless mode (JSON output, automation)
- ✅ Application layer (UI-agnostic controllers)
- ✅ CLI interface
- ✅ 614 unit tests with 92% coverage
- ✅ Zero-knowledge architecture

## Coming Soon

See [ROADMAP.md](../ROADMAP.md) for planned features.

## Need Help?

- 💬 [Discussions](https://github.com/kalashnikxvxiii-collab/stegvault/discussions)
- 🐛 [Issue Tracker](https://github.com/kalashnikxvxiii-collab/stegvault/issues)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.