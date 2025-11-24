"""
Unit tests for TOTP (Time-based One-Time Password) functionality.
"""

import pytest
import time
from stegvault.vault.totp import (
    generate_totp_secret,
    generate_totp_code,
    verify_totp_code,
    get_totp_provisioning_uri,
    generate_qr_code_ascii,
    get_totp_time_remaining,
)


class TestTOTPSecretGeneration:
    """Tests for TOTP secret generation."""

    def test_generate_secret_returns_base32(self):
        """Should generate a base32-encoded secret."""
        secret = generate_totp_secret()

        assert isinstance(secret, str)
        assert len(secret) == 32  # pyotp default
        # Base32 alphabet: A-Z, 2-7
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567" for c in secret)

    def test_generate_secret_is_unique(self):
        """Should generate different secrets each time."""
        secret1 = generate_totp_secret()
        secret2 = generate_totp_secret()

        assert secret1 != secret2


class TestTOTPCodeGeneration:
    """Tests for TOTP code generation."""

    def test_generate_code_returns_6_digits(self):
        """Should generate a 6-digit code."""
        secret = "JBSWY3DPEHPK3PXP"  # Valid base32 secret
        code = generate_totp_code(secret)

        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_code_with_invalid_secret(self):
        """Should raise ValueError for invalid secret."""
        with pytest.raises(ValueError, match="Invalid TOTP secret"):
            generate_totp_code("invalid!@#$")

    def test_generate_code_is_deterministic(self):
        """Should generate same code for same secret at same time."""
        secret = "JBSWY3DPEHPK3PXP"
        code1 = generate_totp_code(secret)
        code2 = generate_totp_code(secret)

        # Same second should produce same code
        assert code1 == code2


class TestTOTPVerification:
    """Tests for TOTP code verification."""

    def test_verify_valid_code(self):
        """Should verify a valid code."""
        secret = "JBSWY3DPEHPK3PXP"
        code = generate_totp_code(secret)

        assert verify_totp_code(secret, code) is True

    def test_verify_invalid_code(self):
        """Should reject an invalid code."""
        secret = "JBSWY3DPEHPK3PXP"

        assert verify_totp_code(secret, "000000") is False

    def test_verify_wrong_secret(self):
        """Should reject code with wrong secret."""
        secret1 = "JBSWY3DPEHPK3PXP"
        secret2 = "JBSWY3DPEHPK3PXQ"  # Different secret

        code = generate_totp_code(secret1)
        assert verify_totp_code(secret2, code) is False

    def test_verify_with_invalid_secret(self):
        """Should return False for invalid secret."""
        assert verify_totp_code("invalid!@#$", "123456") is False

    def test_verify_code_format(self):
        """Should handle various code formats."""
        secret = "JBSWY3DPEHPK3PXP"
        code = generate_totp_code(secret)

        # Valid code
        assert verify_totp_code(secret, code) is True

        # Invalid format
        assert verify_totp_code(secret, "12345") is False  # Too short
        assert verify_totp_code(secret, "1234567") is False  # Too long


class TestProvisioningURI:
    """Tests for TOTP provisioning URI generation."""

    def test_get_provisioning_uri(self):
        """Should generate valid provisioning URI."""
        secret = "JBSWY3DPEHPK3PXP"
        account = "user@example.com"
        issuer = "StegVault"

        uri = get_totp_provisioning_uri(secret, account, issuer)

        assert uri.startswith("otpauth://totp/")
        # @ is URL-encoded as %40
        assert "user@example.com" in uri or "user%40example.com" in uri
        assert issuer in uri
        assert secret in uri

    def test_provisioning_uri_with_default_issuer(self):
        """Should use default issuer if not specified."""
        secret = "JBSWY3DPEHPK3PXP"
        account = "test@example.com"

        uri = get_totp_provisioning_uri(secret, account)

        assert "StegVault" in uri

    def test_provisioning_uri_special_characters(self):
        """Should handle special characters in account name."""
        secret = "JBSWY3DPEHPK3PXP"
        account = "user+tag@example.com"

        uri = get_totp_provisioning_uri(secret, account)

        assert uri.startswith("otpauth://totp/")
        # URL encoding should handle special characters
        assert "user" in uri


class TestQRCodeGeneration:
    """Tests for QR code ASCII generation."""

    def test_generate_qr_code_ascii(self):
        """Should generate ASCII QR code."""
        secret = "JBSWY3DPEHPK3PXP"
        uri = get_totp_provisioning_uri(secret, "test@example.com")

        qr_code = generate_qr_code_ascii(uri)

        assert isinstance(qr_code, str)
        assert len(qr_code) > 0
        # QR code should contain block characters
        assert any(c in qr_code for c in ["█", " ", "\n"])

    def test_qr_code_contains_data(self):
        """Should generate QR code with embedded data."""
        secret = "JBSWY3DPEHPK3PXP"
        uri = get_totp_provisioning_uri(secret, "test@example.com")

        qr_code = generate_qr_code_ascii(uri)

        # QR code should have multiple lines
        lines = qr_code.split("\n")
        assert len(lines) > 10  # QR codes are typically larger


class TestTimeRemaining:
    """Tests for TOTP time remaining calculation."""

    def test_get_time_remaining(self):
        """Should return seconds remaining until next code."""
        remaining = get_totp_time_remaining()

        assert isinstance(remaining, int)
        assert 0 <= remaining <= 30  # TOTP uses 30-second intervals

    def test_time_remaining_changes(self):
        """Should return different values as time passes."""
        # Get initial value
        remaining1 = get_totp_time_remaining()

        # Wait a bit (but not too long to avoid test flakiness)
        time.sleep(0.1)

        remaining2 = get_totp_time_remaining()

        # Should be same or decreased by 1 (depending on timing)
        assert remaining2 <= remaining1
        assert remaining2 >= 0


class TestTOTPRoundtrip:
    """Integration tests for complete TOTP workflow."""

    def test_full_totp_workflow(self):
        """Should complete full TOTP setup and verification workflow."""
        # Generate secret
        secret = generate_totp_secret()

        # Generate code
        code = generate_totp_code(secret)

        # Verify code
        assert verify_totp_code(secret, code) is True

        # Get provisioning URI
        uri = get_totp_provisioning_uri(secret, "test@example.com")
        assert uri.startswith("otpauth://totp/")

        # Generate QR code
        qr_code = generate_qr_code_ascii(uri)
        assert len(qr_code) > 0

    def test_multiple_accounts_workflow(self):
        """Should handle multiple accounts with different secrets."""
        # Create two accounts
        secret1 = generate_totp_secret()
        secret2 = generate_totp_secret()

        assert secret1 != secret2

        # Generate codes
        code1 = generate_totp_code(secret1)
        code2 = generate_totp_code(secret2)

        # Verify codes with correct secrets
        assert verify_totp_code(secret1, code1) is True
        assert verify_totp_code(secret2, code2) is True

        # Verify codes don't work with wrong secrets
        assert verify_totp_code(secret1, code2) is False
        assert verify_totp_code(secret2, code1) is False
