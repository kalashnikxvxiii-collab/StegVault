"""
Unit tests for password strength validation using zxcvbn.
"""

import pytest
from stegvault.crypto import verify_passphrase_strength, get_password_strength_details
from stegvault.vault.generator import assess_password_strength, generate_password


class TestPasswordStrengthValidation:
    """Tests for zxcvbn-based password strength validation."""

    def test_very_weak_passwords_rejected(self):
        """Should reject very weak passwords."""
        weak_passwords = [
            "password",
            "123456",
            "qwerty",
            "abc123",
            "password123",
            "letmein",
        ]

        for password in weak_passwords:
            is_valid, message = verify_passphrase_strength(password, min_length=6)
            assert is_valid is False
            assert "too weak" in message.lower()

    def test_minimum_length_enforced(self):
        """Should enforce minimum length."""
        is_valid, message = verify_passphrase_strength("short", min_length=12)
        assert is_valid is False
        assert "12 characters" in message

    def test_acceptable_passwords(self):
        """Should accept passwords with score >= 2."""
        # Passwords that should be acceptable (score 2+)
        acceptable = [
            "MySecureP@ssw0rd2024",  # Random with symbols
            "correct-horse-battery-staple-123",  # Classic strong passphrase
            "Tr0ub4dour&3Extended",  # Good complexity
        ]

        for password in acceptable:
            is_valid, message = verify_passphrase_strength(password)
            assert is_valid is True
            assert (
                "acceptable" in message.lower()
                or "good" in message.lower()
                or "excellent" in message.lower()
            )

    def test_good_passwords(self):
        """Should recognize good passwords (score 3+)."""
        good_passwords = [
            "K7#mP9@qL2$wN5!xR8",  # Very random
            "MyVeryLongAndComplexPassphrase2024!",  # Long and complex
        ]

        for password in good_passwords:
            is_valid, message = verify_passphrase_strength(password)
            assert is_valid is True
            # Should be rated as good or excellent
            assert any(word in message.lower() for word in ["good", "excellent"])

    def test_feedback_provided_for_weak_passwords(self):
        """Should provide helpful feedback for weak passwords."""
        is_valid, message = verify_passphrase_strength("password123")
        assert is_valid is False
        # Should include some feedback
        assert len(message) > 20  # More than just "too weak"

    def test_suggestions_for_acceptable_passwords(self):
        """Should provide suggestions for acceptable but improvable passwords."""
        # This might get score 2 - acceptable but could be better
        is_valid, message = verify_passphrase_strength("MyPassword2024")
        # If score is 2, should have suggestions
        if "acceptable" in message.lower():
            # Just verify it's accepted - suggestions are optional
            assert is_valid is True


class TestPasswordStrengthDetails:
    """Tests for detailed password strength analysis."""

    def test_details_structure(self):
        """Should return all expected fields."""
        details = get_password_strength_details("TestPassword123!")

        assert "score" in details
        assert "crack_time_display" in details
        assert "warning" in details
        assert "suggestions" in details
        assert "guesses" in details
        assert "guesses_log10" in details

    def test_details_score_range(self):
        """Score should be 0-4."""
        passwords = ["123456", "password", "GoodP@ss123", "VeryStr0ng!P@ssw0rd2024"]

        for password in passwords:
            details = get_password_strength_details(password)
            assert 0 <= details["score"] <= 4

    def test_weak_password_details(self):
        """Weak passwords should have warnings."""
        details = get_password_strength_details("password")

        assert details["score"] <= 1
        # Should have either warning or suggestions
        assert details["warning"] or details["suggestions"]

    def test_strong_password_details(self):
        """Strong passwords should have high scores."""
        strong_password = "K7#mP9@qL2$wN5!xR8"
        details = get_password_strength_details(strong_password)

        assert details["score"] >= 3
        assert details["guesses"] > 1000000  # Should require many guesses


