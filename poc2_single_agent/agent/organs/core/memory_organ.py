#!/usr/bin/env python3
import json
import time
from pathlib import Path
from typing import Dict, Any

class MemoryOrgan:
    """
    Core Memory Organ - Handles all memory storage operations
    
    Receives data with or without structure, formats it properly,
    and stores it in the appropriate memory file.
    """
    
    def __init__(self, memory_path: str):
        self.memory_path = Path(memory_path)
    
    def store(self, memory_type: str, data: Any):
        """
        Store data in the specified memory type
        Structures the data and appends to the appropriate file
        """
        # Store data in specified memory type
        
        if memory_type == "session":
            structured_entry = self._store_session_data(data)
        elif memory_type == "requirements":
            structured_entry = self._store_requirements_data(data)
        elif memory_type == "project":
            structured_entry = self._store_project_data(data)
        elif memory_type == "initial":
            structured_entry = self._store_initial_data(data)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
        
        return structured_entry
    
    def _store_session_data(self, data: Any):
        """Structure and store session data"""
        memory_file = self.memory_path / "session_memory.json"
        
        # Check if data is already structured (from consciousness with speaker info)
        if isinstance(data, dict) and "speaker" in data and "message" in data:
            structured_entry = {
                "speaker": data["speaker"],
                "message": data["message"],
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        else:
            # Structure the message (assume user input)
            structured_entry = {
                "speaker": "user",
                "message": str(data),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        
        # Load existing session memory or create new
        try:
            with open(memory_file, 'r') as f:
                session_memory = json.load(f)
        except FileNotFoundError:
            # Create new session memory structure
            session_memory = {
                "session_id": f"session_{int(time.time())}",
                "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "conversation_flow": [],
                "session_metadata": {
                    "total_messages": 0,
                    "status": "active"
                }
            }
        
        # Append the new entry
        session_memory["conversation_flow"].append(structured_entry)
        session_memory["session_metadata"]["total_messages"] += 1
        
        # Write back to file
        with open(memory_file, 'w') as f:
            json.dump(session_memory, f, indent=2, ensure_ascii=False)
        
        # Data stored successfully
        
        return structured_entry
    
    def _store_requirements_data(self, data: Any):
        """Structure and store requirements data"""
        memory_file = self.memory_path / "requirements_memory.json"
        
        # If data is already structured (from reasoning organ), store as-is
        if isinstance(data, dict):
            requirements_data = data
        else:
            # If raw input, create initial structure
            requirements_data = {
                "raw_requirements": str(data),
                "functional_analysis": {
                    "main_problem": "",
                    "identified_users": [],
                    "main_use_cases": [],
                    "assumptions": [],
                    "risks": [],
                    "pending_questions": []
                },
                "identified_epics": []
            }
        
        # Add timestamp
        requirements_data["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Write to file
        with open(memory_file, 'w') as f:
            json.dump(requirements_data, f, indent=2, ensure_ascii=False)
        
        return requirements_data
    
    def _store_project_data(self, data: Any):
        """Structure and store project data"""
        # TODO: Implement project memory structure
        print(f"📊 Project storage not implemented yet")
    
    def _store_initial_data(self, data: Any):
        """Structure and store initial memory data"""
        # TODO: Implement initial memory structure
        print(f"🏗️ Initial storage not implemented yet")
    
    def retrieve(self, memory_type: str):
        """Retrieve data from specified memory type"""
        if memory_type == "initial":
            # Read text file for initial memory
            memory_file = self.memory_path / "initial_memory.txt"
            try:
                with open(memory_file, 'r') as f:
                    return f.read()
            except FileNotFoundError:
                return ""
        else:
            # Read JSON files for other memory types
            memory_file = self.memory_path / f"{memory_type}_memory.json"
            try:
                with open(memory_file, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                return {}