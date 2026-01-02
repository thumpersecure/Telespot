# 📞 TeleSpot 🔍

```
████████╗███████╗██╗     ███████╗███████╗██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     █████╗  ███████╗██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██╔═══╝ ██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗███████║██║     ╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝    ╚═╝   
                                                         version 4.9
```

[![GitHub](https://img.shields.io/badge/GitHub-thumpersecure/Telespot-blue?logo=github)](https://github.com/thumpersecure/Telespot)
[![Python](https://img.shields.io/badge/Python-3.6+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/thumpersecure/Telespot/blob/main/LICENSE)

A Python script that searches telephone numbers across **Google, Bing, DuckDuckGo, and Dehashed** for phone numbers and focuses on identifying **names, locations, and usernames** in the results. Features API-based searching to avoid CAPTCHAs and IP blocks!

✨ Dev Updates - January 2 2026
1️⃣ All bugs are being reviewed today Jan 2 2026
2️⃣ Testing new version will be done by Jan 4 2026.
3️⃣ First COMPLETE release to be finished by Jan 6 2026.
4️⃣ A lot of great new features to be included!!!!

### 🔍 Search Capabilities
- **🔓 API-Based Search**: Google Custom Search, Bing Search, DuckDuckGo
- **🦆 DuckDuckGo Always Included**: Free backup search engine (no API needed)
- **🔓 Dehashed Integration**: Search breach databases for phone numbers (optional paid service)
- **🎯 Site-Specific Search**: Limit searches to specific people-finder sites:
  - YellowPages.com, WhitePages.com, ThatsThem.com
  - Information.com, InstantCheckmate.com
  - Facebook.com, Yahoo.com
- **📞 10 Search Formats**: Comprehensive format variations including quoted searches
- **🔑 Keyword Enhancement**: Add custom keywords to searches (e.g., "John Smith")

### 📊 Analysis Features
- **Focused Pattern Analysis**:
  - 📛 **Associated names** (people mentioned with the number)
  - 📍 **Geographic locations** (cities, states, zip codes)
  - 👤 **Username Correlations** - Find usernames appearing in 2+ results
  - ✅ **Results by source** (which search engine found what)
- **🎯 Confidence Score**: Percentage-based accuracy rating (0-100%)
- **📋 Dossier Mode**: Specialized searches for persons or businesses
- **💾 Smart File Saving**: Default TXT format with custom naming

### 🎨 User Experience
- **--verbose mode**: See complete listings with URLs, titles, and descriptions
- **--colorful mode**: Enhanced visual experience with extra colors
- **--dtmf mode**: Play DTMF tones while searching (fun audio feedback!)
- **--usernames**: Focus on username correlation analysis
- **--delay option**: Customize rate limiting (default: 2 seconds)
- **Colored Terminal Output**: Easy-to-read results with color coding

## 🆕 What's New in v4.5

✅ **Site-specific search** - Search only on people-finder sites  
✅ **Dehashed integration** - Check breach databases  
✅ **DTMF tone playback** - Audio feedback while searching  
✅ **Username correlation** - Find linked social media profiles  
✅ **Enhanced pattern matching** - Better name/location detection

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

```bash
./telespot.py 5555551212
# or
python telespot.py "(555) 555-1212"
```

### Advanced Options

```bash
# Verbose mode - see all URLs, titles, and descriptions
./telespot.py --verbose 5555551212

# Colorful mode - enhanced visual experience  
./telespot.py --colorful 5555551212

# Add keywords to search
./telespot.py --keywords "John Smith" 5555551212

# Site-specific search (people-finder sites)
./telespot.py --site whitepages.com 5555551212
./telespot.py --site facebook.com 5555551212

# Search Dehashed breach database
./telespot.py --dehashed 5555551212

# Play DTMF tones while searching (fun mode!)
./telespot.py --dtmf 5555551212

# Focus on username correlations
./telespot.py --usernames 5555551212

# Combine multiple options
./telespot.py --verbose --colorful --keywords "Acme Corp" --site yellowpages.com 5555551212

# Custom delay between searches (in seconds)
./telespot.py --delay 5 5555551212

# Generate a person dossier
./telespot.py --dossier person 5555551212

# Generate a business dossier
./telespot.py --dossier business 5555551212

# The works - everything!
./telespot.py --verbose --colorful --dehashed --usernames --dtmf --keywords "Philadelphia" 5555551212
```

### All Options

| Flag | Description |
|------|-------------|
| `--setup` | Run API configuration wizard |
| `--verbose`, `-v` | Show complete result listings with URLs |
| `--colorful`, `-c` | Enable colorful display mode |
| `--keywords`, `-k` | Add search keywords (e.g., "John Smith") |
| `--delay` | Set delay between searches (default: 2 seconds) |
| `--dossier` | Generate dossier (person or business) |
| `--site` | Limit search to specific site (whitepages.com, facebook.com, etc.) |
| `--dehashed` | Include Dehashed breach database search |
| `--dtmf` | Play DTMF tones while searching |
| `--usernames` | Focus on username correlation analysis |
| `--debug`, `-d` | Enable debug output |

### Site-Specific Searches

Available sites for `--site` option:
- `yellowpages.com` - Business/residential directory
- `whitepages.com` - People finder
- `thatsthem.com` - Reverse phone lookup
- `information.com` - Public records
- `instantcheckmate.com` - Background checks
- `facebook.com` - Social media
- `yahoo.com` - General search

### Example Workflow

```bash
# 1. Setup API keys (one-time)
./telespot.py --setup

# 2. Basic search
./telespot.py 2155551234

# 3. Search with context
./telespot.py --keywords "Philadelphia lawyer" 2155551234

# 4. Detailed investigation
./telespot.py --verbose --colorful --dossier person 2155551234

# 5. Business lookup
./telespot.py --keywords "Acme Industries" --dossier business 8005551212
```

## 🔢 Search Formats

The script searches for **10 different format variations** via APIs:

### Basic Formats (4)
1. `555-555-1212` - Dashes
2. `5555551212` - Digits only
3. `(555) 555-1212` - Parentheses and dashes
4. `+1555-555-1212` - International format

### Quoted Formats (4)
5. `"555-555-1212"` - Quoted dashes (exact match)
6. `"5555551212"` - Quoted digits (exact match)
7. `"(555) 555-1212"` - Quoted parentheses (exact match)
8. `"+1555-555-1212"` - Quoted international (exact match)

### Special Formats (2)
9. `(555-555-1212)` - Parentheses variant
10. `"(555) 555-1212)"` - Quoted parentheses variant

**Why quoted searches matter:** Wrapping queries in quotes forces exact matching, which dramatically improves phone number search accuracy!

### Search Engines

Each format is searched using:
- 🦆 **DuckDuckGo API** (always included, free, no API needed)
- 🔵 **Google Custom Search API** (up to 10 results per format, if configured)
- 🟢 **Bing Search API** (up to 10 results per format, if configured)

**Total**: Up to 300 results per search with all engines configured (10 formats × 3 engines × 10 results)

### With Keywords

When you add keywords (e.g., `--keywords "John Smith"`):
```bash
555-555-1212 + John+Smith
"5555551212" + John+Smith
(555) 555-1212 + John+Smith
# ... and so on for all 10 formats
```

## 📊 Output

### Pattern Analysis Summary 📈

The script provides:

- **🎯 Confidence Score** (0-100%) - How reliable the results appear
- **Total Results** found across all search engines
- **Unique URLs** discovered
- **Results by source** (Google, Bing, DuckDuckGo breakdown)
- **📛 Names found** - People's names associated with the number
- **📍 Locations mentioned** - Cities, states, and zip codes
- **🔍 Key insights** - Most frequently appearing name and location

### Confidence Score Calculation

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 75-100% | 🟢 HIGH | Strong evidence, consistent patterns |
| 50-74% | 🟡 MEDIUM | Some evidence, moderate patterns |
| 0-49% | 🔴 LOW | Weak evidence, inconsistent patterns |

The score is based on:
- Number of results found (30%)
- Name consistency across results (35%)
- Location consistency across results (25%)
- Multiple source verification (10%)

### Example Output (Standard Mode)

```
================================================================================
PATTERN ANALYSIS SUMMARY
================================================================================

🎯 Confidence Score: 78% (HIGH)

Total Results Found: 42
Unique URLs: 28

Results by Source:
  • DuckDuckGo: 8 results
  • Google: 20 results
  • Bing: 14 results

📛 Names Found:
  • John Smith: mentioned 12 time(s)
  • Jane Doe: mentioned 3 time(s)
  • Mike Johnson: mentioned 2 time(s)

📍 Locations Mentioned:
  • Philadelphia, PA: 15 occurrence(s)
  • PA: 10 occurrence(s)
  • 19102: 4 occurrence(s)

🔍 Key Insights:
  • Most associated name: John Smith
  • Most associated location: Philadelphia, PA
================================================================================
```

### Example Output (Verbose Mode)

With `--verbose`, you also get complete listings:

```
================================================================================
VERBOSE RESULTS - ALL LISTINGS
================================================================================

Format: "555-555-1212"
────────────────────────────────────────────────────────────────────────────────

[1] John Smith - Philadelphia Lawyer
🔗 URL: https://example.com/john-smith
📄 Description: Attorney John Smith, practicing in Philadelphia since 2010...
🔍 Source: Google

[2] Smith & Associates Law Firm
🔗 URL: https://smithlaw.com/contact
📄 Description: Contact us at (555) 555-1212...
🔍 Source: Bing

...
```

### Dossier Mode Output

With `--dossier person` or `--dossier business`:

```
📋 DOSSIER TYPE: PERSON

🎯 Confidence Score: 82% (HIGH)
...
[Enhanced analysis focused on personal/business information]
```

## 💾 Saving Results

After the analysis, you'll be prompted to save results:

```
Save results to file? (y/n): y
Enter filename (or press Enter for default): 
✓ Results saved to: telespot_5555551212_20241228_143022.txt
```

### File Format

Results are saved as **text files (.txt)** by default, containing:

1. **Header** - Phone number, search date, confidence score
2. **Summary** - Total results, sources, names, locations
3. **Detailed Results** - Complete listings with URLs, titles, and descriptions

### Custom Naming

You can specify a custom filename:
```
Enter filename (or press Enter for default): john_smith_investigation
✓ Results saved to: john_smith_investigation.txt
```

Or use the default (recommended):
```
telespot_[PHONE]_[TIMESTAMP].txt
Example: telespot_5555551212_20241228_143022.txt
```

### File Contents Example

```
================================================================================
TELESPOT SEARCH RESULTS
================================================================================

Phone Number: 5555551212
Search Date: 2024-12-28 14:30:22
Confidence Score: 78%

================================================================================
SUMMARY
================================================================================

Total Results: 42
Unique URLs: 28

Results by Source:
  - DuckDuckGo: 8 results
  - Google: 20 results
  - Bing: 14 results

Names Found:
  - John Smith: 12 mention(s)
  - Jane Doe: 3 mention(s)

Locations Mentioned:
  - Philadelphia, PA: 15 occurrence(s)
  - PA: 10 occurrence(s)

================================================================================
DETAILED RESULTS
================================================================================

Format: "555-555-1212"
--------------------------------------------------------------------------------

[1] John Smith - Philadelphia Lawyer
URL: https://example.com/john-smith
Source: Google
Description: Attorney John Smith has been practicing law in Philadelphia...

...
```

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
