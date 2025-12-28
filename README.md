# 📞 TeleSpot 🔍

```
████████╗███████╗██╗     ███████╗███████╗██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     █████╗  ███████╗██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██╔═══╝ ██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗███████║██║     ╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝    ╚═╝   
                                                         version 1.0
```

[![GitHub](https://img.shields.io/badge/GitHub-thumpersecure/Telespot-blue?logo=github)](https://github.com/thumpersecure/Telespot)
[![Python](https://img.shields.io/badge/Python-3.6+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/thumpersecure/Telespot/blob/main/LICENSE)

A Python script that searches DuckDuckGo for phone numbers using multiple format variations and analyzes patterns in the results.

## ✨ Features

- **Multiple Format Searching**: Automatically generates 8 different phone number format variations
- **Pattern Analysis**: Identifies common patterns including:
  - Domain frequency (which websites appear most)
  - Associated names
  - Geographic locations
  - Business vs. personal indicators
  - Spam/scam warnings
- **Rate Limiting**: Built-in 2-second delays between searches to avoid throttling
- **Colored Terminal Output**: Easy-to-read results with color coding
- **JSON Export**: Option to save detailed results for further analysis

## 📋 Prerequisites

1. **Python 3.6+** 🐍
2. **ddgr** - DuckDuckGo command-line search tool (included in requirements.txt)

### Setting Up Python Virtual Environment (Recommended) 🔧

It's recommended to use a virtual environment to keep dependencies isolated:

```bash
# Create a virtual environment
python3 -m venv telespot-env

# Activate the virtual environment
# On Linux/macOS:
source telespot-env/bin/activate

# On Windows:
telespot-env\Scripts\activate
```

### Installing Dependencies

Once your virtual environment is activated:

```bash
# Install from requirements.txt
pip install -r requirements.txt
```

### Manual Installation (Alternative)

If you prefer to install ddgr manually without a virtual environment:

```bash
# Using pip
pip install ddgr

# On Debian/Ubuntu
sudo apt install ddgr

# On Arch Linux
sudo pacman -S ddgr

# On macOS with Homebrew
brew install ddgr
```

## 📥 Installation

### Automated Setup (Easiest) ⚡

Use the provided setup script to automatically create the virtual environment and install dependencies:

```bash
# Clone the repository
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot

# Run the setup script
chmod +x setup.sh
./setup.sh
```

Or download directly:
```bash
# Download all files
wget https://raw.githubusercontent.com/thumpersecure/Telespot/main/telespot.py
wget https://raw.githubusercontent.com/thumpersecure/Telespot/main/requirements.txt
wget https://raw.githubusercontent.com/thumpersecure/Telespot/main/setup.sh

# Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Check Python version
- ✅ Create virtual environment (telespot-env)
- ✅ Install all dependencies
- ✅ Make telespot.py executable
- ✅ Offer to run TeleSpot immediately

### Manual Setup (Recommended for Learning)

1. **Clone or download TeleSpot:**
```bash
# Clone the repository
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot

# Or download individual files
wget https://raw.githubusercontent.com/thumpersecure/Telespot/main/telespot.py
wget https://raw.githubusercontent.com/thumpersecure/Telespot/main/requirements.txt
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv telespot-env
source telespot-env/bin/activate  # On Linux/macOS
# telespot-env\Scripts\activate   # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Make the script executable:**
```bash
chmod +x telespot.py
```

5. **Run TeleSpot:**
```bash
./telespot.py
# or
python telespot.py
```

### Quick Install (Without Virtual Environment)

1. Download the script:
```bash
wget https://raw.githubusercontent.com/thumpersecure/Telespot/main/telespot.py
# or
curl -O https://raw.githubusercontent.com/thumpersecure/Telespot/main/telespot.py
```

2. Install ddgr globally:
```bash
pip install ddgr
```

3. Make it executable:
```bash
chmod +x telespot.py
```

## 🚀 Usage

> **Note:** Make sure your virtual environment is activated before running TeleSpot:
> ```bash
> source telespot-env/bin/activate  # Linux/macOS
> # telespot-env\Scripts\activate   # Windows
> ```

### Basic Usage

Run the script and enter the phone number when prompted:

```bash
./telespot.py
```

### Command-Line Usage

Pass the phone number as an argument:

```bash
./telespot.py 5555551212
./telespot.py "(555) 555-1212"
./telespot.py 1-555-555-1212
```

The script accepts phone numbers in any format - it will strip out non-digit characters automatically.

## 🔢 Search Formats

The script searches for the following format variations:

1. `"555-555-1212"` - Quoted with dashes
2. `"(555) 555-1212"` - Quoted with parentheses
3. `"5555551212"` - Quoted digits only
4. `"15555551212"` - Quoted with country code
5. `"1 (555) 555-1212"` - Quoted with country code and parentheses
6. `"1 555-555-1212"` - Quoted with country code and dashes
7. `(555-555-1212)` - Parentheses without quotes
8. `555-555-1212` - No quotes or parentheses

## 📊 Output

### Pattern Analysis Summary 📈

The script provides:

- **Total results found** across all formats
- **Unique domains** where the number appears
- **Most common domains** with frequency percentages
- **Potential names** associated with the number
- **Geographic locations** mentioned
- **Content type indicators**:
  - Business-related results
  - Personal-related results
  - Spam/scam warnings
- **Key insights** summarizing findings

### Example Output

```
================================================================================
PATTERN ANALYSIS SUMMARY
================================================================================

Total Results Found: 47
Unique Domains: 12

Most Common Domains:
  • whitepages.com: 8 occurrences (17.0%)
  • spokeo.com: 6 occurrences (12.8%)
  • truecaller.com: 5 occurrences (10.6%)

Potential Names Found:
  • John Smith: mentioned 12 time(s)
  • Jane Doe: mentioned 3 time(s)

Locations Mentioned:
  • Philadelphia, PA: 8 occurrence(s)
  • PA: 5 occurrence(s)

Content Type Indicators:
  • Business-related: 3 results
  • Spam/Scam indicators: 2 results

Key Insights:
  • Listed in online directories
  • Most associated name: John Smith
  • Most associated location: Philadelphia, PA
================================================================================
```

## 💾 Saving Results

After the analysis, you'll be prompted to save detailed results to a JSON file:

```
Save detailed results to JSON file? (y/n): y
Results saved to: phone_search_5555551212.json
```

The JSON file contains:
- Original phone number
- All search format variations used
- Complete search results for each format
- Full pattern analysis data

## ⏱️ Rate Limiting

The script includes a **2-second delay** between searches, which is a best practice to:
- Avoid being throttled or blocked by DuckDuckGo
- Be respectful to the search service
- Ensure consistent results

## 🎯 Use Cases

- **OSINT investigations** 🕵️: Gather information about unknown phone numbers
- **Spam identification** 🚫: Check if a number is associated with spam/scam reports
- **Contact verification** ✅: Verify the legitimacy of business phone numbers
- **Skip tracing** 🔎: Locate associated names and addresses
- **Fraud investigation** ⚖️: Part of your legal work gathering evidence

## 🔒 Privacy & Legal Considerations

- This tool uses publicly available search data
- Use responsibly and in compliance with applicable laws
- Respect privacy and data protection regulations
- Intended for legitimate investigative purposes

## 🔧 Troubleshooting

### "ddgr not found" error ❌
Make sure you:
1. Activated your virtual environment: `source telespot-env/bin/activate`
2. Installed dependencies: `pip install -r requirements.txt`

If you're not using a virtual environment, install ddgr using one of the methods in the Prerequisites section.

### ImportError or Module Not Found 🚨
This usually means your virtual environment isn't activated or dependencies aren't installed:
```bash
# Activate venv
source telespot-env/bin/activate

# Install/reinstall requirements
pip install -r requirements.txt
```

### No results found 🤷
- The phone number may not be indexed in search engines
- Try searching with fewer format variations
- The number may be new or unlisted

### Rate limiting issues ⏳
If you encounter rate limiting:
- Increase the delay between searches (edit the `time.sleep(2)` value)
- Run searches in smaller batches

## ⚙️ Technical Details

- **Language**: Python 3 🐍
- **Dependencies**: ddgr (specified in requirements.txt)
- **Recommended Setup**: Python virtual environment
- **Output**: Colored terminal text + optional JSON export
- **Search engine**: DuckDuckGo (via ddgr) 🦆

### Project Structure 📁
```
telespot/
├── telespot.py          # Main script
├── requirements.txt     # Python dependencies
├── setup.sh            # Automated setup script
└── README.md           # Documentation
```

## 👤 Author

Created by **Spin Apin** ([@thumpersecure](https://github.com/thumpersecure))

Designed for legal marketing and investigative purposes. Particularly useful for:
- Personal injury case investigations
- Verifying contact information
- Identifying spam/harassment sources
- Evidence gathering with proper documentation

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs via [GitHub Issues](https://github.com/thumpersecure/Telespot/issues)
- 💡 Suggest features or enhancements
- 🔧 Submit pull requests
- ⭐ Star the repository if you find it useful

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Disclaimer:** This tool is intended for legitimate investigative and OSINT purposes only. Users are responsible for ensuring their use complies with all applicable laws and regulations.

## 🔗 Links

- **GitHub Repository**: [https://github.com/thumpersecure/Telespot](https://github.com/thumpersecure/Telespot)
- **Report Issues**: [https://github.com/thumpersecure/Telespot/issues](https://github.com/thumpersecure/Telespot/issues)
- **Latest Release**: Check the [Releases page](https://github.com/thumpersecure/Telespot/releases)

---

Made with 💻 for OSINT and investigative work
