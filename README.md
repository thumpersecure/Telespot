# 📞 TeleSpot 🔍

```
████████╗███████╗██╗     ███████╗███████╗██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     █████╗  ███████╗██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██╔═══╝ ██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗███████║██║     ╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝    ╚═╝   
                                                         version 3.0
```

[![GitHub](https://img.shields.io/badge/GitHub-thumpersecure/Telespot-blue?logo=github)](https://github.com/thumpersecure/Telespot)
[![Python](https://img.shields.io/badge/Python-3.6+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/thumpersecure/Telespot/blob/main/LICENSE)

A Python script that searches **Google and Bing via official APIs** for phone numbers and focuses on identifying **names and locations** in the results. No more CAPTCHAs or IP blocks!

## ✨ Features

- **🔓 API-Based Search**: Uses official Google Custom Search API and Bing Search API
  - **No CAPTCHAs** - Legitimate API access
  - **No IP blocks** - Designed for programmatic access
  - **Reliable results** - Consistent, unblocked searches
  - **Free tiers available** - 100 Google searches/day + 1,000 Bing searches/month
- **Multiple Format Searching**: Automatically generates 4 different phone number format variations
- **Focused Pattern Analysis**: Identifies common patterns:
  - 📛 **Associated names** (people mentioned with the number)
  - 📍 **Geographic locations** (cities, states, zip codes)
  - ✅ **Results by source** (which search engine found what)
- **Easy API Setup**: Interactive wizard to configure API keys
- **Fallback Option**: Uses DuckDuckGo API if no keys configured (limited results)
- **Colored Terminal Output**: Easy-to-read results with color coding
- **JSON Export**: Option to save detailed results for further analysis

## 🎯 Why v3.0?

**v1.x - v2.x had a fatal flaw:** Web scraping gets blocked!
- ❌ Search engines use CAPTCHAs
- ❌ IP addresses get blacklisted
- ❌ Results were unreliable

**v3.0 solves this with official APIs:**
- ✅ No blocks or CAPTCHAs
- ✅ Free tiers: 100-1000 searches/month
- ✅ Actually returns results!

## 📋 Prerequisites

1. **Python 3.6+** 🐍
2. **API Keys** (at least one recommended):
   - **Google Custom Search API** - 100 free searches/day
   - **Bing Search API** - 1,000 free searches/month
   - See [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) for detailed instructions
3. **Python package**: `requests` (auto-installed via requirements.txt)

### 🔑 API Setup (5 minutes)

**Quick setup wizard:**
```bash
./telespot.py --setup
```

This will guide you through entering your API keys. See [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) for detailed instructions on getting free API keys.

**Don't want to set up APIs?** TeleSpot will use DuckDuckGo as a fallback (limited results, but works without setup).

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

# Configure API keys (takes 5 minutes)
./telespot.py --setup
```

The setup script will:
- ✅ Check Python version
- ✅ Create virtual environment (telespot-env)
- ✅ Install all dependencies
- ✅ Make telespot.py executable

Then run `--setup` to configure your API keys (see [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)).

### Manual Setup

1. **Clone or download TeleSpot:**
```bash
# Clone the repository
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
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

5. **Configure API keys:**
```bash
./telespot.py --setup
```

6. **Run TeleSpot:**
```bash
./telespot.py 5555551212
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

### Debug Mode 🐛

If you're getting no results, run in debug mode to see what's happening:

```bash
./telespot.py --debug 5555551212
# or
python telespot.py -d 5555551212
```

This will show:
- Exact ddgr commands being run
- Sample results from each search
- Error messages and warnings

The script accepts phone numbers in any format - it will strip out non-digit characters automatically.

## 🔢 Search Formats

The script searches for the following format variations via **official APIs**:

1. `555-555-1212` - Dashes
2. `(555) 555-1212` - Parentheses and dashes
3. `5555551212` - Digits only
4. `1 555-555-1212` - Country code with dashes

Each format is searched using configured APIs:
- 🔵 **Google Custom Search API** (up to 10 results per format, if configured)
- 🟢 **Bing Search API** (up to 10 results per format, if configured)
- 🦆 **DuckDuckGo API** (fallback if no APIs configured, limited results)

**Total**: Up to 80 results per search with both APIs configured (4 formats × 2 engines × 10 results)

## 📊 Output

### Pattern Analysis Summary 📈

The script provides:

- **Total results found** across all search engines
- **Results by source** (Google, Bing, DuckDuckGo breakdown)
- **📛 Names found** - People's names associated with the number
- **📍 Locations mentioned** - Cities, states, and zip codes
- **🔍 Key insights** - Most frequently appearing name and location

### Example Output

```
================================================================================
PATTERN ANALYSIS SUMMARY
================================================================================

Total Results Found: 42

Results by Source:
  • Google: 18 results
  • Bing: 15 results
  • DuckDuckGo: 9 results

📛 Names Found:
  • John Smith: mentioned 8 time(s)
  • Jane Doe: mentioned 3 time(s)
  • Mike Johnson: mentioned 2 time(s)

📍 Locations Mentioned:
  • Philadelphia, PA: 12 occurrence(s)
  • PA: 8 occurrence(s)
  • 19102: 3 occurrence(s)

🔍 Key Insights:
  • Most associated name: John Smith
  • Most associated location: Philadelphia, PA
================================================================================
```

## 💾 Saving Results

After the analysis, you'll be prompted to save detailed results to a JSON file:

```
Save detailed results to file? (y/n): y
Results saved to: telespot_results_5555551212.json
```

The JSON file contains:
- Original phone number
- All search format variations used
- Complete search results from all engines
- Full pattern analysis data (names and locations)

## ⏱️ Rate Limiting

The script includes **smart rate limiting** to avoid being blocked:
- 1 second delay between search engines (Google → Bing → DuckDuckGo)
- 3 second delay between phone number formats
- Total search time: ~1-2 minutes for a complete search

This ensures:
- ✅ Respectful to search engines
- ✅ Avoids IP blocks or CAPTCHAs
- ✅ Consistent, reliable results

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

### Still getting "0 results" even with APIs configured? 🔍

**1. Verify API keys are loaded:**
```bash
./telespot.py --debug 5555551212
```
Look for messages like "Searching Google..." or "Searching Bing..."

**2. Check API status:**
- Google Custom Search: https://console.cloud.google.com/
- Bing Search: https://portal.azure.com/

Make sure:
- APIs are enabled
- You haven't exceeded quota
- Keys are valid

**3. Test APIs directly:**
```bash
# Test if config file exists
cat .telespot_config

# Should show your API keys
```

**4. Common issues:**
- **Wrong API enabled**: Make sure you enabled "Custom Search API" not just "Search API"
- **CSE not configured**: Your Custom Search Engine must be set to "Search the entire web"
- **Quota exceeded**: Check your API dashboard for usage limits

### "API quota exceeded" errors 📊

**Free tier limits:**
- Google: 100 searches/day
- Bing: 1,000 searches/month

**Solutions:**
- Wait for quota to reset (midnight UTC for Google, monthly for Bing)
- Use the other API as backup
- Upgrade to paid tier (rarely needed)

### "API key not configured" warning ⚠️
This usually means your virtual environment isn't activated or dependencies aren't installed:
```bash
# Activate venv
source telespot-env/bin/activate

# Install/reinstall requirements
pip install -r requirements.txt
```

### No results found 🤷
- The phone number may not be publicly indexed
- Try searching manually in a browser to confirm
- Number might be new, unlisted, or private

### Connection timeout errors ⏳
If searches are timing out:
- Check your internet connection
- The search engine might be temporarily down
- Try again in a few minutes

## ⚙️ Technical Details

- **Language**: Python 3 🐍
- **Dependencies**: requests (specified in requirements.txt)
- **Recommended Setup**: Python virtual environment
- **Output**: Colored terminal text + optional JSON export
- **Search method**: Official APIs (Google Custom Search, Bing Search) 🔐
- **Fallback**: DuckDuckGo Instant Answer API

### How It Works 🛠️

1. **Format Generation**: Creates 4 variations of the phone number
2. **API Calls**: Queries Google and/or Bing APIs for each format
3. **Pattern Analysis**: 
   - Identifies names using capitalization patterns
   - Detects locations via state codes, city names, and zip codes
   - Counts frequency of mentions
4. **Result Summary**: Displays most common names and locations

### API Benefits Over Web Scraping 📊

| Feature | v3.0 (APIs) | v2.0 (Web Scraping) |
|---------|-------------|---------------------|
| Blocks/CAPTCHAs | ✅ None | ❌ Constant |
| Results reliability | ✅ 100% | ❌ 10-20% |
| Rate limits | ✅ High (100-1000/month free) | ❌ Low (few searches before block) |
| Setup required | ⚠️ API keys (5 min) | ✅ None |

### Project Structure 📁
```
telespot/
├── telespot.py          # Main script
├── requirements.txt     # Python dependencies
├── setup.sh            # Automated setup script
├── .telespot_config    # API keys (created by --setup, add to .gitignore!)
├── API_SETUP_GUIDE.md  # Detailed API setup instructions
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
