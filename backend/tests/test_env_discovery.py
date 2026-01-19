#!/usr/bin/env python3
"""
Test script to verify .env file discovery logic.

This script demonstrates how the backend searches for .env files
in multiple locations.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import find_env_file, ENV_FILE

print("=" * 60)
print("Testing .env File Discovery")
print("=" * 60)

print("\n📁 Search Strategy:")
print("  1. Current working directory")
print("  2. Parent directory")
print("  3. Backend directory (where config.py is)")
print("  4. Project root (parent of backend)")

print("\n🔍 Current Working Directory:")
print(f"  {Path.cwd()}")

print("\n🔍 Searching for .env file...")
env_path = find_env_file()

if env_path:
    print(f"\n✅ .env file found:")
    print(f"  Location: {env_path}")
    print(f"  Exists: {Path(env_path).exists()}")
    print(f"  Size: {Path(env_path).stat().st_size} bytes")
    
    # Show first few non-secret lines
    print(f"\n📄 Sample configuration (non-secret keys):")
    with open(env_path) as f:
        count = 0
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Only show non-secret keys
                if any(key in line.upper() for key in ['URL', 'PORT', 'PROVIDER', 'TIMEZONE']):
                    print(f"  {line}")
                    count += 1
                    if count >= 5:
                        break
else:
    print("\n❌ .env file not found")
    print("  Backend will use default configuration")

print(f"\n⚙️  Settings will load from:")
print(f"  {ENV_FILE}")

print("\n✅ Test complete!")
print("=" * 60)


