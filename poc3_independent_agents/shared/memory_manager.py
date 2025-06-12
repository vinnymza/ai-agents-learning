#!/usr/bin/env python3
"""
Memory Manager - File System Abstraction Layer

This class provides a clean abstraction over file system operations for JSON-based
memory storage. It handles all the low-level concerns like file I/O, directory
creation, and error handling.

Key responsibilities:
- Abstract file system operations from components
- Handle JSON serialization/deserialization 
- Manage directory creation automatically
- Provide foundation for future database integration
- Ensure consistent file handling across all components

Design principle: Components should not know about files, paths, or JSON.
They should only work with Python dictionaries.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any


class MemoryManager:
    """
    Abstraction layer for persistent memory storage operations.
    
    This class isolates components from file system details, making it easy
    to swap JSON files for databases in the future without changing component code.
    
    Each component gets its own MemoryManager instance pointing to its specific
    memory file location.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize memory manager with specific file path.
        
        Args:
            file_path (str): Path to the JSON memory file
                           Example: "components/communication/memory/conversation_memory.json"
        """
        self.file_path = Path(file_path)
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self) -> None:
        """
        Create directory structure if it doesn't exist.
        
        This ensures that components don't need to worry about creating
        their memory directories manually.
        """
        directory = self.file_path.parent
        directory.mkdir(parents=True, exist_ok=True)
    
    def read(self) -> Dict[str, Any]:
        """
        Read the entire memory structure as a Python dictionary.
        
        This is the main interface for components to access their stored data.
        If the file doesn't exist, returns an empty dictionary to allow
        components to initialize their structure naturally.
        
        Returns:
            Dict[str, Any]: Complete memory structure or empty dict if file doesn't exist
            
        Raises:
            json.JSONDecodeError: If file contains invalid JSON
            PermissionError: If file cannot be read due to permissions
        """
        try:
            if not self.file_path.exists():
                return {}
                
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
                
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {self.file_path}: {str(e)}")
            raise
        except PermissionError as e:
            print(f"ERROR: Cannot read {self.file_path}: {str(e)}")
            raise
    
    def write(self, data: Dict[str, Any]) -> None:
        """
        Write the complete memory structure to file.
        
        This completely replaces the existing file content with new data.
        Components are responsible for reading current data, modifying it,
        and writing it back.
        
        Args:
            data (Dict[str, Any]): Complete memory structure to persist
            
        Raises:
            PermissionError: If file cannot be written due to permissions
            OSError: If there are file system issues
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
                
        except PermissionError as e:
            print(f"ERROR: Cannot write to {self.file_path}: {str(e)}")
            raise
        except OSError as e:
            print(f"ERROR: File system error writing {self.file_path}: {str(e)}")
            raise
    
    def exists(self) -> bool:
        """
        Check if the memory file exists.
        
        Useful for components to determine if they need to initialize
        their memory structure or if they can load existing data.
        
        Returns:
            bool: True if memory file exists, False otherwise
        """
        return self.file_path.exists()
    
    def delete(self) -> None:
        """
        Delete the memory file.
        
        Useful for testing or resetting component state.
        Does not raise error if file doesn't exist.
        """
        try:
            if self.file_path.exists():
                self.file_path.unlink()
        except OSError as e:
            print(f"ERROR: Cannot delete {self.file_path}: {str(e)}")
            raise
    
    def get_file_size(self) -> int:
        """
        Get the size of the memory file in bytes.
        
        Useful for monitoring memory usage and implementing
        memory cleanup policies.
        
        Returns:
            int: File size in bytes, 0 if file doesn't exist
        """
        try:
            if self.file_path.exists():
                return self.file_path.stat().st_size
            return 0
        except OSError:
            return 0
    
    def backup(self, backup_suffix: str = ".backup") -> None:
        """
        Create a backup copy of the current memory file.
        
        Useful for implementing safety mechanisms or versioning.
        
        Args:
            backup_suffix (str): Suffix to add to backup file name
        """
        if not self.file_path.exists():
            return
            
        backup_path = self.file_path.with_suffix(self.file_path.suffix + backup_suffix)
        
        try:
            backup_path.write_bytes(self.file_path.read_bytes())
        except OSError as e:
            print(f"ERROR: Cannot create backup {backup_path}: {str(e)}")
            raise
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return f"MemoryManager({self.file_path})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        exists = "exists" if self.exists() else "not found"
        size = self.get_file_size()
        return f"MemoryManager(path='{self.file_path}', {exists}, {size} bytes)"