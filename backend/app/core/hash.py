import hashlib
import json
import os
from typing import Any

def sha256_string(text: str) -> str:
    """
    Returns the SHA256 hex digest of a string.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_json(data: Any) -> str:
    """
    Returns the SHA256 hex digest of a JSON-serializable object, sorted by key.
    """
    serialized = json.dumps(data, sort_keys=True, default=str)
    return sha256_string(serialized)

def sha256_file(filepath: str) -> str:
    """
    Returns the SHA256 hex digest of a file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found for hashing: {filepath}")
    
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

def sha256_directory(dirpath: str) -> str:
    """
    Returns the SHA256 hex digest of a directory's files (based on filenames and contents).
    """
    if not os.path.exists(dirpath):
        raise FileNotFoundError(f"Directory not found for hashing: {dirpath}")
        
    sha256 = hashlib.sha256()
    for root, _, files in sorted(os.walk(dirpath)):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            # Add relative filename to hash
            rel_path = os.path.relpath(file_path, dirpath)
            sha256.update(rel_path.encode("utf-8"))
            # Add file content hash
            try:
                f_hash = sha256_file(file_path)
                sha256.update(f_hash.encode("utf-8"))
            except Exception:
                pass
    return sha256.hexdigest()
