#!/usr/bin/env python3
"""
Test script for MCP Tools servers.
This script tests the basic functionality of all MCP servers.
"""

import requests
import json
import time
import sys

def test_server(name: str, port: int, tools: list) -> bool:
    """Test a single MCP server."""
    base_url = f"http://127.0.0.1:{port}"
    
    print(f"\n🧪 Testing {name} (port {port})")
    print("-" * 40)
    
    try:
        # Test server health
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
        
        print(f"✅ Server is responding on port {port}")
        
        # Test tools endpoint
        response = requests.get(f"{base_url}/tools", timeout=5)
        if response.status_code == 200:
            available_tools = response.json()
            print(f"✅ Available tools: {len(available_tools)}")
            for tool in available_tools:
                print(f"   - {tool.get('name', 'Unknown')}")
        else:
            print(f"⚠️  Could not fetch tools list: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {name}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout connecting to {name}")
        return False
    except Exception as e:
        print(f"❌ Error testing {name}: {e}")
        return False

def test_file_server():
    """Test file server specific functionality."""
    print("\n📁 Testing File Server functionality")
    print("-" * 40)
    
    base_url = "http://127.0.0.1:8001"
    
    try:
        # Test reading the README file
        payload = {
            "tool": "read_file",
            "arguments": {
                "file_path": "README.md"
            }
        }
        
        response = requests.post(f"{base_url}/call", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully read README.md")
            print(f"   Content length: {len(result.get('result', ''))}")
        else:
            print(f"❌ Failed to read file: {response.status_code}")
        
        # Test listing current directory
        payload = {
            "tool": "list_directory",
            "arguments": {
                "dir_path": "."
            }
        }
        
        response = requests.post(f"{base_url}/call", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully listed directory")
        else:
            print(f"❌ Failed to list directory: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing file server functionality: {e}")

def test_nmap_server():
    """Test NMAP server specific functionality."""
    print("\n🌐 Testing NMAP Server functionality")
    print("-" * 40)
    
    base_url = "http://127.0.0.1:8002"
    
    try:
        # Test ping localhost
        payload = {
            "tool": "ping_host",
            "arguments": {
                "host": "127.0.0.1",
                "count": 2
            }
        }
        
        response = requests.post(f"{base_url}/call", json=payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully pinged localhost")
        else:
            print(f"❌ Failed to ping host: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing NMAP server functionality: {e}")

def main():
    """Main test function."""
    print("🔬 MCP Tools - Server Tests")
    print("=" * 50)
    
    # Load configuration
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        servers = config.get("servers", [])
    except Exception as e:
        print(f"❌ Could not load configuration: {e}")
        sys.exit(1)
    
    # Wait for servers to be ready
    print("⏳ Waiting for servers to start...")
    time.sleep(3)
    
    # Test all servers
    results = []
    for server in servers:
        success = test_server(
            server["name"], 
            server["port"], 
            server.get("tools", [])
        )
        results.append((server["name"], success))
    
    # Test specific functionality
    test_file_server()
    test_nmap_server()
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\n🎯 {passed}/{total} servers passed basic tests")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check server logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
