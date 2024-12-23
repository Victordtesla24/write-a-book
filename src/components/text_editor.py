"""Text editor component for handling text editing functionality."""

from typing import List, Optional


class EditorComponent:
    """Component for handling text editing operations."""

    def __init__(self) -> None:
        self.content = ""
        self.cursor_position = 0
        self.selection_start: Optional[int] = None
        self.selection_end: Optional[int] = None
        self._undo_stack: List[str] = []
        self._redo_stack: List[str] = []

    def set_content(self, content: str) -> None:
        """Set editor content."""
        self._push_undo_state()
        self.content = content
        self.cursor_position = len(content)
        self._redo_stack.clear()

    def get_content(self) -> str:
        """Get current editor content."""
        return self.content

    def move_cursor(self, position: int) -> None:
        """Move cursor to specified position."""
        self.cursor_position = max(0, min(position, len(self.content)))
        self.clear_selection()

    def select_text(self, start: int, end: int) -> None:
        """Select text range."""
        content_length = len(self.content)
        self.selection_start = max(0, min(start, content_length))
        self.selection_end = max(0, min(end, content_length))
        self.cursor_position = self.selection_end

    def get_selected_text(self) -> Optional[str]:
        """Get currently selected text."""
        if self.selection_start is None or self.selection_end is None:
            return None
        start = min(self.selection_start, self.selection_end)
        end = max(self.selection_start, self.selection_end)
        return self.content[start:end]

    def clear_selection(self) -> None:
        """Clear text selection."""
        self.selection_start = None
        self.selection_end = None

    def _push_undo_state(self) -> None:
        """Push current state to undo stack."""
        self._undo_stack.append(self.content)

    def undo(self) -> None:
        """Undo last change."""
        if self._undo_stack:
            self._redo_stack.append(self.content)
            self.content = self._undo_stack.pop()
            self.cursor_position = len(self.content)
            self.clear_selection()

    def redo(self) -> None:
        """Redo last undone change."""
        if self._redo_stack:
            self._push_undo_state()
            self.content = self._redo_stack.pop()
            self.cursor_position = len(self.content)
            self.clear_selection()
