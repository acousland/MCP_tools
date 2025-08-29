#!/usr/bin/env python3
"""
File Server - MCP server for reading files from the local machine.
Provides tools to read file contents and list directory contents.
"""

import asyncio
import os
import pathlib
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("File Server")

@mcp.tool()
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read the contents of a file from the local filesystem.
    
    Args:
        file_path: Absolute or relative path to the file to read
        encoding: Text encoding to use (default: utf-8)
    
    Returns:
        The contents of the file as a string
    """
    try:
        # Convert to absolute path for security
        abs_path = os.path.abspath(file_path)
        
        # Check if file exists
        if not os.path.exists(abs_path):
            return f"Error: File '{file_path}' does not exist"
        
        # Check if it's actually a file (not a directory)
        if not os.path.isfile(abs_path):
            return f"Error: '{file_path}' is not a file"
        
        # Read the file
        with open(abs_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return content
        
    except PermissionError:
        return f"Error: Permission denied reading file '{file_path}'"
    except UnicodeDecodeError as e:
        return f"Error: Unicode decode error reading file '{file_path}': {e}"
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"

@mcp.tool()
def list_directory(dir_path: str, show_hidden: bool = False) -> str:
    """
    List the contents of a directory.
    
    Args:
        dir_path: Path to the directory to list
        show_hidden: Whether to show hidden files (starting with .)
    
    Returns:
        A formatted string listing the directory contents
    """
    try:
        # Convert to absolute path
        abs_path = os.path.abspath(dir_path)
        
        # Check if directory exists
        if not os.path.exists(abs_path):
            return f"Error: Directory '{dir_path}' does not exist"
        
        # Check if it's actually a directory
        if not os.path.isdir(abs_path):
            return f"Error: '{dir_path}' is not a directory"
        
        # Get directory contents
        items = os.listdir(abs_path)
        
        # Filter hidden files if requested
        if not show_hidden:
            items = [item for item in items if not item.startswith('.')]
        
        # Sort items
        items.sort()
        
        # Create formatted output
        result = f"Contents of '{abs_path}':\n"
        result += f"{'='*50}\n"
        
        if not items:
            result += "Directory is empty\n"
        else:
            for item in items:
                item_path = os.path.join(abs_path, item)
                if os.path.isdir(item_path):
                    result += f"📁 {item}/\n"
                else:
                    # Get file size
                    try:
                        size = os.path.getsize(item_path)
                        if size < 1024:
                            size_str = f"{size}B"
                        elif size < 1024*1024:
                            size_str = f"{size/1024:.1f}KB"
                        else:
                            size_str = f"{size/(1024*1024):.1f}MB"
                        result += f"📄 {item} ({size_str})\n"
                    except:
                        result += f"📄 {item}\n"
        
        return result
        
    except PermissionError:
        return f"Error: Permission denied accessing directory '{dir_path}'"
    except Exception as e:
        return f"Error listing directory '{dir_path}': {e}"

@mcp.tool()
def get_file_info(file_path: str) -> str:
    """
    Get information about a file or directory.
    
    Args:
        file_path: Path to the file or directory
    
    Returns:
        Information about the file/directory
    """
    try:
        abs_path = os.path.abspath(file_path)
        
        if not os.path.exists(abs_path):
            return f"Error: Path '{file_path}' does not exist"
        
        stat_info = os.stat(abs_path)
        path_obj = pathlib.Path(abs_path)
        
        result = f"Information for '{abs_path}':\n"
        result += f"{'='*50}\n"
        result += f"Type: {'Directory' if path_obj.is_dir() else 'File'}\n"
        result += f"Size: {stat_info.st_size} bytes\n"
        result += f"Permissions: {oct(stat_info.st_mode)[-3:]}\n"
        result += f"Owner: {stat_info.st_uid}\n"
        result += f"Group: {stat_info.st_gid}\n"
        result += f"Modified: {stat_info.st_mtime}\n"
        result += f"Accessed: {stat_info.st_atime}\n"
        result += f"Created: {stat_info.st_ctime}\n"
        
        if path_obj.is_file():
            result += f"Extension: {path_obj.suffix}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting file info for '{file_path}': {e}"

if __name__ == "__main__":
    import sys
    
    # Check if we should run in HTTP mode (for testing) or stdio mode (for Claude Desktop)
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        # HTTP mode for testing
        import asyncio
        
        async def run_server():
            await mcp.run_http_async(host="127.0.0.1", port=8001)
        
        print("🚀 Starting File Server in HTTP mode on http://127.0.0.1:8001")
        print("Use --http flag to run in HTTP mode, otherwise runs in stdio mode for Claude Desktop")
        asyncio.run(run_server())
    else:
        # Stdio mode for Claude Desktop
        mcp.run()