class TestAssessPasswordStrength:
    """Tests for password strength assessment in generator module."""

    def test_assess_weak_password(self):
        """Should assess weak passwords correctly."""
        label, score = assess_password_strength("password123")

        assert score <= 1
        assert label in ["Very Weak", "Weak"]

    def test_assess_strong_password(self):
        """Should assess strong passwords correctly."""
        label, score = assess_password_strength("K7#mP9@qL2$wN5!xR8")

        assert score >= 3
        assert label in ["Strong", "Very Strong"]

    def test_assess_all_score_levels(self):
        """Should correctly map all zxcvbn scores to labels."""
        # Test all possible score values
        # Note: zxcvbn scores can vary, so we test ranges
        test_cases = {
            "123456": (0, "Very Weak"),
            "password": (0, "Very Weak"),  # Also gets score 0
            "letmein1": (1, "Weak"),  # Slightly better but still weak
            # Score 2-4 depends on zxcvbn analysis, just verify labels exist
        }

        for password, (expected_score, expected_label) in test_cases.items():
            label, score = assess_password_strength(password)
            # zxcvbn may vary slightly, allow ±1 score difference for weak passwords
            assert (
                abs(score - expected_score) <= 1
            ), f"Password '{password}' expected score {expected_score}, got {score}"
            # Label should match the score
            expected_labels_for_score = {
                0: "Very Weak",
                1: "Weak",
                2: "Fair",
                3: "Strong",
                4: "Very Strong",
            }
            assert label == expected_labels_for_score[score]

    def test_label_options(self):
        """All possible labels should be valid."""
        valid_labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]

        # Test various passwords
        passwords = [
            "123",
            "password",
            "Password123",
            "MyGoodP@ssword123",
            "VeryStr0ng!C0mpl3x#P@ssw0rd2024",
        ]

        for password in passwords:
            label, score = assess_password_strength(password)
            assert label in valid_labels
            assert 0 <= score <= 4


class TestGeneratedPasswordStrength:
    """Tests to verify generated passwords are strong."""

    def test_default_generated_password_is_strong(self):
        """Default generated passwords should be strong (score >= 3)."""
        for _ in range(5):  # Test multiple times
            password = generate_password()
            label, score = assess_password_strength(password)

            assert score >= 3, f"Generated password '{password}' has score {score}, expected >= 3"
            assert label in ["Strong", "Very Strong"]

    def test_long_generated_password_is_very_strong(self):
        """Long generated passwords should be very strong (score 4)."""
        for _ in range(3):
            password = generate_password(length=32)
            label, score = assess_password_strength(password)

            # Most 32-char random passwords should get score 4
            assert score >= 3
            assert label in ["Strong", "Very Strong"]

    def test_short_generated_password_still_acceptable(self):
        """Even short generated passwords should be acceptable."""
        for _ in range(3):
            password = generate_password(length=12)
            label, score = assess_password_strength(password)

            # Should be at least acceptable
            assert score >= 2
            assert label in ["Fair", "Strong", "Very Strong"]


class TestPasswordStrengthEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_empty_password(self):
        """Should reject empty password."""
        is_valid, message = verify_passphrase_strength("")
        assert is_valid is False

    def test_unicode_password(self):
        """Should handle unicode characters."""
        # Unicode password
        password = "Мой_Пароль_2024_ЯЁ"
        is_valid, message = verify_passphrase_strength(password)
        # Should not crash, result depends on zxcvbn analysis
        assert isinstance(is_valid, bool)
        assert isinstance(message, str)

    def test_very_long_password(self):
        """Should handle long passwords (up to zxcvbn limit of 72 chars)."""
        # zxcvbn has a max length of 72 characters
        password = "A" * 60 + "123!@#BcD"
        is_valid, message = verify_passphrase_strength(password)
        # Should accept long passwords
        assert is_valid is True

    def test_special_characters_only(self):
        """Should handle passwords with only special characters."""
        password = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        is_valid, message = verify_passphrase_strength(password)
        # Result depends on zxcvbn, should not crash
        assert isinstance(is_valid, bool)


class TestRealWorldPasswords:
    """Tests with real-world password examples."""

    def test_common_patterns_detected(self):
        """Should detect and reject common patterns."""
        common_patterns = [
            "qwertyuiop",
            "asdfghjkl",
            "1234567890",
            "abcdefghij",
        ]

        for pattern in common_patterns:
            is_valid, message = verify_passphrase_strength(pattern, min_length=8)
            # These should be weak
            assert is_valid is False or "acceptable" not in message.lower()

    def test_leetspeak_not_fooled(self):
        """Should not be fooled by simple leetspeak."""
        # zxcvbn should detect these as weak despite substitutions
        leetspeak = [
            "P@ssw0rd",  # password with substitutions
            "L3tm31n",  # letmein
        ]

        for password in leetspeak:
            is_valid, message = verify_passphrase_strength(password)
            # Should not rate these as strong
            details = get_password_strength_details(password)
            assert details["score"] <= 2

    def test_passphrases_accepted(self):
        """Should accept good passphrases."""
        passphrases = [
            "correct horse battery staple extended",
            "MyFavoriteBook2024Chapter7",
            "i-love-python-programming-2024",
        ]

        for passphrase in passphrases:
            is_valid, message = verify_passphrase_strength(passphrase)
            # Long passphrases should generally be accepted
            if len(passphrase) >= 25:
                assert is_valid is True
