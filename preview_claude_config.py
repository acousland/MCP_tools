#!/usr/bin/env python3
"""
Preview Claude Desktop Configuration

This script shows what the Claude Desktop configuration will look like
without actually writing it to the system.
"""

import json
import sys
from pathlib import Path
from generate_claude_config import create_mcp_config, get_claude_config_path

def preview_config():
    """Preview the configuration that would be generated."""
    print("🔍 Claude Desktop MCP Configuration Preview")
    print("=" * 55)
    
    # Get the configuration
    config = create_mcp_config()
    config_path = get_claude_config_path()
    
    print(f"📁 Configuration file path:")
    print(f"   {config_path}")
    
    print(f"\n📋 Configuration content:")
    print("-" * 40)
    print(json.dumps(config, indent=2))
    
    print(f"\n🔧 MCP Servers that will be added:")
    print("-" * 40)
    
    for server_name, server_config in config["mcpServers"].items():
        print(f"📡 {server_name}")
        print(f"   Command: {server_config['command']}")
        print(f"   Args: {' '.join(server_config['args'])}")
        if server_config.get('env'):
            print(f"   Environment: {server_config['env']}")
        print()
    
    print(f"💡 To generate the actual configuration file, run:")
    print(f"   python generate_claude_config.py")

if __name__ == "__main__":
    preview_config()
