"""
Custom widgets for StegVault TUI.

Provides reusable UI components for the terminal interface.
"""

from pathlib import Path
from typing import Optional, Callable

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import (
    Static,
    Input,
    Button,
    Label,
    ListView,
    ListItem,
    DirectoryTree,
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding

from stegvault.vault import Vault, VaultEntry


class FileSelectScreen(ModalScreen[Optional[str]]):
    """Modal screen for selecting a vault image file."""

    CSS = """
    FileSelectScreen {
        align: center middle;
    }

    #file-dialog {
        width: 80;
        height: 30;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    #file-tree {
        height: 20;
        border: solid $accent;
        margin-bottom: 1;
    }

    #file-path-input {
        margin-bottom: 1;
    }

    #button-row {
        height: 3;
        align: center middle;
    }

    .file-button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, title: str = "Select Vault Image"):
        """Initialize file selection screen."""
        super().__init__()
        self.title = title
        self.selected_path: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose file selection dialog."""
        with Container(id="file-dialog"):
            yield Label(self.title)
            yield DirectoryTree(".", id="file-tree")
            yield Input(
                placeholder="Enter file path or select from tree",
                id="file-path-input",
            )
            with Horizontal(id="button-row"):
                yield Button("Select", variant="primary", id="btn-select", classes="file-button")
                yield Button("Cancel", variant="default", id="btn-cancel", classes="file-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-select":
            input_widget = self.query_one("#file-path-input", Input)
            path = input_widget.value.strip()

            if path and Path(path).exists():
                self.dismiss(path)
            else:
                self.app.notify("Please enter a valid file path", severity="error")
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection from tree."""
        input_widget = self.query_one("#file-path-input", Input)
        input_widget.value = str(event.path)

    def action_cancel(self) -> None:
        """Cancel and close dialog."""
        self.dismiss(None)


class PassphraseInputScreen(ModalScreen[Optional[str]]):
    """Modal screen for passphrase input."""

    CSS = """
    PassphraseInputScreen {
        align: center middle;
    }

    #passphrase-dialog {
        width: 60;
        height: 15;
        border: thick $primary;
        background: $surface;
        padding: 2;
    }

    #passphrase-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #passphrase-input {
        margin-bottom: 2;
    }

    #button-row {
        height: 3;
        align: center middle;
    }

    .pass-button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, title: str = "Enter Passphrase"):
        """Initialize passphrase input screen."""
        super().__init__()
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose passphrase dialog."""
        with Container(id="passphrase-dialog"):
            yield Label(self.title, id="passphrase-title")
            yield Input(
                placeholder="Enter vault passphrase",
                password=True,
                id="passphrase-input",
            )
            with Horizontal(id="button-row"):
                yield Button("Unlock", variant="primary", id="btn-unlock", classes="pass-button")
                yield Button("Cancel", variant="default", id="btn-cancel", classes="pass-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "btn-unlock":
            input_widget = self.query_one("#passphrase-input", Input)
            passphrase = input_widget.value

            if passphrase:
                self.dismiss(passphrase)
            else:
                self.app.notify("Passphrase cannot be empty", severity="error")
        elif event.button.id == "btn-cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input."""
        if event.input.id == "passphrase-input" and event.value:
            self.dismiss(event.value)

    def action_cancel(self) -> None:
        """Cancel and close dialog."""
        self.dismiss(None)


class EntryListItem(ListItem):
    """List item for a vault entry."""

    def __init__(self, entry: VaultEntry):
        """Initialize entry list item."""
        super().__init__()
        self.entry = entry
        self.add_class("entry-item")

    def render(self) -> str:
        """Render entry list item."""
        tags_str = f" [{', '.join(self.entry.tags)}]" if self.entry.tags else ""
        return f"{self.entry.key}{tags_str}"


class EntryDetailPanel(Container):
    """Panel displaying details of a vault entry."""

    CSS = """
    EntryDetailPanel {
        height: 100%;
        border: solid $accent;
        padding: 1;
    }

    .detail-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .detail-field {
        margin-bottom: 1;
    }

    .field-label {
        color: $text-muted;
        text-style: italic;
    }

    .field-value {
        margin-left: 2;
    }

    .password-masked {
        color: $warning;
    }

    #no-entry-msg {
        color: $text-muted;
        text-align: center;
        margin-top: 5;
    }
    """

    def __init__(self):
        """Initialize entry detail panel."""
        super().__init__()
        self.current_entry: Optional[VaultEntry] = None
        self.password_visible = False

    def compose(self) -> ComposeResult:
        """Compose detail panel."""
        yield ScrollableContainer(
            Label("No entry selected", id="no-entry-msg"),
            id="detail-content",
        )

    def show_entry(self, entry: VaultEntry) -> None:
        """Display entry details."""
        self.current_entry = entry
        self.password_visible = False
        self._update_display()

    def toggle_password_visibility(self) -> None:
        """Toggle password visibility."""
        if self.current_entry:
            self.password_visible = not self.password_visible
            self._update_display()

    def _update_display(self) -> None:
        """Update the display with current entry details."""
        if not self.current_entry:
            content = ScrollableContainer(
                Label("No entry selected", id="no-entry-msg"),
                id="detail-content",
            )
        else:
            entry = self.current_entry
            widgets = [
                Label(f"Entry: {entry.key}", classes="detail-title"),
            ]

            # Password field
            password_display = (
                entry.password if self.password_visible else "*" * len(entry.password)
            )
            widgets.append(
                Vertical(
                    Label("Password:", classes="field-label"),
                    Label(password_display, classes="field-value password-masked"),
                    classes="detail-field",
                )
            )

            # Username
            if entry.username:
                widgets.append(
                    Vertical(
                        Label("Username:", classes="field-label"),
                        Label(entry.username, classes="field-value"),
                        classes="detail-field",
                    )
                )

            # URL
            if entry.url:
                widgets.append(
                    Vertical(
                        Label("URL:", classes="field-label"),
                        Label(entry.url, classes="field-value"),
                        classes="detail-field",
                    )
                )

            # Tags
            if entry.tags:
                widgets.append(
                    Vertical(
                        Label("Tags:", classes="field-label"),
                        Label(", ".join(entry.tags), classes="field-value"),
                        classes="detail-field",
                    )
                )

            # Notes
            if entry.notes:
                widgets.append(
                    Vertical(
                        Label("Notes:", classes="field-label"),
                        Label(entry.notes, classes="field-value"),
                        classes="detail-field",
                    )
                )

            # TOTP
            if entry.totp_secret:
                widgets.append(
                    Vertical(
                        Label("TOTP:", classes="field-label"),
                        Label("✓ Configured", classes="field-value"),
                        classes="detail-field",
                    )
                )

            # Timestamps
            widgets.append(
                Vertical(
                    Label("Created:", classes="field-label"),
                    Label(entry.created, classes="field-value"),
                    classes="detail-field",
                )
            )

            if entry.modified != entry.created:
                widgets.append(
                    Vertical(
                        Label("Modified:", classes="field-label"),
                        Label(entry.modified, classes="field-value"),
                        classes="detail-field",
                    )
                )

            content = ScrollableContainer(*widgets, id="detail-content")

        # Replace content
        old_content = self.query_one("#detail-content")
        old_content.remove()
        self.mount(content)

    def clear(self) -> None:
        """Clear the detail panel."""
        self.current_entry = None
        self.password_visible = False
        self._update_display()
