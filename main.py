#!/usr/bin/env python3
"""
MCP Tools - Main application to manage and run all FastMCP servers.
This script starts all available MCP servers and provides a simple interface to manage them.
"""

import asyncio
import subprocess
import sys
import time
import signal
import os
from typing import List, Dict, Any, Optional

class MCPServerManager:
    """Manager for running multiple MCP servers."""
    
    def __init__(self):
        self.servers = {}
        self.running = False
        
        # Define server configurations
        self.server_configs = [
            {
                "name": "File Server",
                "script": "servers/file_server.py",
                "port": 8001,
                "description": "Provides file reading and directory listing capabilities"
            },
            {
                "name": "NMAP Server", 
                "script": "servers/nmap_server.py",
                "port": 8002,
                "description": "Provides network scanning and NMAP functionality"
            },
            {
                "name": "SSH Server",
                "script": "servers/ssh_server.py", 
                "port": 8003,
                "description": "Provides SSH remote command execution and file transfer"
            },
            {
                "name": "FTP Server",
                "script": "servers/ftp_server.py",
                "port": 8004,
                "description": "Provides FTP file transfer and server operations"
            },
            {
                "name": "Telnet Server",
                "script": "servers/telnet_server.py",
                "port": 8005,
                "description": "Provides Telnet connectivity testing and basic operations"
            }
        ]
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        missing_deps = []
        
        try:
            import fastmcp
        except ImportError:
            missing_deps.append("fastmcp")
        
        try:
            import uvicorn
        except ImportError:
            missing_deps.append("uvicorn")
        
        # Check if nmap is installed
        try:
            result = subprocess.run(["nmap", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                missing_deps.append("nmap (system package)")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing_deps.append("nmap (system package)")
        
        if missing_deps:
            print("❌ Missing dependencies:")
            for dep in missing_deps:
                print(f"   - {dep}")
            print("\nInstall missing dependencies:")
            print("   pip install -r requirements.txt")
            print("   brew install nmap  # macOS")
            return False
        
        print("✅ All dependencies are installed")
        return True
    
    def start_server(self, config: Dict[str, Any]) -> Optional[subprocess.Popen]:
        """Start a single MCP server."""
        script_path = os.path.join(os.path.dirname(__file__), config["script"])
        
        if not os.path.exists(script_path):
            print(f"❌ Server script not found: {script_path}")
            return None
        
        try:
            print(f"🚀 Starting {config['name']} on port {config['port']}...")
            
            # Use --http flag to run in HTTP mode for manual testing
            process = subprocess.Popen(
                [sys.executable, script_path, "--http"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give the server a moment to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {config['name']} started successfully (PID: {process.pid})")
                return process
            else:
                # Process died, get error output
                _, stderr = process.communicate()
                print(f"❌ {config['name']} failed to start: {stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting {config['name']}: {e}")
            return None
    
    def stop_server(self, name: str, process: subprocess.Popen):
        """Stop a single MCP server."""
        try:
            print(f"🛑 Stopping {name}...")
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                print(f"✅ {name} stopped successfully")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Force killing {name}...")
                process.kill()
                process.wait()
                print(f"✅ {name} force stopped")
                
        except Exception as e:
            print(f"❌ Error stopping {name}: {e}")
    
    def start_all_servers(self):
        """Start all configured servers."""
        print("🔧 MCP Tools - Starting All Servers")
        print("=" * 50)
        
        if not self.check_dependencies():
            return False
        
        print(f"\n📋 Starting {len(self.server_configs)} servers...")
        
        for config in self.server_configs:
            process = self.start_server(config)
            if process:
                self.servers[config["name"]] = {
                    "process": process,
                    "config": config
                }
        
        if not self.servers:
            print("❌ No servers started successfully")
            return False
        
        print(f"\n✅ Started {len(self.servers)}/{len(self.server_configs)} servers successfully")
        self.running = True
        return True
    
    def stop_all_servers(self):
        """Stop all running servers."""
        print("\n🛑 Stopping all servers...")
        
        for name, server_info in self.servers.items():
            self.stop_server(name, server_info["process"])
        
        self.servers.clear()
        self.running = False
        print("✅ All servers stopped")
    
    def show_status(self):
        """Show status of all servers."""
        print("\n📊 Server Status")
        print("=" * 50)
        
        if not self.servers:
            print("No servers running")
            return
        
        for name, server_info in self.servers.items():
            config = server_info["config"]
            process = server_info["process"]
            
            # Check if process is still alive
            if process.poll() is None:
                status = "🟢 Running"
            else:
                status = "🔴 Stopped"
            
            print(f"{status} {name}")
            print(f"   Port: {config['port']}")
            print(f"   Description: {config['description']}")
            print(f"   URL: http://127.0.0.1:{config['port']}")
            print()
    
    def interactive_mode(self):
        """Run in interactive mode with menu."""
        def signal_handler(sig, frame):
            print("\n\n🛑 Received interrupt signal")
            self.stop_all_servers()
            sys.exit(0)
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("\n🎮 Interactive Mode")
        print("Commands:")
        print("  status - Show server status")
        print("  restart - Restart all servers")
        print("  stop - Stop all servers") 
        print("  quit - Exit application")
        print("  help - Show this help")
        
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "status":
                    self.show_status()
                elif command == "restart":
                    self.stop_all_servers()
                    self.start_all_servers()
                elif command == "stop":
                    self.stop_all_servers()
                elif command in ["quit", "exit", "q"]:
                    break
                elif command == "help":
                    print("\nCommands:")
                    print("  status - Show server status")
                    print("  restart - Restart all servers")
                    print("  stop - Stop all servers")
                    print("  quit - Exit application")
                    print("  help - Show this help")
                elif command == "":
                    continue
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user")
                break
        
        self.stop_all_servers()

def main():
    """Main entry point."""
    manager = MCPServerManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            if manager.start_all_servers():
                print("\n🎯 All servers started. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping servers...")
                finally:
                    manager.stop_all_servers()
        
        elif command == "check":
            manager.check_dependencies()
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: start, check")
    
    else:
        # Interactive mode
        if manager.start_all_servers():
            manager.show_status()
            manager.interactive_mode()

if __name__ == "__main__":
    main()
