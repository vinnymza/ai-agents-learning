#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_agent(script_path, lock, json_path, base_dir):
    """Execute an agent script and allow it to update the shared JSON file"""
    # Ensure the script is executable
    script_path.chmod(0o755)
    
    print(f"\n{'='*50}")
    print(f"Iniciando {script_path.name}...")
    print(f"{'='*50}")
    
    # Execute the script with the lock path as an argument
    # This allows agents to coordinate access to the shared JSON
    result = subprocess.run(
        [script_path, str(json_path)], 
        check=True,
        capture_output=True,
        text=True
    )
    
    print(f"{script_path.name} output:")
    print(result.stdout)
    
    return script_path.name

def main():
    # Get project base path
    base_dir = Path(__file__).parent
    json_path = base_dir / 'shared' / 'communication.json'
    lock_path = base_dir / 'shared' / 'comm.lock'
    
    # Get task from command line or use default
    default_task = "Implementar login con Google"
    task = sys.argv[1] if len(sys.argv) > 1 else default_task
    
    # Initialize communication.json with task and workflow state
    initial_data = {
        "task": task,
        "workflow_state": "initialized",
        "agents": {
            "product_owner": {"status": "pending"},
            "staff_engineer": {"status": "pending"},
            "engineering_manager": {"status": "pending"}
        },
        "iterations": 0,
        "max_iterations": 3
    }
    
    with open(json_path, 'w') as f:
        json.dump(initial_data, f, indent=2)
    
    # Create a lock file
    with open(lock_path, 'w') as f:
        f.write("")
    
    print(f"Inicializado {json_path} con la tarea: {initial_data['task']}")
    
    # Agent scripts to execute
    scripts = [
        'agents/product_owner.py',
        'agents/staff_engineer.py',
        'agents/engineering_manager.py'
    ]
    
    # Create lock object for thread synchronization
    lock = threading.Lock()
    
    # Execute scripts sequentially for better coordination
    script_paths = [base_dir / script for script in scripts]
    
    for script_path in script_paths:
        try:
            result = run_agent(script_path, lock, json_path, base_dir)
            print(f"Agent {script_path.name} completed successfully")
        except Exception as e:
            print(f"Agent {script_path.name} generated an exception: {e}")
            # Continue with the next agent even if one fails
    
    # Clean up lock file
    lock_path.unlink(missing_ok=True)
    
    # Show final content of the JSON file
    print(f"\n{'='*50}")
    print("Contenido final de communication.json:")
    print(f"{'='*50}")
    with open(json_path, 'r') as f:
        final_data = json.load(f)
        print(json.dumps(final_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()