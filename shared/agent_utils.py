#!/usr/bin/env python3
import json
import os
import time
import fcntl
import random
from pathlib import Path

class AgentCommunication:
    """Utility class for agent communication using a shared JSON file with locking"""
    
    def __init__(self, json_path, agent_name):
        """Initialize the communication utility with the shared JSON path and agent name"""
        self.json_path = Path(json_path)
        self.agent_name = agent_name
        self.lock_path = self.json_path.parent / "comm.lock"
    
    def read_json(self):
        """Read the shared JSON file with lock protection"""
        with open(self.lock_path, 'r+') as lock_file:
            # Acquire an exclusive lock
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            try:
                with open(self.json_path, 'r') as f:
                    data = json.load(f)
                return data
            finally:
                # Release the lock
                fcntl.flock(lock_file, fcntl.LOCK_UN)
    
    def write_json(self, data):
        """Write to the shared JSON file with lock protection"""
        with open(self.lock_path, 'r+') as lock_file:
            # Acquire an exclusive lock
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            try:
                with open(self.json_path, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            finally:
                # Release the lock
                fcntl.flock(lock_file, fcntl.LOCK_UN)
    
    def update_status(self, status, message=None):
        """Update the agent's status in the shared JSON"""
        data = self.read_json()
        
        # Update agent status
        data["agents"][self.agent_name]["status"] = status
        
        if message:
            data["agents"][self.agent_name]["message"] = message
            
        # Add timestamp
        data["agents"][self.agent_name]["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        self.write_json(data)
    
    def check_other_agents_status(self, target_status=None):
        """Check if all other agents have reached the specified status"""
        data = self.read_json()
        
        for agent, info in data["agents"].items():
            if agent != self.agent_name:
                if target_status is None:
                    # If no specific status is provided, just return the statuses
                    return {agent: info["status"] for agent in data["agents"] if agent != self.agent_name}
                elif info["status"] != target_status:
                    return False
        
        return True if target_status else {}
    
    def send_message_to_agent(self, target_agent, message_key, message_content):
        """Send a message to a specific agent through the shared JSON"""
        data = self.read_json()
        
        # Create messages section if it doesn't exist
        if "messages" not in data:
            data["messages"] = {}
        
        # Create messages section for target agent if it doesn't exist
        if target_agent not in data["messages"]:
            data["messages"][target_agent] = {}
        
        # Add the message with a timestamp
        data["messages"][target_agent][message_key] = {
            "content": message_content,
            "from": self.agent_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "read": False
        }
        
        self.write_json(data)
    
    def get_messages(self, mark_as_read=True):
        """Get messages directed to this agent"""
        data = self.read_json()
        
        if "messages" not in data or self.agent_name not in data["messages"]:
            return {}
        
        messages = data["messages"][self.agent_name]
        
        if mark_as_read and messages:
            # Mark all messages as read
            for key in messages:
                data["messages"][self.agent_name][key]["read"] = True
            self.write_json(data)
        
        return messages
    
    def increment_iteration(self):
        """Increment the iteration counter in the shared JSON"""
        data = self.read_json()
        
        data["iterations"] += 1
        self.write_json(data)
        
        return data["iterations"]
    
    def wait_with_backoff(self, condition_func, max_attempts=5, initial_wait=1):
        """Wait with exponential backoff until a condition is met"""
        wait_time = initial_wait
        attempts = 0
        
        while attempts < max_attempts:
            if condition_func():
                return True
            
            # Add some randomness to avoid thundering herd problems
            jitter = random.uniform(0.8, 1.2)
            sleep_time = wait_time * jitter
            
            print(f"{self.agent_name} waiting for {sleep_time:.2f}s...")
            time.sleep(sleep_time)
            
            wait_time *= 2
            attempts += 1
        
        return False