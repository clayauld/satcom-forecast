#!/usr/bin/env python3
"""
Version bump script for satcom-forecast

Usage:
    python scripts/bump_version.py <new_version>

Example:
    python scripts/bump_version.py 0.0.4
"""

import re
import sys
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


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    new_version = sys.argv[1]

    # Validate version format (basic check)
    if not re.match(r"^\d+\.\d+\.\d+", new_version):
        print("Error: Version should be in format X.Y.Z (e.g., 0.0.4)")
        sys.exit(1)

    print(f"Bumping version to {new_version}...")

    update_pyproject_toml(new_version)
    update_manifest_json(new_version)

    print("\nVersion bump complete!")


if __name__ == "__main__":
    main()
