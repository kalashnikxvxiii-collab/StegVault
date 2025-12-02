"""
Tests for TUI widgets.

Tests custom Textual widgets for StegVault TUI.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from stegvault.tui.widgets import (
    FileSelectScreen,
    PassphraseInputScreen,
    EntryListItem,
    EntryDetailPanel,
)
from stegvault.vault import Vault, VaultEntry


class TestEntryListItem:
    """Tests for EntryListItem widget."""

    def test_entry_list_item_creation(self):
        """Should create entry list item."""
        entry = VaultEntry(
            key="test",
            password="secret",
            username="user@test.com",
            tags=["work", "email"],
        )

        item = EntryListItem(entry)

        assert item.entry == entry
        assert "entry-item" in item.classes

    def test_entry_list_item_render_with_tags(self):
        """Should render entry with tags."""
        entry = VaultEntry(
            key="github",
            password="pass",
            tags=["dev", "work"],
        )

        item = EntryListItem(entry)
        rendered = item.render()

        assert "github" in rendered
        assert "dev" in rendered
        assert "work" in rendered

    def test_entry_list_item_render_without_tags(self):
        """Should render entry without tags."""
        entry = VaultEntry(key="simple", password="pass")

        item = EntryListItem(entry)
        rendered = item.render()

        assert "simple" in rendered
        assert "[" not in rendered  # No tags


class TestEntryDetailPanel:
    """Tests for EntryDetailPanel widget."""

    def test_entry_detail_panel_creation(self):
        """Should create entry detail panel."""
        panel = EntryDetailPanel()

        assert panel.current_entry is None
        assert panel.password_visible is False

    def test_show_entry_basic(self):
        """Should display entry details."""
        entry = VaultEntry(
            key="test",
            password="secret123",
            username="user@test.com",
        )

        # Create panel and manually set composed state
        panel = EntryDetailPanel()
        panel._composed = True  # Simulate composition

        # Mock query_one to avoid DOM access
        from unittest.mock import Mock

        mock_content = Mock()
        panel.query_one = Mock(return_value=mock_content)
        panel.mount = Mock()

        panel.show_entry(entry)

        assert panel.current_entry == entry
        assert panel.password_visible is False

    def test_show_entry_with_all_fields(self):
        """Should display entry with all fields."""
        entry = VaultEntry(
            key="complete",
            password="pass",
            username="user@example.com",
            url="https://example.com",
            notes="Important notes here",
            tags=["tag1", "tag2"],
            totp_secret="ABCD1234",
        )

        # Create panel and mock DOM access
        panel = EntryDetailPanel()
        panel._composed = True
        from unittest.mock import Mock

        mock_content = Mock()
        panel.query_one = Mock(return_value=mock_content)
        panel.mount = Mock()

        panel.show_entry(entry)

        assert panel.current_entry == entry

    def test_toggle_password_visibility(self):
        """Should toggle password visibility."""
        entry = VaultEntry(key="test", password="secret")

        # Create panel and mock DOM access
        panel = EntryDetailPanel()
        panel._composed = True
        from unittest.mock import Mock

        mock_content = Mock()
        panel.query_one = Mock(return_value=mock_content)
        panel.mount = Mock()

        panel.show_entry(entry)
        assert panel.password_visible is False

        panel.toggle_password_visibility()
        assert panel.password_visible is True

        panel.toggle_password_visibility()
        assert panel.password_visible is False

    def test_toggle_password_without_entry(self):
        """Should handle toggle without entry."""
        panel = EntryDetailPanel()

        # Should not crash
        panel.toggle_password_visibility()
        assert panel.password_visible is False

    def test_clear_panel(self):
        """Should clear entry detail panel."""
        entry = VaultEntry(key="test", password="pass")

        # Create panel and mock DOM access
        panel = EntryDetailPanel()
        panel._composed = True
        from unittest.mock import Mock

        mock_content = Mock()
        panel.query_one = Mock(return_value=mock_content)
        panel.mount = Mock()

        panel.show_entry(entry)
        assert panel.current_entry is not None

        panel.clear()
        assert panel.current_entry is None
        assert panel.password_visible is False


class TestFileSelectScreen:
    """Tests for FileSelectScreen modal."""

    def test_file_select_screen_creation(self):
        """Should create file select screen."""
        screen = FileSelectScreen()

        assert screen.title == "Select Vault Image"
        assert screen.selected_path is None

    def test_file_select_screen_custom_title(self):
        """Should create file select screen with custom title."""
        screen = FileSelectScreen(title="Choose Image")

        assert screen.title == "Choose Image"

    def test_file_select_screen_bindings(self):
        """Should have escape binding."""
        screen = FileSelectScreen()
        binding_keys = [b.key for b in screen.BINDINGS]
        assert "escape" in binding_keys

    def test_action_cancel(self):
        """Should dismiss with None on cancel."""
        screen = FileSelectScreen()
        screen.dismiss = Mock()

        screen.action_cancel()

        screen.dismiss.assert_called_once_with(None)

    def test_on_button_pressed_select_valid_path(self, tmp_path):
        """Should dismiss with path when valid."""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test")

        screen = FileSelectScreen()
        screen.dismiss = Mock()

        # Mock input widget
        mock_input = Mock()
        mock_input.value = str(test_file)
        screen.query_one = Mock(return_value=mock_input)

        # Create button pressed event
        button = Mock()
        button.id = "btn-select"
        event = Mock()
        event.button = button

        screen.on_button_pressed(event)

        screen.dismiss.assert_called_once_with(str(test_file))

    def test_on_button_pressed_select_invalid_path(self):
        """Should notify error for invalid path."""
        screen = FileSelectScreen()
        screen.dismiss = Mock()

        # Mock app
        mock_app = Mock()
        mock_app.notify = Mock()

        # Mock input widget with invalid path
        mock_input = Mock()
        mock_input.value = "/nonexistent/path/file.png"
        screen.query_one = Mock(return_value=mock_input)

        # Create button pressed event
        button = Mock()
        button.id = "btn-select"
        event = Mock()
        event.button = button

        with patch.object(type(screen), "app", property(lambda self: mock_app)):
            screen.on_button_pressed(event)

            mock_app.notify.assert_called_once()
            call_args = mock_app.notify.call_args
            assert "valid file path" in call_args[0][0]

    def test_on_button_pressed_cancel(self):
        """Should dismiss with None on cancel button."""
        screen = FileSelectScreen()
        screen.dismiss = Mock()

        button = Mock()
        button.id = "btn-cancel"
        event = Mock()
        event.button = button

        screen.on_button_pressed(event)

        screen.dismiss.assert_called_once_with(None)

    def test_on_directory_tree_file_selected(self):
        """Should update input when file selected from tree."""
        screen = FileSelectScreen()

        # Mock input widget
        mock_input = Mock()
        mock_input.value = ""
        screen.query_one = Mock(return_value=mock_input)

        # Create file selected event
        event = Mock()
        event.path = Path("/some/path/file.png")

        screen.on_directory_tree_file_selected(event)

        assert mock_input.value == str(event.path)


class TestPassphraseInputScreen:
    """Tests for PassphraseInputScreen modal."""

    def test_passphrase_input_screen_creation(self):
        """Should create passphrase input screen."""
        screen = PassphraseInputScreen()

        assert screen.title == "Enter Passphrase"

    def test_passphrase_input_screen_custom_title(self):
        """Should create passphrase input screen with custom title."""
        screen = PassphraseInputScreen(title="Unlock Vault")

        assert screen.title == "Unlock Vault"

    def test_passphrase_input_screen_bindings(self):
        """Should have escape binding."""
        screen = PassphraseInputScreen()
        binding_keys = [b.key for b in screen.BINDINGS]
        assert "escape" in binding_keys

    def test_action_cancel(self):
        """Should dismiss with None on cancel."""
        screen = PassphraseInputScreen()
        screen.dismiss = Mock()

        screen.action_cancel()

        screen.dismiss.assert_called_once_with(None)

    def test_on_button_pressed_unlock_with_passphrase(self):
        """Should dismiss with passphrase on unlock."""
        screen = PassphraseInputScreen()
        screen.dismiss = Mock()

        # Mock input widget
        mock_input = Mock()
        mock_input.value = "my_secret_passphrase"
        screen.query_one = Mock(return_value=mock_input)

        # Create button pressed event
        button = Mock()
        button.id = "btn-unlock"
        event = Mock()
        event.button = button

        screen.on_button_pressed(event)

        screen.dismiss.assert_called_once_with("my_secret_passphrase")

    def test_on_button_pressed_unlock_empty_passphrase(self):
        """Should notify error for empty passphrase."""
        screen = PassphraseInputScreen()
        screen.dismiss = Mock()

        # Mock app
        mock_app = Mock()
        mock_app.notify = Mock()

        # Mock input widget with empty value
        mock_input = Mock()
        mock_input.value = ""
        screen.query_one = Mock(return_value=mock_input)

        # Create button pressed event
        button = Mock()
        button.id = "btn-unlock"
        event = Mock()
        event.button = button

        with patch.object(type(screen), "app", property(lambda self: mock_app)):
            screen.on_button_pressed(event)

            mock_app.notify.assert_called_once()
            call_args = mock_app.notify.call_args
            assert "cannot be empty" in call_args[0][0]
            screen.dismiss.assert_not_called()

    def test_on_button_pressed_cancel(self):
        """Should dismiss with None on cancel button."""
        screen = PassphraseInputScreen()
        screen.dismiss = Mock()

        button = Mock()
        button.id = "btn-cancel"
        event = Mock()
        event.button = button

        screen.on_button_pressed(event)

        screen.dismiss.assert_called_once_with(None)

    def test_on_input_submitted(self):
        """Should dismiss with value on Enter key."""
        screen = PassphraseInputScreen()
        screen.dismiss = Mock()

        # Create input submitted event
        mock_input = Mock()
        mock_input.id = "passphrase-input"
        event = Mock()
        event.input = mock_input
        event.value = "my_passphrase"

        screen.on_input_submitted(event)

        screen.dismiss.assert_called_once_with("my_passphrase")

    def test_on_input_submitted_empty_value(self):
        """Should not dismiss on Enter with empty value."""
        screen = PassphraseInputScreen()
        screen.dismiss = Mock()

        # Create input submitted event with empty value
        mock_input = Mock()
        mock_input.id = "passphrase-input"
        event = Mock()
        event.input = mock_input
        event.value = ""

        screen.on_input_submitted(event)

        screen.dismiss.assert_not_called()
