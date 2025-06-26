#!/usr/bin/env python3
"""
Test script to simulate the GitHub Actions release workflow locally.

This script helps you test the version bumping process before creating a GitHub release.

Usage:
    python3 scripts/test_release_workflow.py <version>
    
Example:
    python3 scripts/test_release_workflow.py 0.0.4
"""

import re
import sys
import shutil
import zipfile
from pathlib import Path


def update_pyproject_toml(version: str) -> None:
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        return
    
    content = pyproject_path.read_text()
    
    # Update version line
    pattern = r'^version = ".*"'
    replacement = f'version = "{version}"'
    
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if new_content != content:
        pyproject_path.write_text(new_content)
        print(f"✓ Updated pyproject.toml version to {version}")
    else:
        print("⚠ No changes made to pyproject.toml")


def update_manifest_json(version: str) -> None:
    """Update version in manifest.json"""
    manifest_path = Path("custom_components/satcom_forecast/manifest.json")
    
    if not manifest_path.exists():
        print("Error: manifest.json not found")
        return
    
    content = manifest_path.read_text()
    
    # Update version line
    pattern = r'"version": ".*"'
    replacement = f'"version": "{version}"'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        manifest_path.write_text(new_content)
        print(f"✓ Updated manifest.json version to {version}")
    else:
        print("⚠ No changes made to manifest.json")


def create_release_assets(version: str) -> None:
    """Create release assets with the updated version"""
    # Create a temporary directory for the release files
    temp_dir = Path("temp_release")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # Copy necessary files
    files_to_copy = [
        "custom_components",
        "pyproject.toml", 
        "README.md",
        "LICENSE"
    ]
    
    for item in files_to_copy:
        src = Path(item)
        dst = temp_dir / item
        if src.is_file():
            shutil.copy2(src, dst)
        elif src.is_dir():
            shutil.copytree(src, dst)
    
    # Create zip file
    zip_filename = f"satcom-forecast-{version}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in temp_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    print(f"✓ Created release asset: {zip_filename}")


def verify_changes(version: str) -> None:
    """Verify that the changes were applied correctly"""
    print("\n=== Verification ===")
    
    # Check pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
        if match and match.group(1) == version:
            print(f"✓ pyproject.toml version: {match.group(1)}")
        else:
            print(f"✗ pyproject.toml version mismatch: expected {version}")
    
    # Check manifest.json
    manifest_path = Path("custom_components/satcom_forecast/manifest.json")
    if manifest_path.exists():
        content = manifest_path.read_text()
        match = re.search(r'"version": "([^"]+)"', content)
        if match and match.group(1) == version:
            print(f"✓ manifest.json version: {match.group(1)}")
        else:
            print(f"✗ manifest.json version mismatch: expected {version}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    
    new_version = sys.argv[1]
    
    # Validate version format (basic check)
    if not re.match(r'^\d+\.\d+\.\d+', new_version):
        print("Error: Version should be in format X.Y.Z (e.g., 0.0.4)")
        sys.exit(1)
    
    print(f"Testing release workflow for version {new_version}...")
    print("=" * 50)
    
    # Simulate the workflow steps
    print("1. Updating version files...")
    update_pyproject_toml(new_version)
    update_manifest_json(new_version)
    
    print("\n2. Creating release assets...")
    create_release_assets(new_version)
    
    print("\n3. Verifying changes...")
    verify_changes(new_version)
    
    print("\n" + "=" * 50)
    print("✓ Release workflow simulation complete!")
    print(f"\nNext steps:")
    print(f"1. Review the changes above")
    print(f"2. Create a GitHub release with tag: v{new_version}")
    print(f"3. The GitHub Actions workflow will handle the rest automatically")
    print(f"\nTo revert changes, run: python3 scripts/bump_version.py <previous_version>")


if __name__ == "__main__":
    main() 