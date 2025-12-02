"""
Tests for TUI screens.

Tests the VaultScreen for StegVault TUI.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from stegvault.tui.screens import VaultScreen
from stegvault.vault import Vault, VaultEntry
from stegvault.app.controllers import VaultController


class TestVaultScreen:
    """Tests for VaultScreen."""

    def test_vault_screen_creation(self):
        """Should create vault screen."""
        vault = Vault(entries=[])
        controller = VaultController()

        screen = VaultScreen(vault, "test.png", controller)

        assert screen.vault == vault
        assert screen.image_path == "test.png"
        assert screen.controller == controller
        assert screen.selected_entry is None

    def test_vault_screen_bindings(self):
        """Should have key bindings defined."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)

        binding_keys = [b.key for b in screen.BINDINGS]

        assert "escape" in binding_keys  # back
        assert "c" in binding_keys  # copy password
        assert "v" in binding_keys  # toggle password
        assert "r" in binding_keys  # refresh
        assert "q" in binding_keys  # quit

    def test_action_back(self):
        """Should call app.pop_screen."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)

        # Create a mock parent with app
        mock_app = Mock()
        mock_app.pop_screen = Mock()
        screen._parent = Mock()
        screen._parent.app = mock_app

        # Patch the app property to return mock_app
        with patch.object(type(screen), "app", property(lambda self: mock_app)):
            screen.action_back()
            mock_app.pop_screen.assert_called_once()

    def test_action_quit(self):
        """Should call app.exit."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)

        # Create a mock parent with app
        mock_app = Mock()
        mock_app.exit = Mock()
        screen._parent = Mock()
        screen._parent.app = mock_app

        # Patch the app property to return mock_app
        with patch.object(type(screen), "app", property(lambda self: mock_app)):
            screen.action_quit()
            mock_app.exit.assert_called_once()

    def test_action_refresh(self):
        """Should notify refresh feature."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.notify = Mock()

        screen.action_refresh()

        screen.notify.assert_called_once()
        call_args = screen.notify.call_args
        assert "Coming soon" in call_args[0][0]

    def test_action_copy_password_no_entry(self):
        """Should warn when no entry selected."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.notify = Mock()

        screen.action_copy_password()

        screen.notify.assert_called_once()
        call_args = screen.notify.call_args
        assert "No entry selected" in call_args[0][0]
        assert call_args[1]["severity"] == "warning"

    def test_action_copy_password_success(self):
        """Should copy password to clipboard."""
        entry = VaultEntry(key="test", password="secret123")
        vault = Vault(entries=[entry])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.selected_entry = entry
        screen.notify = Mock()

        # Mock pyperclip at import level
        with patch("pyperclip.copy") as mock_copy:
            screen.action_copy_password()

            mock_copy.assert_called_once_with("secret123")
            screen.notify.assert_called_once()
            call_args = screen.notify.call_args
            assert "Password copied" in call_args[0][0]
            assert "test" in call_args[0][0]

    def test_action_copy_password_failure(self):
        """Should handle clipboard copy failure."""
        entry = VaultEntry(key="test", password="secret")
        vault = Vault(entries=[entry])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.selected_entry = entry
        screen.notify = Mock()

        # Mock pyperclip to raise exception
        with patch("pyperclip.copy", side_effect=Exception("Clipboard error")):
            screen.action_copy_password()

            screen.notify.assert_called_once()
            call_args = screen.notify.call_args
            assert "Failed to copy password" in call_args[0][0]
            assert call_args[1]["severity"] == "error"

    def test_action_toggle_password_no_entry(self):
        """Should warn when no entry selected."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.notify = Mock()

        screen.action_toggle_password()

        screen.notify.assert_called_once()
        call_args = screen.notify.call_args
        assert "No entry selected" in call_args[0][0]
        assert call_args[1]["severity"] == "warning"

    def test_action_toggle_password_success(self):
        """Should toggle password visibility."""
        entry = VaultEntry(key="test", password="secret")
        vault = Vault(entries=[entry])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.selected_entry = entry

        # Mock detail panel
        mock_panel = Mock()
        mock_panel.toggle_password_visibility = Mock()
        screen.query_one = Mock(return_value=mock_panel)

        screen.action_toggle_password()

        mock_panel.toggle_password_visibility.assert_called_once()

    def test_on_button_pressed_copy(self):
        """Should handle copy button press."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.action_copy_password = Mock()

        button = Mock()
        button.id = "btn-copy"
        event = Mock()
        event.button = button

        screen.on_button_pressed(event)

        screen.action_copy_password.assert_called_once()

    def test_on_button_pressed_toggle(self):
        """Should handle toggle button press."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.action_toggle_password = Mock()

        button = Mock()
        button.id = "btn-toggle"
        event = Mock()
        event.button = button

        screen.on_button_pressed(event)

        screen.action_toggle_password.assert_called_once()

    def test_on_button_pressed_refresh(self):
        """Should handle refresh button press."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.action_refresh = Mock()

        button = Mock()
        button.id = "btn-refresh"
        event = Mock()
        event.button = button

        screen.on_button_pressed(event)

        screen.action_refresh.assert_called_once()

    def test_on_button_pressed_back(self):
        """Should handle back button press."""
        vault = Vault(entries=[])
        controller = VaultController()
        screen = VaultScreen(vault, "test.png", controller)
        screen.action_back = Mock()

        button = Mock()
        button.id = "btn-back"
        event = Mock()
        event.button = button

        screen.on_button_pressed(event)

        screen.action_back.assert_called_once()
