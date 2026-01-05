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
[![Python](https://img.shields.io/badge/Python-3.6+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/thumpersecure/Telespot/blob/main/LICENSE)
[![Version](https://img.shields.io/badge/Version-5.0--beta-orange)](https://github.com/thumpersecure/Telespot/releases)

**Python OSINT tool for phone number reconnaissance.** Searches across **Google, Bing, DuckDuckGo & Dehashed** using official APIs with **10 format variations**. Features **pattern analysis** for names/locations/usernames, **confidence scoring**, **User-Agent rotation**, and **random rate limiting** for anti-detection.

## Features

### Search Engines (API-Based)
| Engine | API Required | Free Tier |
|--------|--------------|-----------|
| Google Custom Search | Yes | 100 searches/day |
| Bing Search (Azure) | Yes | 1,000 searches/month |
| DuckDuckGo | No | Unlimited (Instant Answers) |
| Dehashed | Yes (Optional) | Paid |

### Anti-Detection
- **User-Agent Rotation**: 11 different browser profiles (Chrome, Firefox, Edge, Safari, Mobile)
- **Random Rate Limiting**: 3-5 second random delays between searches
- **API-Based**: No web scraping, avoids CAPTCHAs and IP blocks

### Search Formats (10 Variations)
**Basic (4):**
1. `856-570-5151` - Dashes
2. `8565705151` - Digits only
3. `(856) 570-5151` - Parentheses
4. `+1856-570-5151` - International

**Quoted (4):**
5. `"856-570-5151"` - Exact match
6. `"8565705151"` - Exact digits
7. `"(856) 570-5151"` - Exact parentheses
8. `"+1856-570-5151"` - Exact international

**Special (2):**
9. `(856-570-5151)` - Variant
10. `"(856) 570-5151)"` - Variant

### Pattern Analysis
- **Names**: Extracts people's names from results
- **Locations**: Cities, states, zip codes
- **Usernames**: Social media handles (@username)
- **Confidence Score**: 0-100% based on pattern consistency

### Output Options
- **Verbose Mode** (`-v`): Complete listings with URLs
- **Colorful Mode** (`--colorful`): Rainbow terminal output
- **JSON Export** (`-o results.json`): Machine-readable output
- **TXT Export** (`-o results.txt`): Human-readable report
- **Summary Mode** (`--summary`): Pattern comparison chart

## Installation

```bash
# Clone repository
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot

# Install dependencies
pip install -r requirements.txt

# Configure API keys
./telespot.py --setup
```

### Requirements
- Python 3.6+
- `requests` library

## API Setup

Run the interactive setup wizard:
```bash
./telespot.py --setup
```

Or see [GUIDE_APIS.md](GUIDE_APIS.md) for detailed instructions on getting API keys.

**No API keys?** DuckDuckGo works without setup (limited to Instant Answers).

### Check Configuration
```bash
./telespot.py --api-status
```

Output:
```
API Configuration Status:
----------------------------------------
  [+] Google: CONFIGURED
  [+] Bing: CONFIGURED
  [+] DuckDuckGo: CONFIGURED
  [-] Dehashed: NOT CONFIGURED
----------------------------------------
  3/4 APIs configured
```

## Usage

### Basic Search
```bash
./telespot.py 8565705151
```

### With Options
```bash
# Add keywords to narrow results
./telespot.py 8565705151 -k "John Smith"

# Search specific site only
./telespot.py 8565705151 -s whitepages.com

# Include Dehashed breach database
./telespot.py 8565705151 --dehashed

# Verbose output with all details
./telespot.py 8565705151 -v

# Save results to JSON
./telespot.py 8565705151 -o results.json

# Rainbow color mode
./telespot.py 8565705151 --colorful

# Show DTMF tones
./telespot.py 8565705151 --dtmf

# International number
./telespot.py +442071234567 -c +44

# Everything combined
./telespot.py 8565705151 -v --colorful --summary --dehashed -k "owner" -o results.json
```

### Command Reference

```
telespot [phone] [options]

Positional:
  phone                 Phone number to search

Search Options:
  -k, --keyword WORD    Add keyword to search (e.g., "owner", "business")
  -s, --site DOMAIN     Limit to specific site (e.g., whitepages.com)
  -c, --country CODE    Country code (default: +1)
  --dehashed            Include Dehashed breach database search

Output Options:
  -o, --output FILE     Save results to file (.json or .txt)
  -v, --verbose         Show detailed listings with URLs
  --summary             Show pattern comparison chart
  --dtmf                Show DTMF tone representation

Display Options:
  --colorful            Enable rainbow color mode
  --no-color            Disable all colors

Configuration:
  --setup               Interactive API key setup
  --api-status          Show API configuration status

Maintenance:
  --update              Update from GitHub repository
  --version             Show version number

Debug:
  -d, --debug           Enable debug output (show API responses)
```

## Output Example

```
  _       *      _                     _   *
 | |_ ___| | ___  ___ _ __   ___ | |_
 | __/ _ \ |/ _ \/ __| '_ \ / _ \| __|*
 | ||  __/ |  __/\__ \ |_) | (_) | |_
  \__\___|_|\___||___/ .__/ \___/ \__|
*                    |_|    *   v5.0-beta

Searching for: 8565705151
Country code: +1
Using 10 format variations

API Configuration Status:
----------------------------------------
  [+] Google: CONFIGURED
  [+] Bing: CONFIGURED
  [+] DuckDuckGo: CONFIGURED
  [-] Dehashed: NOT CONFIGURED
----------------------------------------
  3/4 APIs configured

[1/10] Searching: 856-570-5151
  → Google API... (8 results)
  → Bing API... (10 results)
  → DuckDuckGo... (2 results)
  ✓ 20 total for this format
  ⏳ Waited 4.2 seconds

[2/10] Searching: 8565705151
  → Google API... (5 results)
  → Bing API... (7 results)
  → DuckDuckGo... (0 results)
  ✓ 12 total for this format
  ⏳ Waited 3.8 seconds

...

Total Results: 127

======================================================================
PATTERN ANALYSIS SUMMARY
======================================================================

Confidence Score: HIGH (78%)

Total Results Found: 127
Unique URLs: 84

Results by Source:
  • Google: 52 results
  • Bing: 61 results
  • DuckDuckGo: 14 results

Names Found:
  • John Smith: mentioned 12 time(s) ⭐
  • Jane Doe: mentioned 3 time(s)
  • Mike Johnson: mentioned 2 time(s)

Locations Mentioned:
  • Philadelphia, PA: 15 occurrence(s) ⭐
  • PA: 10 occurrence(s)
  • 19103: 4 occurrence(s)

Usernames Found:
  • @johnsmith: 3 occurrence(s) ⭐
  • @jsmith215: 2 occurrence(s)

Key Insights:
  • Most associated name: John Smith
  • Most associated location: Philadelphia, PA
======================================================================

Results saved to: results.json
```

## Summary Comparison Mode

With `--summary`, see a visual chart of patterns:

```
SUMMARY COMPARISON
======================================================================

Items appearing in multiple results (higher confidence):

  NAME     | ████████████ | John Smith (12x)
  NAME     | ███ | Jane Doe (3x)
  LOCATION | ███████████████ | Philadelphia, PA (15x)
  LOCATION | ██████████ | PA (10x)
  USERNAME | ███ | @johnsmith (3x)
```

## Use Cases

- **OSINT Investigations**: Gather information about unknown phone numbers
- **Spam Identification**: Check if a number is associated with spam/scam reports
- **Contact Verification**: Verify legitimacy of business phone numbers
- **Skip Tracing**: Locate associated names and addresses
- **Fraud Investigation**: Gather evidence for legal work

## Technical Details

### User Agents (11 profiles)
- Chrome (Windows, Mac, Linux)
- Firefox (Windows, Mac, Linux)
- Edge (Windows)
- Safari (Mac)
- Mobile (iPhone, Android)

### Rate Limiting
- Random delay: 3-5 seconds between format searches
- 1 second delay between API calls within same format
- Prevents IP blocking and respects API limits

### Configuration File
API keys stored in `.telespot_config`:
```ini
# Google Custom Search API
google_api_key=AIzaSy...
google_cse_id=017576...

# Bing Search API (Azure)
bing_api_key=a1b2c3...

# Dehashed API (optional)
dehashed_api_key=email@example.com:key123

# Settings
default_country_code=+1
delay_seconds=2
```

File permissions: `600` (owner read/write only)

## Troubleshooting

### No results
1. Check API status: `./telespot.py --api-status`
2. Verify API keys are valid
3. Try with `--debug` to see API responses
4. DuckDuckGo Instant Answers only works for known topics

### API quota exceeded
- **Google**: 100/day, resets at midnight UTC
- **Bing**: 1,000/month, resets monthly
- **DuckDuckGo**: No limits (but limited result types)

### Connection errors
- Check internet connection
- Use `--debug` to see detailed error messages
- Some APIs may be temporarily unavailable

## Files

| File | Description |
|------|-------------|
| `telespot.py` | Main script (1,238 lines) |
| `.telespot_config` | API keys (created by --setup) |
| `requirements.txt` | Dependencies (`requests>=2.25.0`) |
| `GUIDE_APIS.md` | Detailed API setup guide |
| `LICENSE` | MIT License |
| `README.md` | This file |

## Contributing

Pull requests welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Credits

- Created by **Spin Apin** ([@thumpersecure](https://github.com/thumpersecure))
- User-Agent rotation concept from [@kaifcodec](https://github.com/kaifcodec)

## Version History

| Version | Changes |
|---------|---------|
| 5.0-beta | Complete rewrite: API-based search, 10 formats, user-agent rotation, random rate limiting |
| 4.5 | Added user-agent rotation |
| 4.0 | API integration |
| 3.0 | Multi-engine search |
| 2.0 | Pattern analysis |
| 1.0 | Initial release |

## License

MIT License - See [LICENSE](LICENSE)

## Links

- **Repository**: https://github.com/thumpersecure/Telespot
- **Issues**: https://github.com/thumpersecure/Telespot/issues
- **Releases**: https://github.com/thumpersecure/Telespot/releases

---

**Disclaimer:** This tool is intended for legitimate investigative and OSINT purposes only. Users are responsible for ensuring their use complies with all applicable laws and regulations. Do not use for harassment, stalking, or any illegal purposes.
