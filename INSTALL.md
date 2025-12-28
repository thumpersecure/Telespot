# 🚀 TeleSpot Quick Install Guide

## Quick Start (3 Steps)

### 1️⃣ Clone or Download
```bash
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
```

### 2️⃣ Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

### 3️⃣ Start Searching
```bash
source telespot-env/bin/activate
./telespot.py 5555551212
```

## What's Included

- **telespot.py** - Main search tool
- **requirements.txt** - Python dependencies (ddgr)
- **setup.sh** - Automated installer
- **README.md** - Full documentation
- **.gitignore** - Git exclusions
- **LICENSE** - MIT License

## First Time Setup

The `setup.sh` script will automatically:
- ✅ Check Python version
- ✅ Create virtual environment (`telespot-env`)
- ✅ Install ddgr dependency
- ✅ Make scripts executable
- ✅ Offer to run TeleSpot

## Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv telespot-env

# Activate it
source telespot-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x telespot.py

# Run it
./telespot.py
```

## Usage Examples

```bash
# Basic usage (prompts for number)
./telespot.py

# Search specific number
./telespot.py 2155551212

# Search with formatted number
./telespot.py "(215) 555-1212"

# Search with country code
./telespot.py 12155551212
```

## Deactivating Virtual Environment

When done:
```bash
deactivate
```

## Getting Help

- 📖 Full docs: See [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/thumpersecure/Telespot/issues)
- ⭐ Star the repo if you find it useful!

---

**Repository**: https://github.com/thumpersecure/Telespot
