#!/usr/bin/env python3
"""
Claude Desktop Config Generator for MCP Tools

This script generates a configuration file for Claude Desktop to use the MCP servers.
The configuration will be written to the appropriate location for your operating system.
"""

import json
import os
import sys
import platform
from pathlib import Path

def get_claude_config_path():
    """Get the Claude Desktop configuration file path based on OS."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        # Try XDG config dir first, fall back to ~/.config
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "Claude" / "claude_desktop_config.json"
        else:
            return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    else:
        raise ValueError(f"Unsupported operating system: {system}")

def get_python_executable():
    """Get the Python executable path for the virtual environment."""
    venv_path = Path(__file__).parent / ".venv"
    
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    if python_exe.exists():
        return str(python_exe.absolute())
    else:
        # Fallback to system Python
        return sys.executable

def create_mcp_config():
    """Create the MCP configuration for Claude Desktop."""
    
    # Get the current project directory
    project_dir = Path(__file__).parent.absolute()
    python_exe = get_python_executable()
    
    # File server configuration
    file_server_config = {
        "command": python_exe,
        "args": [str(project_dir / "servers" / "file_server.py")],
        "env": {
            "PYTHONPATH": str(project_dir)
        }
    }
    
    # NMAP server configuration  
    nmap_server_config = {
        "command": python_exe,
        "args": [str(project_dir / "servers" / "nmap_server.py")],
        "env": {
            "PYTHONPATH": str(project_dir)
        }
    }
    
    # SSH server configuration
    ssh_server_config = {
        "command": python_exe,
        "args": [str(project_dir / "servers" / "ssh_server.py")],
        "env": {
            "PYTHONPATH": str(project_dir)
        }
    }
    
    # FTP server configuration
    ftp_server_config = {
        "command": python_exe,
        "args": [str(project_dir / "servers" / "ftp_server.py")],
        "env": {
            "PYTHONPATH": str(project_dir)
        }
    }
    
    # Telnet server configuration
    telnet_server_config = {
        "command": python_exe,
        "args": [str(project_dir / "servers" / "telnet_server.py")],
        "env": {
            "PYTHONPATH": str(project_dir)
        }
    }
    
    # Complete configuration
    config = {
        "mcpServers": {
            "mcp-file-server": file_server_config,
            "mcp-nmap-server": nmap_server_config,
            "mcp-ssh-server": ssh_server_config,
            "mcp-ftp-server": ftp_server_config,
            "mcp-telnet-server": telnet_server_config
        }
    }
    
    return config

def backup_existing_config(config_path):
    """Create a backup of existing configuration if it exists."""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        counter = 1
        while backup_path.exists():
            backup_path = config_path.with_suffix(f'.json.backup.{counter}')
            counter += 1
        
        # Copy existing config to backup
        with open(config_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        
        print(f"📋 Existing configuration backed up to: {backup_path}")
        return backup_path
    return None

def merge_with_existing_config(config_path, new_config):
    """Merge new MCP servers with existing configuration."""
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            
            # Merge mcpServers sections
            if "mcpServers" in existing_config:
                # Update existing servers with new ones
                existing_config["mcpServers"].update(new_config["mcpServers"])
                print("🔄 Merged with existing MCP servers configuration")
            else:
                # Add mcpServers section
                existing_config["mcpServers"] = new_config["mcpServers"]
                print("➕ Added MCP servers to existing configuration")
            
            return existing_config
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Error reading existing config: {e}")
            print("Creating new configuration...")
            return new_config
    
    return new_config

def write_config():
    """Write the Claude Desktop configuration file."""
    try:
        # Get configuration path
        config_path = get_claude_config_path()
        print(f"📁 Claude Desktop config path: {config_path}")
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create new MCP configuration
        new_config = create_mcp_config()
        
        # Backup existing configuration
        backup_path = backup_existing_config(config_path)
        
        # Merge with existing configuration
        final_config = merge_with_existing_config(config_path, new_config)
        
        # Write configuration file
        with open(config_path, 'w') as f:
            json.dump(final_config, f, indent=2)
        
        print(f"✅ Claude Desktop configuration written to: {config_path}")
        
        # Show summary
        print(f"\n📊 Configuration Summary:")
        print(f"   MCP Servers: {len(final_config['mcpServers'])}")
        for server_name in final_config['mcpServers']:
            print(f"   - {server_name}")
        
        return config_path
        
    except Exception as e:
        print(f"❌ Error writing configuration: {e}")
        return None

def show_server_info():
    """Display information about the MCP servers."""
    print(f"\n🔧 MCP Server Information:")
    print(f"=" * 50)
    
    print(f"📁 File Server (mcp-file-server)")
    print(f"   Description: Read files and list directories from local machine")
    print(f"   Tools: read_file, list_directory, get_file_info")
    print(f"   Script: servers/file_server.py")
    
    print(f"\n🌐 NMAP Server (mcp-nmap-server)")
    print(f"   Description: Network scanning and connectivity testing")
    print(f"   Tools: nmap_scan, ping_host, port_scan, network_discovery")
    print(f"   Script: servers/nmap_server.py")
    
    print(f"\n🔐 SSH Server (mcp-ssh-server)")
    print(f"   Description: SSH remote command execution and file transfer")
    print(f"   Tools: ssh_execute, ssh_copy_file, ssh_tunnel, ssh_key_info")
    print(f"   Script: servers/ssh_server.py")
    
    print(f"\n📂 FTP Server (mcp-ftp-server)")
    print(f"   Description: FTP file transfer and server operations")
    print(f"   Tools: ftp_list_files, ftp_download_file, ftp_upload_file, ftp_server_info")
    print(f"   Script: servers/ftp_server.py")
    
    print(f"\n📡 Telnet Server (mcp-telnet-server)")
    print(f"   Description: Telnet connectivity testing and basic operations")
    print(f"   Tools: telnet_connect, telnet_execute, telnet_port_check, telnet_banner_grab")
    print(f"   Script: servers/telnet_server.py")

def validate_setup():
    """Validate that the MCP servers are properly set up."""
    project_dir = Path(__file__).parent
    python_exe = get_python_executable()
    
    print(f"\n🔍 Validating Setup:")
    print(f"-" * 30)
    
    # Check Python executable
    if Path(python_exe).exists():
        print(f"✅ Python executable: {python_exe}")
    else:
        print(f"❌ Python executable not found: {python_exe}")
        return False
    
    # Check server scripts
    servers = [
        ("file_server.py", "File server"),
        ("nmap_server.py", "NMAP server"),
        ("ssh_server.py", "SSH server"),
        ("ftp_server.py", "FTP server"),
        ("telnet_server.py", "Telnet server")
    ]
    
    all_found = True
    for script_name, description in servers:
        script_path = project_dir / "servers" / script_name
        if script_path.exists():
            print(f"✅ {description} script: {script_path}")
        else:
            print(f"❌ {description} script not found: {script_path}")
            all_found = False
    
    # Check virtual environment
    venv_path = project_dir / ".venv"
    if venv_path.exists():
        print(f"✅ Virtual environment: {venv_path}")
    else:
        print(f"⚠️  Virtual environment not found: {venv_path}")
    
    return all_found

def main():
    """Main function."""
    print(f"🔧 Claude Desktop MCP Configuration Generator")
    print(f"=" * 60)
    
    # Show system information
    print(f"💻 System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📂 Project Directory: {Path(__file__).parent.absolute()}")
    
    # Validate setup
    if not validate_setup():
        print(f"\n❌ Setup validation failed. Please ensure all MCP servers are properly installed.")
        return 1
    
    # Show server information
    show_server_info()
    
    # Ask for confirmation
    if len(sys.argv) > 1 and sys.argv[1] == "--yes":
        confirm = True
    else:
        print(f"\n❓ Generate Claude Desktop configuration? (y/N): ", end="")
        confirm = input().lower().startswith('y')
    
    if not confirm:
        print(f"❌ Configuration generation cancelled.")
        return 0
    
    # Write configuration
    config_path = write_config()
    
    if config_path:
        print(f"\n🎉 Configuration generated successfully!")
        print(f"\n📋 Next Steps:")
        print(f"   1. Restart Claude Desktop application")
        print(f"   2. The MCP servers will be available in Claude Desktop")
        print(f"   3. You can use file operations and network scanning tools")
        
        print(f"\n💡 Usage Tips:")
        print(f"   File Server:")
        print(f"   - Ask Claude to 'read the README.md file'")
        print(f"   - Ask Claude to 'list files in the current directory'")
        print(f"   Network Scanning:")
        print(f"   - Ask Claude to 'ping google.com'")
        print(f"   - Ask Claude to 'scan port 80 on localhost'")
        print(f"   SSH Operations:")
        print(f"   - Ask Claude to 'execute ls -la on server via SSH'")
        print(f"   - Ask Claude to 'copy file via SSH'")
        print(f"   FTP Operations:")
        print(f"   - Ask Claude to 'list files on FTP server'")
        print(f"   - Ask Claude to 'download file from FTP'")
        print(f"   Telnet Testing:")
        print(f"   - Ask Claude to 'test telnet connection to server'")
        print(f"   - Ask Claude to 'grab banner from port 80'")
        
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
