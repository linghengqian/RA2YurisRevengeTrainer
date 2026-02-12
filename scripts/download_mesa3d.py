#!/usr/bin/env python3
"""
Download Mesa3D OpenGL software renderer for Windows.
This provides a software fallback for environments without hardware OpenGL support
(e.g., RDP, Hyper-V Enhanced Session Mode).
"""

import os
import sys
import urllib.request
import subprocess
from pathlib import Path

# Mesa3D distribution for Windows
# Using a stable release from pal1000/mesa-dist-win
MESA_VERSION = "25.3.5"
MESA_URL = f"https://github.com/pal1000/mesa-dist-win/releases/download/{MESA_VERSION}/mesa3d-{MESA_VERSION}-release-msvc.7z"

def download_file(url: str, dest: Path) -> None:
    """Download a file from a URL to the destination path."""
    print(f"Downloading {url}...")
    with urllib.request.urlopen(url) as response:
        with open(dest, 'wb') as out_file:
            out_file.write(response.read())
    print(f"Downloaded to {dest}")

def extract_opengl_dll_7z(archive_path: Path, output_dir: Path) -> None:
    """Extract opengl32.dll from the Mesa3D 7z archive."""
    print(f"Extracting opengl32.dll from {archive_path}...")
    
    # Try to extract using 7z command if available
    try:
        # Extract to a temporary directory first
        temp_extract_dir = output_dir / "temp_extract"
        temp_extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Try 7z command
        subprocess.run(['7z', 'x', str(archive_path), '-o' + str(temp_extract_dir), 'x86/opengl32.dll', '-y'],
                      check=True, capture_output=True)
        
        # Move the extracted file
        extracted_dll = temp_extract_dir / "x86" / "opengl32.dll"
        final_dll = output_dir / "opengl32.dll"
        
        if extracted_dll.exists():
            extracted_dll.rename(final_dll)
            print(f"Extracted to {final_dll}")
        
        # Clean up
        import shutil
        shutil.rmtree(temp_extract_dir)
        
    except FileNotFoundError:
        print("Error: 7z command not found.")
        print("\nPlease install 7-Zip and ensure it's in your PATH, or:")
        print(f"1. Download {MESA_URL}")
        print(f"2. Extract x86/opengl32.dll manually to {output_dir / 'opengl32.dll'}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error extracting with 7z: {e}")
        print("Please extract x86/opengl32.dll manually from the archive.")
        sys.exit(1)

def main():
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    deps_dir = project_dir / "deps" / "mesa3d"
    
    # Create deps directory if it doesn't exist
    deps_dir.mkdir(parents=True, exist_ok=True)
    
    archive_file = deps_dir / f"mesa3d-{MESA_VERSION}.7z"
    
    # Download if not already downloaded
    if not archive_file.exists():
        try:
            download_file(MESA_URL, archive_file)
        except Exception as e:
            print(f"Error downloading Mesa3D: {e}")
            print("\nPlease download manually from:")
            print(f"  {MESA_URL}")
            print(f"And place it at: {archive_file}")
            sys.exit(1)
    else:
        print(f"Using cached {archive_file}")
    
    # Extract opengl32.dll
    try:
        extract_opengl_dll_7z(archive_file, deps_dir)
        print(f"\nMesa3D OpenGL software renderer ready at: {deps_dir / 'opengl32.dll'}")
        print("This will be copied to the build output directory during compilation.")
    except Exception as e:
        print(f"Error extracting Mesa3D: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
