# StegVault v0.3.2 - Test Coverage Enhancement

## Overview

Version 0.3.2 is a quality-focused release that significantly expands the test suite and improves overall code coverage from 75% to 87%. This release adds 61 new comprehensive CLI tests, bringing the total test count from 84 to 145 tests.

## Highlights

### Expanded Test Suite
- **61 additional CLI tests** added for comprehensive coverage
- **Total test count: 145 tests** (up from 84 in v0.3.1)
- **CLI module: 113 comprehensive tests** covering all commands:
  - Backup/restore operations
  - Configuration management
  - Batch operations
  - Check command
  - End-to-end workflows
  - Edge cases and error handling

### Improved Coverage
- **Overall coverage: 87%** (up from 75%)
  - CLI module: 81% coverage (up from 78%)
  - Batch operations: 95% coverage (up from 93%)
  - Crypto module: 87% coverage
  - Stego module: 88% coverage
  - Payload module: 100% coverage
  - Config module: 86% coverage

### Quality Improvements
- Applied Black formatter to test files for code consistency
- Enhanced test organization and readability
- All 145 tests pass reliably across Python 3.9-3.14
- Improved CI/CD reliability with comprehensive test coverage

## What's Changed

### Added
- 61 new CLI tests covering:
  - Config command group (show, init, path)
  - Batch command group (batch-backup, batch-restore)
  - Extended backup/restore scenarios
  - Main command tests (version, help)
  - End-to-end workflow validation

### Changed
- Code formatting: Applied Black formatter to test_cli.py
- Test coverage metrics updated across all modules
- Better test organization with clear test class groupings

## Installation

Install or upgrade via pip:

```bash
pip install --upgrade stegvault
```

Or install from source:

```bash
git clone https://github.com/kalashnikxvxiii-collab/stegvault.git
cd stegvault
pip install -e .
```

## Testing

Run the full test suite:

```bash
pytest --cov=stegvault --cov-report=term-missing
```

Expected results:
- 145 tests passing
- 87% overall coverage

## Documentation

- [Full Changelog](https://github.com/kalashnikxvxiii-collab/stegvault/blob/main/CHANGELOG.md)
- [README](https://github.com/kalashnikxvxiii-collab/stegvault/blob/main/README.md)
- [Contributing Guidelines](https://github.com/kalashnikxvxiii-collab/stegvault/blob/main/CONTRIBUTING.md)

## Previous Releases

- [v0.3.1](https://github.com/kalashnikxvxiii-collab/stegvault/releases/tag/v0.3.1) - Security fixes and test coverage improvements
- [v0.3.0](https://github.com/kalashnikxvxiii-collab/stegvault/releases/tag/v0.3.0) - Batch operations and configuration system
- [v0.2.1](https://github.com/kalashnikxvxiii-collab/stegvault/releases/tag/v0.2.1) - Sequential embedding reliability fix
- [v0.2.0](https://github.com/kalashnikxvxiii-collab/stegvault/releases/tag/v0.2.0) - CLI test suite and LSB embedding improvements
- [v0.1.0](https://github.com/kalashnikxvxiii-collab/stegvault/releases/tag/v0.1.0) - Initial release
---

**Full Changelog**: https://github.com/kalashnikxvxiii-collab/stegvault/compare/v0.3.1...v0.3.2