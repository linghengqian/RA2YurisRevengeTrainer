#!/usr/bin/env python3
import os
import sys
import urllib.request
import subprocess
from pathlib import Path

MESA_VERSION = "25.3.5"
MESA_URL = f"https://github.com/pal1000/mesa-dist-win/releases/download/{MESA_VERSION}/mesa3d-{MESA_VERSION}-release-msvc.7z"

def download_file(url: str, dest: Path) -> None:
    print(f"Downloading {url}...")
    with urllib.request.urlopen(url) as response:
        with open(dest, 'wb') as out_file:
            out_file.write(response.read())
    print(f"Downloaded to {dest}")

def extract_opengl_dll_7z(archive_path: Path, output_dir: Path) -> None:
    print(f"Extracting opengl32.dll from {archive_path}...")
    try:
        temp_extract_dir = output_dir / "temp_extract"
        temp_extract_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(['7z', 'x', str(archive_path), '-o' + str(temp_extract_dir), 'x86/opengl32.dll', '-y'],
                      check=True, capture_output=True)
        extracted_dll = temp_extract_dir / "x86" / "opengl32.dll"
        final_dll = output_dir / "opengl32.dll"
        if extracted_dll.exists():
            extracted_dll.rename(final_dll)
            print(f"Extracted to {final_dll}")
        import shutil
        shutil.rmtree(temp_extract_dir)
    except FileNotFoundError:
        print("Error: 7z command not found.")
        print("\nTo install 7-Zip, run:")
        print("  winget install --source winget --exact 7zip.7zip")
        print("\nOr manually:")
        print(f"1. Download {MESA_URL}")
        print(f"2. Extract x86/opengl32.dll manually to {output_dir / 'opengl32.dll'}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error extracting with 7z: {e}")
        print("Please extract x86/opengl32.dll manually from the archive.")
        sys.exit(1)

def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    deps_dir = project_dir / "deps" / "mesa3d"
    deps_dir.mkdir(parents=True, exist_ok=True)
    archive_file = deps_dir / f"mesa3d-{MESA_VERSION}.7z"
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
    try:
        extract_opengl_dll_7z(archive_file, deps_dir)
        print(f"\nMesa3D OpenGL software renderer ready at: {deps_dir / 'opengl32.dll'}")
        print("This will be copied to the build output directory during compilation.")
    except Exception as e:
        print(f"Error extracting Mesa3D: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
