#!/usr/bin/env python3
"""
AI Council PyPI Publishing Script
=================================

This script helps publish AI Council to PyPI (Python Package Index).
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    else:
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True

def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    required_tools = ['python', 'pip']
    for tool in required_tools:
        if not run_command(f"which {tool}", f"Checking {tool}"):
            print(f"❌ {tool} is not installed or not in PATH")
            return False
    
    # Check if build and twine are installed
    try:
        import build
        import twine
        print("✅ Build tools are available")
        return True
    except ImportError:
        print("📦 Installing required build tools...")
        return run_command("pip install build twine", "Installing build tools")

def validate_package():
    """Validate the package configuration."""
    print("\n🔍 Validating package configuration...")
    
    # Check required files exist
    required_files = ['pyproject.toml', 'README.md', 'LICENSE', 'ai_council/__init__.py']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file missing: {file}")
            return False
    
    print("✅ All required files present")
    
    # Run tests
    if not run_command("python -m pytest tests/ -v", "Running tests"):
        print("❌ Tests failed. Fix tests before publishing.")
        return False
    
    return True

def build_package():
    """Build the package."""
    print("\n🏗️ Building package...")
    
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info", "Cleaning previous builds")
    
    # Build the package
    return run_command("python -m build", "Building package")

def upload_to_pypi(test=True):
    """Upload package to PyPI."""
    repository = "testpypi" if test else "pypi"
    description = f"Uploading to {'Test PyPI' if test else 'PyPI'}"
    
    print(f"\n🚀 {description}...")
    
    if test:
        cmd = "python -m twine upload --repository testpypi dist/*"
    else:
        cmd = "python -m twine upload dist/*"
    
    return run_command(cmd, description)

def main():
    """Main publishing workflow."""
    print("🚀 AI Council PyPI Publishing Script")
    print("=" * 50)
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"📁 Working directory: {project_root}")
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed")
        sys.exit(1)
    
    # Step 2: Validate package
    if not validate_package():
        print("❌ Package validation failed")
        sys.exit(1)
    
    # Step 3: Build package
    if not build_package():
        print("❌ Package build failed")
        sys.exit(1)
    
    # Step 4: Ask user about upload
    print("\n📦 Package built successfully!")
    print("Choose upload option:")
    print("1. Upload to Test PyPI (recommended first)")
    print("2. Upload to Production PyPI")
    print("3. Skip upload")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🧪 Uploading to Test PyPI...")
        print("You'll need Test PyPI credentials.")
        print("Create account at: https://test.pypi.org/account/register/")
        if upload_to_pypi(test=True):
            print("\n✅ Successfully uploaded to Test PyPI!")
            print("Test installation with:")
            print("pip install --index-url https://test.pypi.org/simple/ ai-council")
    
    elif choice == "2":
        print("\n🚀 Uploading to Production PyPI...")
        print("You'll need PyPI credentials.")
        print("Create account at: https://pypi.org/account/register/")
        confirm = input("Are you sure you want to upload to production PyPI? (yes/no): ")
        if confirm.lower() == "yes":
            if upload_to_pypi(test=False):
                print("\n🎉 Successfully published to PyPI!")
                print("Install with: pip install ai-council")
        else:
            print("❌ Upload cancelled")
    
    else:
        print("⏭️ Skipping upload")
    
    print("\n🎉 Publishing process completed!")

if __name__ == "__main__":
    main()