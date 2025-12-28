"""
Tests for TUI main application.

Tests StegVaultTUI app initialization and basic functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from stegvault.tui.app import StegVaultTUI
from stegvault.vault import Vault, VaultEntry
from stegvault.app.controllers import VaultController


class TestStegVaultTUI:
    """Tests for StegVaultTUI application."""

    def test_tui_app_creation(self):
        """Should create TUI application."""
        app = StegVaultTUI()

        assert app.vault_controller is not None
        assert app.crypto_controller is not None
        assert app.current_vault is None
        assert app.current_image_path is None

    def test_tui_app_title(self):
        """Should have correct title."""
        app = StegVaultTUI()

        assert app.TITLE == "⚡⚡ STEGVAULT ⚡⚡ Neural Security Terminal"
        assert "Privacy is a luxury" in app.SUB_TITLE

    def test_tui_app_bindings(self):
        """Should have key bindings defined."""
        app = StegVaultTUI()

        binding_keys = [b.key for b in app.BINDINGS]

        assert "q" in binding_keys  # quit
        assert "o" in binding_keys  # open vault
        assert "n" in binding_keys  # new vault
        assert "h" in binding_keys  # help

    @pytest.mark.asyncio
    async def test_action_quit(self):
        """Should show quit confirmation and schedule exit if confirmed."""
        app = StegVaultTUI()
        app.exit = Mock()
        app.call_later = Mock()

        # Mock push_screen_wait to return True (user confirmed quit)
        app.push_screen_wait = AsyncMock(return_value=True)

        await app._async_quit()

        # Verify that exit was scheduled via call_later
        app.call_later.assert_called_once_with(app.exit)

    @pytest.mark.asyncio
    async def test_action_quit_cancelled(self):
        """Should not schedule exit if quit cancelled."""
        app = StegVaultTUI()
        app.call_later = Mock()

        # Mock push_screen_wait to return False (user cancelled quit)
        app.push_screen_wait = AsyncMock(return_value=False)

        await app._async_quit()

        # Verify that exit was NOT scheduled
        app.call_later.assert_not_called()

    @pytest.mark.asyncio
    async def test_action_new_vault_cancel_file(self):
        """Should handle cancelled file selection for new vault."""
        app = StegVaultTUI()
        app.push_screen_wait = AsyncMock(return_value=None)

        await app._async_new_vault()

        # Should return early without error
        app.push_screen_wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_action_new_vault_cancel_passphrase(self):
        """Should handle cancelled passphrase input for new vault."""
        app = StegVaultTUI()
        # Add extra None to handle loop returning to file selection (Python 3.14 compatibility)
        app.push_screen_wait = AsyncMock(side_effect=["output.png", None, None])

        await app._async_new_vault()

        # Should call push_screen_wait at least twice (file, then passphrase)
        assert app.push_screen_wait.call_count >= 2

    @pytest.mark.asyncio
    async def test_action_new_vault_cancel_first_entry(self):
        """Should handle cancelled first entry form."""
        app = StegVaultTUI()
        # Add extra None to handle loop returning to file selection (Python 3.14 compatibility)
        app.push_screen_wait = AsyncMock(side_effect=["output.png", "passphrase", None, None])

        await app._async_new_vault()

        # Should call push_screen_wait at least three times (file, passphrase, entry form)
        assert app.push_screen_wait.call_count >= 3

    @pytest.mark.asyncio
    async def test_action_new_vault_create_failure(self):
        """Should handle vault creation failure."""
        app = StegVaultTUI()
        form_data = {"key": "test", "password": "secret"}
        # Add extra None to handle loop returning to file selection after error (Python 3.14 compatibility)
        app.push_screen_wait = AsyncMock(side_effect=["output.png", "passphrase", form_data, None])
        app.notify = Mock()

        # Mock controller to return failure
        app.vault_controller.create_new_vault = Mock(return_value=(None, False, "Test error"))

        await app._async_new_vault()

        # Should notify error
        app.notify.assert_called()
        error_calls = [call for call in app.notify.call_args_list if "Failed" in str(call)]
        assert len(error_calls) > 0

    @pytest.mark.asyncio
    async def test_action_new_vault_save_failure(self):
        """Should handle vault save failure."""
        app = StegVaultTUI()
        form_data = {"key": "test", "password": "secret"}
        # Add extra None to handle loop returning to file selection after error (Python 3.14 compatibility)
        app.push_screen_wait = AsyncMock(side_effect=["output.png", "passphrase", form_data, None])
        app.notify = Mock()

        # Mock create success, save failure
        mock_vault = Vault(entries=[])
        app.vault_controller.create_new_vault = Mock(return_value=(mock_vault, True, None))

        from stegvault.app.controllers import VaultSaveResult

        save_result = VaultSaveResult(output_path="", success=False, error="Disk full")
        app.vault_controller.save_vault = Mock(return_value=save_result)

        await app._async_new_vault()

        # Should notify error
        app.notify.assert_called()
        error_calls = [call for call in app.notify.call_args_list if "Failed to save" in str(call)]
        assert len(error_calls) > 0

    @pytest.mark.asyncio
    async def test_action_new_vault_success(self):
        """Should successfully create and open new vault."""
        app = StegVaultTUI()
        form_data = {
            "key": "gmail",
            "password": "secret123",
            "username": "user@gmail.com",
            "url": "https://gmail.com",
            "notes": "Personal",
            "tags": ["email"],
        }
        app.push_screen_wait = AsyncMock(side_effect=["output.png", "passphrase", form_data])
        app.push_screen = Mock()
        app.notify = Mock()

        # Mock successful vault creation and save
        mock_entry = VaultEntry(key="gmail", password="secret123")
        mock_vault = Vault(entries=[mock_entry])
        app.vault_controller.create_new_vault = Mock(return_value=(mock_vault, True, None))

        from stegvault.app.controllers import VaultSaveResult

        save_result = VaultSaveResult(output_path="output.png", success=True)
        app.vault_controller.save_vault = Mock(return_value=save_result)

        await app._async_new_vault()

        # Should create vault with correct parameters
        app.vault_controller.create_new_vault.assert_called_once_with(
            key="gmail",
            password="secret123",
            username="user@gmail.com",
            url="https://gmail.com",
            notes="Personal",
            tags=["email"],
        )

        # Should save vault
        app.vault_controller.save_vault.assert_called_once_with(
            mock_vault, "output.png", "passphrase"
        )

        # Should push vault screen
        app.push_screen.assert_called_once()
        assert app.current_vault == mock_vault
        assert app.current_image_path == "output.png"

        # Should notify success
        success_calls = [
            call for call in app.notify.call_args_list if "created successfully" in str(call)
        ]
        assert len(success_calls) > 0

    @pytest.mark.asyncio
    async def test_action_new_vault_exception(self):
        """Should handle exceptions during vault creation."""
        app = StegVaultTUI()
        form_data = {"key": "test", "password": "secret"}
        # Add extra None to handle loop returning to file selection after error (Python 3.14 compatibility)
        app.push_screen_wait = AsyncMock(side_effect=["output.png", "passphrase", form_data, None])
        app.notify = Mock()

        # Mock controller to raise exception
        app.vault_controller.create_new_vault = Mock(side_effect=Exception("Test error"))

        await app._async_new_vault()

        # Should notify error
        app.notify.assert_called()
        error_calls = [call for call in app.notify.call_args_list if "Error creating" in str(call)]
        assert len(error_calls) > 0

    def test_action_show_help(self):
        """Should push help screen."""
        app = StegVaultTUI()
        app.push_screen = Mock()

        app.action_show_help()

        app.push_screen.assert_called_once()
        # Verify HelpScreen was passed
        from stegvault.tui.widgets import HelpScreen

        call_args = app.push_screen.call_args
        assert isinstance(call_args[0][0], HelpScreen)

    @pytest.mark.asyncio
    async def test_action_open_vault_cancel_file(self):
        """Should handle cancelled file selection."""
        app = StegVaultTUI()
        app.push_screen_wait = AsyncMock(return_value=None)

        await app._async_open_vault()

        # Should return early without error
        app.push_screen_wait.assert_called_once()

    @pytest.mark.asyncio
    async def test_action_open_vault_cancel_passphrase(self):
        """Should handle cancelled passphrase input."""
        app = StegVaultTUI()
        # Add extra None to handle loop returning to file selection (Python 3.14 compatibility)
        app.push_screen_wait = AsyncMock(side_effect=["test.png", None, None])

        await app._async_open_vault()

        # Should call push_screen_wait at least twice (file, then passphrase)
        assert app.push_screen_wait.call_count >= 2

    @pytest.mark.asyncio
    async def test_action_open_vault_load_failure(self):
        """Should handle vault loading failure."""
        app = StegVaultTUI()
        # Add extra None to handle loop returning to file selection after error (Python 3.14 compatibility)
        app.push_screen_wait = AsyncMock(side_effect=["test.png", "passphrase", None])
        app.notify = Mock()

        # Mock controller to return failure
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Invalid passphrase"
        app.vault_controller.load_vault = Mock(return_value=mock_result)

        await app._async_open_vault()

        # Should notify error
        app.notify.assert_called()
        error_calls = [call for call in app.notify.call_args_list if "Failed" in str(call)]
        assert len(error_calls) > 0

    @pytest.mark.asyncio
    async def test_action_open_vault_success(self):
        """Should successfully load vault."""
        app = StegVaultTUI()
        app.push_screen_wait = AsyncMock(side_effect=["test.png", "passphrase"])
        app.push_screen = Mock()
        app.notify = Mock()

        # Mock successful vault load
        mock_vault = Vault(entries=[])
        mock_result = Mock()
        mock_result.success = True
        mock_result.vault = mock_vault
        app.vault_controller.load_vault = Mock(return_value=mock_result)

        await app._async_open_vault()

        # Should push vault screen
        app.push_screen.assert_called_once()
        assert app.current_vault == mock_vault
        assert app.current_image_path == "test.png"

    @pytest.mark.asyncio
    async def test_action_open_vault_exception(self):
        """Should handle exceptions during vault loading."""
        app = StegVaultTUI()
        # Add extra None to handle loop returning to file selection after error (Python 3.14 compatibility)
        app.push_screen_wait = AsyncMock(side_effect=["test.png", "passphrase", None])
        app.notify = Mock()

        # Mock controller to raise exception
        app.vault_controller.load_vault = Mock(side_effect=Exception("Test error"))

        await app._async_open_vault()

        # Should notify error
        app.notify.assert_called()
        error_calls = [call for call in app.notify.call_args_list if "Error" in str(call)]
        assert len(error_calls) > 0

    def test_on_button_pressed_open(self):
        """Should handle open button press."""
        app = StegVaultTUI()
        app.action_open_vault = Mock()

        button = Mock()
        button.id = "btn-open"
        event = Mock()
        event.button = button

        app.on_button_pressed(event)

        # Should call action_open_vault
        app.action_open_vault.assert_called_once()

    def test_on_button_pressed_new(self):
        """Should handle new button press."""
        app = StegVaultTUI()
        app.action_new_vault = Mock()

        button = Mock()
        button.id = "btn-new"
        event = Mock()
        event.button = button

        app.on_button_pressed(event)

        app.action_new_vault.assert_called_once()

    def test_on_button_pressed_help(self):
        """Should handle help button press."""
        app = StegVaultTUI()
        app.action_show_help = Mock()

        button = Mock()
        button.id = "btn-help"
        event = Mock()
        event.button = button

        app.on_button_pressed(event)

        app.action_show_help.assert_called_once()

    def test_on_click_settings(self):
        """Should handle settings static widget click."""
        app = StegVaultTUI()
        app.action_show_settings = Mock()

        widget = Mock()
        widget.id = "btn-settings"
        event = Mock()
        event.widget = widget

        app.on_click(event)

        app.action_show_settings.assert_called_once()

    @patch("stegvault.utils.updater.update_cache_version")
    def test_on_mount_updates_cache_version(self, mock_update_cache):
        """Should call update_cache_version on mount to fix version mismatch."""
        app = StegVaultTUI()
        app.run_worker = Mock()
        app.query_one = Mock()  # Mock button query

        app.on_mount()

        # Should call update_cache_version
        mock_update_cache.assert_called_once()

    @patch("stegvault.utils.updater.update_cache_version")
    def test_on_mount_cache_update_exception(self, mock_update_cache):
        """Should handle exception in update_cache_version gracefully."""
        mock_update_cache.side_effect = Exception("Cache error")

        app = StegVaultTUI()
        app.run_worker = Mock()
        app.query_one = Mock()  # Mock button query

        # Should not crash
        app.on_mount()

    @pytest.mark.skip(reason="Requires full Textual app initialization with screen stack")
    def test_notify_toast_limiting(self):
        """Should limit toasts to maximum of 3."""
        app = StegVaultTUI()

        # Mock the screen and ToastRack
        mock_toast_rack = Mock()
        mock_toasts = [Mock() for _ in range(5)]  # 5 toasts
        mock_toast_rack.query.return_value = mock_toasts

        mock_screen = Mock()
        mock_screen.query_one.return_value = mock_toast_rack

        # Mock the parent notify and screen property
        with patch.object(type(app).__bases__[0], "notify"):
            with patch.object(app, "screen", mock_screen):
                app.notify("Test message")

        # Should have removed 2 oldest toasts (5 - 3 = 2)
        assert mock_toasts[0].remove.called
        assert mock_toasts[1].remove.called
        assert not mock_toasts[2].remove.called

    @pytest.mark.skip(reason="Requires full Textual app initialization with screen stack")
    def test_notify_toast_limiting_exception(self):
        """Should handle toast limiting exception gracefully."""
        app = StegVaultTUI()

        # Mock screen to raise exception when querying ToastRack
        mock_screen = Mock()
        mock_screen.query_one.side_effect = Exception("ToastRack not found")

        # Mock the parent notify
        with patch.object(type(app).__bases__[0], "notify"):
            with patch.object(app, "screen", mock_screen):
                # Should not crash
                app.notify("Test message")

    @pytest.mark.asyncio
    async def test_check_totp_auth_disabled(self):
        """Should skip TOTP auth when disabled in config."""
        app = StegVaultTUI()

        mock_config = Mock()
        mock_config.totp.enabled = False

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            await app._check_totp_auth()

        # Should return early without showing auth screen
        # (no assertion needed - just ensuring it doesn't crash)

    @pytest.mark.asyncio
    async def test_check_totp_auth_no_secret(self):
        """Should skip TOTP auth when secret not configured."""
        app = StegVaultTUI()

        mock_config = Mock()
        mock_config.totp.enabled = True
        mock_config.totp.secret = None

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            await app._check_totp_auth()

    @pytest.mark.asyncio
    async def test_check_totp_auth_config_load_failure(self):
        """Should handle config load failure gracefully."""
        app = StegVaultTUI()

        with patch("stegvault.config.core.load_config", side_effect=Exception("Config error")):
            # Should not crash
            await app._check_totp_auth()

    @pytest.mark.asyncio
    async def test_check_totp_auth_success(self):
        """Should continue when TOTP authentication succeeds."""
        app = StegVaultTUI()
        app.exit = Mock()

        mock_config = Mock()
        mock_config.totp.enabled = True
        mock_config.totp.secret = "SECRET123"
        mock_config.totp.backup_code = "BACKUP"

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            with patch.object(app, "push_screen_wait", new_callable=AsyncMock) as mock_push:
                mock_push.return_value = True  # Authentication successful

                await app._check_totp_auth()

        # Should not exit
        app.exit.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_totp_auth_failure(self):
        """Should exit app when TOTP authentication fails."""
        app = StegVaultTUI()
        app.exit = Mock()

        mock_config = Mock()
        mock_config.totp.enabled = True
        mock_config.totp.secret = "SECRET123"
        mock_config.totp.backup_code = "BACKUP"

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            with patch.object(app, "push_screen_wait", new_callable=AsyncMock) as mock_push:
                mock_push.return_value = False  # Authentication failed

                await app._check_totp_auth()

        # Should exit app
        app.exit.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_totp_auth_exception(self):
        """Should handle TOTP auth exception gracefully."""
        app = StegVaultTUI()

        mock_config = Mock()
        mock_config.totp.enabled = True
        mock_config.totp.secret = "SECRET123"

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            with patch.object(app, "push_screen_wait", side_effect=Exception("Auth error")):
                # Should not crash
                await app._check_totp_auth()

    @pytest.mark.asyncio
    async def test_check_for_updates_async_disabled(self):
        """Should skip update check when auto_check disabled."""
        app = StegVaultTUI()

        mock_config = Mock()
        mock_config.updates.auto_check = False

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            await app._check_for_updates_async()

        # Should return early (no assertion needed)

    @pytest.mark.asyncio
    async def test_check_for_updates_async_config_failure(self):
        """Should handle config load failure gracefully."""
        app = StegVaultTUI()

        with patch("stegvault.config.core.load_config", side_effect=Exception("Config error")):
            # Should not crash
            await app._check_for_updates_async()

    @pytest.mark.asyncio
    async def test_check_for_updates_async_cached_no_update(self):
        """Should use cached result when available and show no banner."""
        app = StegVaultTUI()
        app.query_one = Mock()

        mock_config = Mock()
        mock_config.updates.auto_check = True
        mock_config.updates.check_interval_hours = 24

        cached_result = {"update_available": False, "latest_version": "0.7.9"}

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            with patch("stegvault.utils.updater.get_cached_check", return_value=cached_result):
                await app._check_for_updates_async()

        # Banner should not be queried/shown
        app.query_one.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_for_updates_async_cached_with_update(self):
        """Should show banner when cached result indicates update available."""
        app = StegVaultTUI()

        mock_banner = Mock()
        app.query_one = Mock(return_value=mock_banner)

        mock_config = Mock()
        mock_config.updates.auto_check = True
        mock_config.updates.check_interval_hours = 24

        cached_result = {"update_available": True, "latest_version": "0.8.0"}

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            with patch("stegvault.utils.updater.get_cached_check", return_value=cached_result):
                await app._check_for_updates_async()

        # Banner should be updated and displayed
        mock_banner.update.assert_called_once()
        assert "v0.8.0" in mock_banner.update.call_args[0][0]
        assert mock_banner.display is True

    @pytest.mark.asyncio
    async def test_check_for_updates_async_fresh_check_with_update(self):
        """Should perform fresh check and show banner when cache miss."""
        app = StegVaultTUI()

        mock_banner = Mock()
        app.query_one = Mock(return_value=mock_banner)

        mock_config = Mock()
        mock_config.updates.auto_check = True
        mock_config.updates.check_interval_hours = 24

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            with patch("stegvault.utils.updater.get_cached_check", return_value=None):
                with patch(
                    "stegvault.utils.updater.check_for_updates", return_value=(True, "0.8.0", None)
                ):
                    with patch("stegvault.utils.updater.cache_check_result") as mock_cache:
                        await app._check_for_updates_async()

        # Should cache the result
        mock_cache.assert_called_once_with(True, "0.8.0", None)

        # Banner should be shown
        mock_banner.update.assert_called_once()
        assert mock_banner.display is True

    @pytest.mark.asyncio
    async def test_check_for_updates_async_exception(self):
        """Should handle exception during update check gracefully."""
        app = StegVaultTUI()

        mock_config = Mock()
        mock_config.updates.auto_check = True

        with patch("stegvault.config.core.load_config", return_value=mock_config):
            with patch(
                "stegvault.utils.updater.get_cached_check", side_effect=Exception("Check error")
            ):
                # Should not crash
                await app._check_for_updates_async()

    @pytest.mark.asyncio
    async def test_async_quit_with_screen_stack(self):
        """Should pop all screens before exiting."""
        app = StegVaultTUI()
        app.exit = Mock()

        # Mock screen stack with multiple screens
        mock_screens = [Mock(), Mock(), Mock()]  # 3 screens
        app.pop_screen = Mock()
        app.call_later = Mock()

        # Mock confirmation dialog
        mock_app_class = Mock()
        mock_app_class.push_screen_wait = AsyncMock(return_value=True)

        with patch.object(type(app), "screen_stack", property(lambda self: mock_screens)):
            with patch.object(type(app), "push_screen_wait", mock_app_class.push_screen_wait):
                await app._async_quit()

        # Should pop screens until only 1 remains
        assert app.pop_screen.call_count == 2
        app.call_later.assert_called_once()

    @pytest.mark.skip(reason="Complex async loop with file selection retry - difficult to mock")
    async def test_async_open_vault_path_truncation(self):
        """Should truncate long file paths in passphrase prompt."""
        pass

    @pytest.mark.asyncio
    async def test_async_open_vault_null_vault(self):
        """Should handle vault loaded but with no data."""
        app = StegVaultTUI()
        app.notify = Mock()

        # Mock file selection
        mock_app = Mock()
        mock_app.push_screen_wait = AsyncMock(side_effect=["test.png", "passphrase123"])

        # Mock vault controller to return success but null vault
        from stegvault.app.controllers import VaultLoadResult

        app.vault_controller.load_vault = Mock(
            return_value=VaultLoadResult(success=True, vault=None, error=None)
        )

        with patch.object(type(app), "push_screen_wait", mock_app.push_screen_wait):
            await app._async_open_vault()

        # Should notify about no data
        app.notify.assert_called_with("Vault loaded but contains no data", severity="warning")
