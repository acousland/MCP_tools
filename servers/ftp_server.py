#!/usr/bin/env python3
"""
FTP Server - MCP server for FTP file transfer operations.
Provides tools to connect to FTP servers and transfer files.
"""

import subprocess
import os
import tempfile
import ftplib
import socket
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("FTP Server")

def _connect_ftp(host: str, username: str = "anonymous", password: str = "", 
                port: int = 21, timeout: int = 30, passive: bool = True) -> Dict[str, Any]:
    """
    Create FTP connection and return connection object or error.
    
    Args:
        host: FTP server hostname or IP
        username: FTP username
        password: FTP password
        port: FTP port (default: 21)
        timeout: Connection timeout
        passive: Use passive mode
    
    Returns:
        Dictionary with connection result
    """
    try:
        # Create FTP connection
        ftp = ftplib.FTP()
        ftp.connect(host, port, timeout)
        
        # Set passive mode
        ftp.set_pasv(passive)
        
        # Login
        ftp.login(username, password)
        
        return {
            "success": True,
            "ftp": ftp,
            "welcome": ftp.getwelcome()
        }
        
    except ftplib.all_errors as e:
        return {
            "success": False,
            "error": f"FTP connection failed: {e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection error: {e}"
        }

@mcp.tool()
def ftp_list_files(host: str, directory: str = "/", username: str = "anonymous", 
                   password: str = "", port: int = 21, timeout: int = 30) -> str:
    """
    List files and directories on an FTP server.
    
    Args:
        host: FTP server hostname or IP address
        directory: Directory to list (default: root)
        username: FTP username (default: anonymous)
        password: FTP password (default: empty for anonymous)
        port: FTP port (default: 21)
        timeout: Connection timeout in seconds
    
    Returns:
        Directory listing from FTP server
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    # Connect to FTP server
    conn_result = _connect_ftp(host, username, password, port, timeout)
    
    if not conn_result["success"]:
        return f"Error: {conn_result['error']}"
    
    ftp = conn_result["ftp"]
    
    try:
        # Change to specified directory
        if directory != "/":
            ftp.cwd(directory)
        
        # Get directory listing
        files = []
        ftp.retrlines('LIST', files.append)
        
        # Format output
        output = f"FTP Directory Listing\n"
        output += f"{'='*40}\n"
        output += f"Server: {host}:{port}\n"
        output += f"Directory: {ftp.pwd()}\n"
        output += f"User: {username}\n"
        output += f"Welcome: {conn_result['welcome']}\n"
        output += f"{'='*40}\n"
        
        if files:
            for file_info in files:
                output += f"{file_info}\n"
        else:
            output += "Directory is empty\n"
        
        ftp.quit()
        return output
        
    except ftplib.all_errors as e:
        try:
            ftp.quit()
        except:
            pass
        return f"Error listing directory: {e}"
    except Exception as e:
        try:
            ftp.quit()
        except:
            pass
        return f"Error: {e}"

@mcp.tool()
def ftp_download_file(host: str, remote_file: str, local_file: str = None, 
                      username: str = "anonymous", password: str = "", 
                      port: int = 21, timeout: int = 30) -> str:
    """
    Download a file from an FTP server.
    
    Args:
        host: FTP server hostname or IP address
        remote_file: Path to file on FTP server
        local_file: Local path to save file (optional, uses remote filename)
        username: FTP username
        password: FTP password
        port: FTP port (default: 21)
        timeout: Connection timeout in seconds
    
    Returns:
        File download result
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not remote_file:
        return "Error: Remote file path required"
    
    # Set local filename if not specified
    if not local_file:
        local_file = os.path.basename(remote_file)
        if not local_file:
            local_file = "downloaded_file"
    
    # Connect to FTP server
    conn_result = _connect_ftp(host, username, password, port, timeout)
    
    if not conn_result["success"]:
        return f"Error: {conn_result['error']}"
    
    ftp = conn_result["ftp"]
    
    try:
        # Get file size for progress info
        try:
            size = ftp.size(remote_file)
            size_info = f" ({size} bytes)" if size else ""
        except:
            size_info = ""
        
        # Download file
        with open(local_file, 'wb') as f:
            ftp.retrbinary(f'RETR {remote_file}', f.write)
        
        # Verify download
        local_size = os.path.getsize(local_file)
        
        # Format output
        output = f"FTP File Download\n"
        output += f"{'='*30}\n"
        output += f"Server: {host}:{port}\n"
        output += f"Remote file: {remote_file}{size_info}\n"
        output += f"Local file: {local_file}\n"
        output += f"Downloaded: {local_size} bytes\n"
        output += f"Status: ✅ Download completed successfully\n"
        
        ftp.quit()
        return output
        
    except ftplib.all_errors as e:
        try:
            ftp.quit()
        except:
            pass
        # Clean up partially downloaded file
        if os.path.exists(local_file):
            try:
                os.remove(local_file)
            except:
                pass
        return f"Error downloading file: {e}"
    except Exception as e:
        try:
            ftp.quit()
        except:
            pass
        return f"Error: {e}"

