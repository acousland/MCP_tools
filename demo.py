#!/usr/bin/env python3
"""
Demo script to show MCP Tools in action.
"""

import subprocess
import time
import requests
import json
import sys
import os

def run_demo():
    print("🚀 MCP Tools Demo")
    print("=" * 50)
    
    # Start the file server in background
    print("Starting File Server...")
    
    file_server_process = subprocess.Popen([
        sys.executable, "servers/file_server.py", "--http"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Give it time to start
    time.sleep(3)
    
    # Test the server
    try:
        print("Testing File Server...")
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        
        # Test reading the README
        payload = {
            "tool": "read_file",
            "arguments": {"file_path": "README.md"}
        }
        
        response = requests.post("http://127.0.0.1:8001/call", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully read README.md")
            content = result.get("result", "")
            lines = content.split('\n')
            print(f"   File has {len(lines)} lines")
            print(f"   First line: {lines[0] if lines else 'Empty'}")
        else:
            print(f"❌ Failed to read file: {response.status_code}")
        
        # Test directory listing
        payload = {
            "tool": "list_directory", 
            "arguments": {"dir_path": "."}
        }
        
        response = requests.post("http://127.0.0.1:8001/call", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully listed directory")
            listing = result.get("result", "")
            # Count files mentioned
            file_count = listing.count("📄")
            folder_count = listing.count("📁")
            print(f"   Found {file_count} files and {folder_count} folders")
        else:
            print(f"❌ Failed to list directory: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing file server: {e}")
    
    finally:
        # Clean up
        print("\nStopping File Server...")
        file_server_process.terminate()
        try:
            file_server_process.wait(timeout=5)
        except:
            file_server_process.kill()
        
    print("\n🎉 Demo completed!")
    print("\nTo run the full system:")
    print("  python3 main.py")

if __name__ == "__main__":
    run_demo()
