from langchain.tools import tool
from pathlib import Path
import os

BASE = Path("data/workspace")
BASE.mkdir(parents=True, exist_ok=True)

@tool("File Write")
def fs_write(filepath: str, content: str = "") -> str:
    """Write content to a file. Supports both absolute and relative paths. Creates directories if needed.
    
    Args:
        filepath: Path to the file (absolute or relative to project root)
        content: Content to write to the file
    
    Examples:
        - filepath='test.txt', content='Hello World'
        - filepath='src/utils/helper.py', content='def helper(): pass'
    """
    try:
        # Convert to Path object
        if os.path.isabs(filepath):
            p = Path(filepath)
        else:
            # For relative paths, make them relative to current working directory
            p = Path.cwd() / filepath
        
        # Create parent directories if they don't exist
        p.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content with proper encoding
        p.write_text(content, encoding="utf-8")
        
        # Return success message with actual path
        return f"✅ Successfully created file: {p.absolute()}"
        
    except PermissionError:
        return f"❌ Permission denied: Cannot write to {filepath}"
    except Exception as e:
        return f"❌ Error writing file '{filepath}': {str(e)}"

@tool("Create Directory")
def create_directory(dirpath: str) -> str:
    """Create a directory (and parent directories if needed).
    
    Args:
        dirpath: Path to the directory to create
    """
    try:
        if os.path.isabs(dirpath):
            p = Path(dirpath)
        else:
            p = Path.cwd() / dirpath
            
        p.mkdir(parents=True, exist_ok=True)
        return f"✅ Successfully created directory: {p.absolute()}"
        
    except PermissionError:
        return f"❌ Permission denied: Cannot create directory {dirpath}"
    except Exception as e:
        return f"❌ Error creating directory '{dirpath}': {str(e)}"

@tool("File Read")
def fs_read(filepath: str) -> str:
    """Read content from a file. Use absolute path or relative to project root."""
    try:
        if os.path.isabs(filepath):
            p = Path(filepath)
        else:
            p = Path(filepath)
        
        if not p.exists():
            return f"File not found: {filepath}"
        return p.read_text(encoding="utf-8")[:10000]  # guardrails
    except Exception as e:
        return f"Error reading file: {str(e)}"
