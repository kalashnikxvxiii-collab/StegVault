"""
TUI screens for StegVault.

Provides main application screens for vault management.
"""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, ListView, Button, Label
from textual.screen import Screen
from textual.binding import Binding

from stegvault.vault import Vault, VaultEntry
from stegvault.app.controllers import VaultController

from .widgets import EntryListItem, EntryDetailPanel


class VaultScreen(Screen):
    """Main vault management screen."""

    CSS = """
    VaultScreen {
        background: $surface;
    }

    #vault-container {
        height: 100%;
    }

    #vault-header {
        height: 3;
        background: $primary;
        color: $text;
        padding: 0 2;
        dock: top;
    }

    #vault-title {
        text-style: bold;
    }

    #vault-path {
        color: $text-muted;
        margin-left: 2;
    }

    #main-panel {
        height: 1fr;
    }

    #entry-list-container {
        width: 30%;
        border-right: solid $accent;
    }

    #entry-list-header {
        height: 3;
        background: $panel;
        padding: 0 1;
    }

    #entry-count {
        color: $text-muted;
    }

    #entry-list {
        height: 1fr;
    }

    #detail-container {
        width: 70%;
    }

    .entry-item {
        padding: 0 1;
    }

    .entry-item:hover {
        background: $primary 20%;
    }

    ListItem.--highlight {
        background: $primary;
    }

    #action-bar {
        height: 3;
        background: $panel;
        dock: bottom;
        padding: 0 2;
    }

    .action-button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back to Menu"),
        Binding("c", "copy_password", "Copy Password"),
        Binding("v", "toggle_password", "Show/Hide Password"),
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, vault: Vault, image_path: str, controller: VaultController):
        """Initialize vault screen."""
        super().__init__()
        self.vault = vault
        self.image_path = image_path
        self.controller = controller
        self.selected_entry: Optional[VaultEntry] = None

    def compose(self) -> ComposeResult:
        """Compose vault screen layout."""
        yield Header()

        with Container(id="vault-container"):
            # Vault header
            with Horizontal(id="vault-header"):
                yield Label(f"Vault: {self.vault.name or 'Unnamed'}", id="vault-title")
                yield Label(f"📁 {self.image_path}", id="vault-path")

            # Main panel with entry list and details
            with Horizontal(id="main-panel"):
                # Entry list
                with Vertical(id="entry-list-container"):
                    with Horizontal(id="entry-list-header"):
                        yield Label("Entries", id="entry-list-title")
                        yield Label(f"({len(self.vault.entries)})", id="entry-count")

                    entry_list = ListView(id="entry-list")
                    for entry in self.vault.entries:
                        entry_list.append(EntryListItem(entry))
                    yield entry_list

                # Detail panel
                with Container(id="detail-container"):
                    yield EntryDetailPanel()

            # Action bar
            with Horizontal(id="action-bar"):
                yield Button(
                    "Copy Password", variant="primary", id="btn-copy", classes="action-button"
                )
                yield Button(
                    "Show/Hide", variant="default", id="btn-toggle", classes="action-button"
                )
                yield Button(
                    "Refresh", variant="default", id="btn-refresh", classes="action-button"
                )
                yield Button("Back", variant="default", id="btn-back", classes="action-button")

        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle entry selection."""
        if isinstance(event.item, EntryListItem):
            self.selected_entry = event.item.entry
            detail_panel = self.query_one(EntryDetailPanel)
            detail_panel.show_entry(self.selected_entry)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        button_id = event.button.id

        if button_id == "btn-copy":
            self.action_copy_password()
        elif button_id == "btn-toggle":
            self.action_toggle_password()
        elif button_id == "btn-refresh":
            self.action_refresh()
        elif button_id == "btn-back":
            self.action_back()

    def action_copy_password(self) -> None:
        """Copy selected entry password to clipboard."""
        if self.selected_entry:
            try:
                import pyperclip

                pyperclip.copy(self.selected_entry.password)
                self.notify(
                    f"Password copied for '{self.selected_entry.key}'",
                    severity="information",
                )
            except Exception as e:
                self.notify(f"Failed to copy password: {e}", severity="error")
        else:
            self.notify("No entry selected", severity="warning")

    def action_toggle_password(self) -> None:
        """Toggle password visibility."""
        if self.selected_entry:
            detail_panel = self.query_one(EntryDetailPanel)
            detail_panel.toggle_password_visibility()
        else:
            self.notify("No entry selected", severity="warning")

    def action_refresh(self) -> None:
        """Refresh vault from disk."""
        self.notify("Refresh feature - Coming soon!", severity="information")

    def action_back(self) -> None:
        """Return to welcome screen."""
        self.app.pop_screen()

    def action_quit(self) -> None:
        """Quit application."""
        self.app.exit()
