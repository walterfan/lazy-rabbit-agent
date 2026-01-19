#!/usr/bin/env python3
"""
Environment Setup Script
Generates .env file from .env.example with secure SECRET_KEY
Usage: python scripts/setup-env.py
"""

import os
import secrets
import shutil
import sys
from pathlib import Path


def generate_secret_key(length: int = 32) -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(length)


def setup_env():
    """Setup .env file from .env.example."""
    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_example_path = project_root / ".env.example"
    env_path = project_root / ".env"

    print("🔧 Environment Setup Script")
    print("=" * 40)
    print()

    # Check if .env already exists
    if env_path.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response not in ("y", "yes"):
            print("❌ Setup cancelled.")
            return False

    # Check if .env.example exists
    if not env_example_path.exists():
        print("❌ Error: .env.example file not found!")
        print(f"Expected location: {env_example_path}")
        return False

    # Generate secure SECRET_KEY
    print("🔐 Generating secure SECRET_KEY...")
    secret_key = generate_secret_key(32)
    print(f"✓ Generated SECRET_KEY: {secret_key[:10]}...")
    print()

    # Read .env.example content
    with open(env_example_path, "r") as f:
        content = f.read()

    # Replace placeholder SECRET_KEY with generated one
    content = content.replace(
        "SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars",
        f"SECRET_KEY={secret_key}",
    )

    # Write to .env
    print("📝 Creating .env file...")
    with open(env_path, "w") as f:
        f.write(content)

    print("✓ .env file created successfully!")
    print()
    print("📋 Summary:")
    print("  - SECRET_KEY: Generated (32 bytes, URL-safe)")
    print("  - Database: SQLite (./app.db)")
    print("  - CORS Origins: localhost:5173, localhost:3000")
    print()
    print("⚠️  Important:")
    print("  1. Review .env file and adjust settings if needed")
    print("  2. Never commit .env file to version control")
    print("  3. For production, update CORS origins and database URL")
    print()
    print("✅ Environment setup complete!")
    print()
    print("Next steps:")
    print("  make install    # Install dependencies")
    print("  make migrate    # Run database migrations")
    print("  make run        # Start servers")
    
    return True


def main():
    """Main entry point."""
    try:
        success = setup_env()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

