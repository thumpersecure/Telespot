# telespot Quick Install Guide

## Fastest Method (One Command)

```bash
curl -sSL https://raw.githubusercontent.com/thumpersecure/Telespot/main/just-do-it.sh | bash
```

Or with wget:
```bash
wget -qO- https://raw.githubusercontent.com/thumpersecure/Telespot/main/just-do-it.sh | bash
```

This will:
1. Check for Python 3 and pip
2. Clone the repository
3. Install dependencies
4. Set up configuration
5. Create a convenient `telespot` command

---

## Manual Installation

### Step 1: Requirements

- Python 3.7 or higher
- pip (Python package manager)
- git (optional, for easy updates)

**Check Python version:**
```bash
python3 --version
```

### Step 2: Get the Code

**Option A: Clone with Git (recommended)**
```bash
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
```

**Option B: Download ZIP**
1. Go to https://github.com/thumpersecure/Telespot
2. Click "Code" → "Download ZIP"
3. Extract and navigate to folder

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests beautifulsoup4 lxml
```

### Step 4: Run telespot

```bash
python3 telespot.py --help
```

---

## Platform-Specific Instructions

### Ubuntu/Debian Linux

```bash
# Install Python if needed
sudo apt update
sudo apt install python3 python3-pip git

# Clone and install
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
pip3 install -r requirements.txt

# Run
python3 telespot.py 2155551234
```

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3 git

# Clone and install
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
pip3 install -r requirements.txt

# Run
python3 telespot.py 2155551234
```

### Windows

1. Install Python from https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

2. Open Command Prompt or PowerShell:
```cmd
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
pip install -r requirements.txt
python telespot.py --help
```

### Termux (Android)

```bash
pkg update
pkg install python git
pip install requests beautifulsoup4 lxml

git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
python telespot.py 2155551234
```

---

## Quick Start Examples

```bash
# Basic search
python3 telespot.py 2155551234

# With keyword
python3 telespot.py 2155551234 -k "owner"

# Verbose with JSON output
python3 telespot.py 2155551234 -v -o results.json

# International number
python3 telespot.py +442071234567 -c +44

# Interactive mode
python3 telespot.py
```

---

## Optional: Configure APIs

For enhanced lookups, configure API keys:

```bash
python3 telespot.py --setup
```

See [GUIDE_APIS.md](GUIDE_APIS.md) for details.

---

## Updating

**If installed with git:**
```bash
cd Telespot
git pull
```

**Or use built-in update:**
```bash
python3 telespot.py --update
```

---

## Troubleshooting

**"python3: command not found"**
- Try `python` instead of `python3`
- Or install Python 3

**"pip: command not found"**
- Try `pip3` instead of `pip`
- Or: `python3 -m pip install -r requirements.txt`

**"No module named 'bs4'"**
```bash
pip install beautifulsoup4
```

**Permission denied**
```bash
pip install --user -r requirements.txt
```

---

## Need Help?

```bash
python3 telespot.py --help
```

Or open an issue: https://github.com/thumpersecure/Telespot/issues
