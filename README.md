# telespot

```
  _       *      _                     _   *
 | |_ ___| | ___  ___ _ __   ___ | |_
 | __/ _ \ |/ _ \/ __| '_ \ / _ \| __|*
 | ||  __/ |  __/\__ \ |_) | (_) | |_
  \__\___|_|\___||___/ .__/ \___/ \__|
*                    |_|    *   v5.0-beta
```

[![GitHub](https://img.shields.io/badge/GitHub-thumpersecure/Telespot-blue?logo=github)](https://github.com/thumpersecure/Telespot)
[![Python](https://img.shields.io/badge/Python-3.7+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/thumpersecure/Telespot/blob/main/LICENSE)
[![Version](https://img.shields.io/badge/Version-5.0--beta-orange)](https://github.com/thumpersecure/Telespot/releases)

**Multi-Engine Phone Number OSINT Tool**

telespot searches for phone numbers across **10 search engines** and people search sites to gather intelligence about names, locations, and business associations.

## What's New in v5.0-beta

- **10 Search Engines**: Google, Bing, DuckDuckGo, Yahoo, Ask, AOL, Ecosia, Startpage, Qwant, Brave
- **People Search Sites**: truepeoplesearch.com, whitepages.com, spokeo.com, and more
- **Random Rate Limiting**: 3-5 second randomized delays to avoid detection
- **Enhanced User Agent Rotation**: 14+ browser profiles
- **Confidence Scoring**: Results ranked by appearance frequency
- **International Support**: 40+ country codes
- **Rainbow Mode**: Colorful output option
- **JSON Export**: Full results export
- **Update Command**: Built-in self-update feature

## Quick Install

### One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/thumpersecure/Telespot/main/just-do-it.sh | bash
```

Or with wget:
```bash
wget -qO- https://raw.githubusercontent.com/thumpersecure/Telespot/main/just-do-it.sh | bash
```

### Manual Install

```bash
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
pip install -r requirements.txt
python3 telespot.py --help
```

See [QUICK_INSTALL_GUIDE.md](QUICK_INSTALL_GUIDE.md) for platform-specific instructions.

## Usage

### Basic Search

```bash
python3 telespot.py 2155551234
```

### Search Options

```bash
# Add a keyword to narrow results
python3 telespot.py 2155551234 -k "pizza"

# Search a specific site only
python3 telespot.py 2155551234 -s whitepages.com

# International number
python3 telespot.py +442071234567 -c +44

# Verbose output with JSON export
python3 telespot.py 2155551234 -v -o results.json

# Show comparison summary
python3 telespot.py 2155551234 --summary

# Rainbow colors
python3 telespot.py 2155551234 --colorful
```

### All Options

```
telespot [phone] [options]

Search Options:
  -k, --keyword WORD    Add keyword to search
  -s, --site DOMAIN     Search specific site only
  -c, --country CODE    Country code (default: +1)

Output Options:
  -o, --output FILE     Save results to JSON file
  -v, --verbose         Show verbose output
  --summary             Show comparison summary
  --dtmf                Show DTMF representation

Display Options:
  --colorful            Enable rainbow colors
  --no-color            Disable all colors

Configuration:
  --setup               Interactive API setup
  --api-status          Show API status
  --update              Update from repository

Debug:
  -d, --debug           Enable debug mode
  -h, --help            Show help
  --version             Show version
```

## Search Engines

telespot searches across 10 engines in order:

| # | Engine | Description |
|---|--------|-------------|
| 1 | Google | Most comprehensive results |
| 2 | Bing | Microsoft search |
| 3 | DuckDuckGo | Privacy-focused |
| 4 | Yahoo | Legacy but useful |
| 5 | Ask | Ask.com |
| 6 | AOL | Powered by Bing |
| 7 | Ecosia | Tree-planting search |
| 8 | Startpage | Privacy proxy to Google |
| 9 | Qwant | European privacy search |
| 10 | Brave | Privacy browser search |

Plus targeted searches on people search sites:
- truepeoplesearch.com
- whitepages.com
- spokeo.com
- fastpeoplesearch.com
- and more...

## Phone Number Formats

Each search uses 10 format variations:

1. `+12155551234` - International
2. `"+12155551234"` - Quoted international
3. `(215) 555-1234` - Standard US
4. `"1 (215) 555-1234"` - Quoted with country
5. `"215-555-1234"` - Quoted dashes
6. `215-555-1234` - Dashes
7. `215.555.1234` - Dots
8. `2155551234` - Digits only
9. `"2155551234"` - Quoted digits
10. `215 555 1234` - Spaces

## Output Example

```
══════════════════════════════════════════════════════════════════════
TELESPOT ANALYSIS RESULTS
══════════════════════════════════════════════════════════════════════
Phone: 2155551234
Total Results: 127
Confidence: HIGH
══════════════════════════════════════════════════════════════════════

Results by Source:
  [ 23] Google
  [ 18] Bing
  [ 15] DuckDuckGo
  [ 12] Yahoo
  ...

Primary Findings:
  Name: John Smith
  Location: Philadelphia, PA
  Business: Smith Plumbing LLC

Names Detected:
  [5x] John Smith **
  [3x] J Smith **
  [1x] Jonathan Smith

High-Confidence Intel (2+ appearances):
  [NAME] John Smith (appeared 5x)
  [LOCATION] Philadelphia, PA (appeared 4x)
  [BUSINESS] Smith Plumbing LLC (appeared 3x)
```

## API Integration (Optional)

For enhanced lookups, configure API keys:

| API | Purpose | Free Tier |
|-----|---------|-----------|
| NumVerify | Phone validation | 100/month |
| AbstractAPI | Phone validation | 250/month |
| Twilio | Caller ID lookup | Paid |
| OpenCNAM | CNAM lookup | Paid |
| Telnyx | Phone intelligence | Paid |

Configure with:
```bash
python3 telespot.py --setup
```

See [GUIDE_APIS.md](GUIDE_APIS.md) for detailed instructions.

## Configuration

Settings stored in `config.txt`:

```ini
# API Keys
numverify_api_key=your_key
abstract_api_key=your_key

# Settings
default_country_code=+1
rate_limit_min=3
rate_limit_max=5
verbose=false
colorful_mode=false
```

## International Support

40+ country codes supported:

```
+1  USA/Canada     +44 UK           +49 Germany
+33 France         +61 Australia    +81 Japan
+91 India          +86 China        +7  Russia
+55 Brazil         +52 Mexico       +34 Spain
```

## Updating

```bash
python3 telespot.py --update
```

Or with git:
```bash
git pull origin main
```

## Legal Notice

This tool is for **authorized research and educational purposes only**.

- Only search phone numbers you have permission to investigate
- Respect privacy laws in your jurisdiction
- Do not use for harassment or illegal purposes

## Troubleshooting

### No results
- Check internet connection
- Try different formats
- Use `-d` debug mode
- Number may have limited online presence

### Getting blocked
- Rate limiting is automatic (3-5s delays)
- Use a VPN if needed
- Wait and retry

### Dependencies
```bash
pip install --upgrade requests beautifulsoup4 lxml
```

## Files

| File | Description |
|------|-------------|
| `telespot.py` | Main script |
| `config.txt` | Configuration file |
| `setup.py` | Python installer |
| `just-do-it.sh` | One-line installer |
| `requirements.txt` | Dependencies |
| `README.md` | This file |
| `QUICK_INSTALL_GUIDE.md` | Quick start guide |
| `GUIDE_APIS.md` | API setup guide |

## Contributing

Pull requests welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Version History

- **v5.0-beta** - Complete rewrite, 10 search engines, enhanced analysis
- **v4.5** - User agent rotation
- **v4.0** - API integration
- **v3.0** - Multi-engine search
- **v2.0** - Pattern analysis
- **v1.0** - Initial release

## Author

Created by **Spin Apin** ([@thumpersecure](https://github.com/thumpersecure))

## License

MIT License - See [LICENSE](LICENSE)

## Links

- Repository: https://github.com/thumpersecure/Telespot
- Issues: https://github.com/thumpersecure/Telespot/issues
- Releases: https://github.com/thumpersecure/Telespot/releases

---

Made with care for OSINT and investigative work