@mcp.tool()
def ftp_upload_file(host: str, local_file: str, remote_file: str = None, 
                    username: str = "anonymous", password: str = "", 
                    port: int = 21, timeout: int = 30) -> str:
    """
    Upload a file to an FTP server.
    
    Args:
        host: FTP server hostname or IP address
        local_file: Local file to upload
        remote_file: Remote path to save file (optional, uses local filename)
        username: FTP username
        password: FTP password
        port: FTP port (default: 21)
        timeout: Connection timeout in seconds
    
    Returns:
        File upload result
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    if not os.path.exists(local_file):
        return f"Error: Local file not found: {local_file}"
    
    # Set remote filename if not specified
    if not remote_file:
        remote_file = os.path.basename(local_file)
    
    # Connect to FTP server
    conn_result = _connect_ftp(host, username, password, port, timeout)
    
    if not conn_result["success"]:
        return f"Error: {conn_result['error']}"
    
    ftp = conn_result["ftp"]
    
    try:
        # Get local file size
        local_size = os.path.getsize(local_file)
        
        # Upload file
        with open(local_file, 'rb') as f:
            ftp.storbinary(f'STOR {remote_file}', f)
        
        # Verify upload by checking remote file size
        try:
            remote_size = ftp.size(remote_file)
            verify_info = f"Remote size: {remote_size} bytes" if remote_size else "Size verification not supported"
        except:
            verify_info = "Size verification not supported"
        
        # Format output
        output = f"FTP File Upload\n"
        output += f"{'='*30}\n"
        output += f"Server: {host}:{port}\n"
        output += f"Local file: {local_file}\n"
        output += f"Remote file: {remote_file}\n"
        output += f"Uploaded: {local_size} bytes\n"
        output += f"{verify_info}\n"
        output += f"Status: ✅ Upload completed successfully\n"
        
        ftp.quit()
        return output
        
    except ftplib.all_errors as e:
        try:
            ftp.quit()
        except:
            pass
        return f"Error uploading file: {e}"
    except Exception as e:
        try:
            ftp.quit()
        except:
            pass
        return f"Error: {e}"

@mcp.tool()
def ftp_server_info(host: str, username: str = "anonymous", password: str = "", 
                    port: int = 21, timeout: int = 30) -> str:
    """
    Get information about an FTP server.
    
    Args:
        host: FTP server hostname or IP address
        username: FTP username
        password: FTP password
        port: FTP port (default: 21)
        timeout: Connection timeout in seconds
    
    Returns:
        FTP server information
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    # Connect to FTP server
    conn_result = _connect_ftp(host, username, password, port, timeout)
    
    if not conn_result["success"]:
        return f"Error: {conn_result['error']}"
    
    ftp = conn_result["ftp"]
    
    try:
        # Get server information
        output = f"FTP Server Information\n"
        output += f"{'='*35}\n"
        output += f"Server: {host}:{port}\n"
        output += f"User: {username}\n"
        output += f"Welcome Message: {conn_result['welcome']}\n"
        
        # Get current directory
        try:
            pwd = ftp.pwd()
            output += f"Current Directory: {pwd}\n"
        except:
            output += f"Current Directory: Unable to determine\n"
        
        # Get system type
        try:
            syst = ftp.getwelcome()  # Some servers include system info in welcome
            output += f"System Type: {ftp.sendcmd('SYST')}\n"
        except:
            output += f"System Type: Unable to determine\n"
        
        # Test features
        try:
            features = ftp.sendcmd('FEAT')
            output += f"Features:\n{features}\n"
        except:
            output += f"Features: Not supported or unable to retrieve\n"
        
        # Get status
        try:
            status = ftp.sendcmd('STAT')
            output += f"Status: {status[:100]}...\n" if len(status) > 100 else f"Status: {status}\n"
        except:
            output += f"Status: Unable to retrieve\n"
        
        ftp.quit()
        return output
        
    except Exception as e:
        try:
            ftp.quit()
        except:
            pass
        return f"Error getting server info: {e}"

@mcp.tool()
def ftp_test_connection(host: str, username: str = "anonymous", password: str = "", 
                       port: int = 21, timeout: int = 10) -> str:
    """
    Test FTP connection to a server.
    
    Args:
        host: FTP server hostname or IP address
        username: FTP username
        password: FTP password
        port: FTP port (default: 21)
        timeout: Connection timeout in seconds
    
    Returns:
        Connection test result
    """
    # Basic validation
    if not host or len(host) > 100:
        return "Error: Invalid host specified"
    
    # Test connection
    conn_result = _connect_ftp(host, username, password, port, timeout)
    
    output = f"FTP Connection Test\n"
    output += f"{'='*30}\n"
    output += f"Server: {host}:{port}\n"
    output += f"Username: {username}\n"
    output += f"Timeout: {timeout}s\n"
    output += f"{'='*30}\n"
    
    if conn_result["success"]:
        ftp = conn_result["ftp"]
        output += f"✅ Connection successful\n"
        output += f"Welcome: {conn_result['welcome']}\n"
        
        try:
            ftp.quit()
        except:
            pass
    else:
        output += f"❌ Connection failed\n"
        output += f"Error: {conn_result['error']}\n"
    
    return output

if __name__ == "__main__":
    import sys
    
    # Check if we should run in HTTP mode (for testing) or stdio mode (for Claude Desktop)
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # HTTP mode for testing
        import asyncio
        
        async def run_server():
            await mcp.run_http_async(host="127.0.0.1", port=8004)
        
        print("🚀 Starting FTP Server in HTTP mode on http://127.0.0.1:8004")
        print("Use --http flag to run in HTTP mode, otherwise runs in stdio mode for Claude Desktop")
        asyncio.run(run_server())
    else:
        # Stdio mode for Claude Desktop
        mcp.run()
