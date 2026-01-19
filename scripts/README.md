# Scripts Directory

This directory contains utility scripts for project setup and maintenance.

## Available Scripts

### 1. `setup-env.sh` (Bash Script)

Generates `.env` file from `.env.example` with a secure SECRET_KEY.

**Usage:**
```bash
./scripts/setup-env.sh
```

**Features:**
- Automatically generates secure 32-byte URL-safe SECRET_KEY
- Checks if .env already exists and prompts before overwriting
- Works on macOS and Linux
- Validates Python availability

**Requirements:**
- Bash shell
- Python 3 (for generating SECRET_KEY)

---

### 2. `setup-env.py` (Python Script)

Python version of the environment setup script with the same functionality.

**Usage:**
```bash
python3 scripts/setup-env.py
```

**Features:**
- Cross-platform (works on Windows, macOS, Linux)
- Pure Python implementation
- Generates secure SECRET_KEY using Python's `secrets` module
- Interactive prompts for safety

**Requirements:**
- Python 3.6+

---

## Quick Reference

### Generate .env (Easiest Way)
```bash
# From project root
make setup
```

This automatically runs the appropriate script for your system.

### First-Time Project Setup
```bash
# Complete setup in one command
make first-time-setup
```

This runs:
1. `make setup` - Generates .env
2. `make install` - Installs dependencies
3. `make migrate` - Creates database

---

## Manual SECRET_KEY Generation

If you prefer to manually create the SECRET_KEY:

```bash
# Generate a secure random key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then manually add it to your `.env` file:
```bash
SECRET_KEY=your-generated-key-here
```

---

## Troubleshooting

### Script Permission Denied
```bash
chmod +x scripts/setup-env.sh scripts/setup-env.py
```

### Python Not Found
Ensure Python 3 is installed:
```bash
python3 --version
```

If not installed, download from [python.org](https://python.org) or use your system's package manager:
- **macOS**: `brew install python3`
- **Ubuntu/Debian**: `sudo apt install python3`
- **Windows**: Download from python.org

### .env Already Exists
Both scripts will prompt before overwriting. Choose:
- `y` or `yes` - Overwrite existing .env
- `n` or `no` - Keep existing .env

---

## Security Notes

⚠️ **Important:**
1. Never commit `.env` files to version control
2. Use different SECRET_KEY values for development and production
3. Store production secrets in secure secret management systems
4. Rotate SECRET_KEY periodically in production

The `.gitignore` file is already configured to exclude `.env` files.

