import os
import glob

def read_file(path: str) -> str:
    """Reads content from a file."""
    try:
        if not os.path.exists(path):
            return f"[ERROR] File '{path}' does not exist."
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return content[:8000] # Limit size for context window
    except Exception as e:
        return f"[ERROR] Could not read file: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Writes content to a file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{path}'."
    except Exception as e:
        return f"[ERROR] Could not write file: {str(e)}"

def list_workspace(directory: str = ".") -> str:
    """Lists files and folders in a directory."""
    try:
        if not os.path.exists(directory):
            return f"[ERROR] Directory '{directory}' does not exist."
        items = os.listdir(directory)
        formatted = []
        for item in sorted(items):
            full_path = os.path.join(directory, item)
            kind = "[DIR]" if os.path.isdir(full_path) else "[FILE]"
            size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
            formatted.append(f"{kind} {item} ({size} bytes)")
        return "\n".join(formatted[:50])
    except Exception as e:
        return f"[ERROR] Could not list directory: {str(e)}"
