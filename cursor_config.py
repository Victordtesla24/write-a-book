"""Cursor configuration module."""


class CursorConfig:
    """Configuration class for Cursor."""
    
    def __init__(self):
        self.attached_files = []
        
    def attach_files(self, files):
        """Attach files to the configuration."""
        if isinstance(files, str):
            files = [files]
        self.attached_files.extend(files)
        
    def get_attached_files(self):
        """Get list of attached files."""
        return self.attached_files


CURSOR_CONFIG = CursorConfig()
