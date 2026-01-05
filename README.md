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

A Python script that searches telephone numbers across **Google, Bing, DuckDuckGo, and Dehashed** for phone numbers and focuses on identifying **names, locations, and usernames** in the results. Features API-based searching to avoid CAPTCHAs and IP blocks!

## Features

### Search Capabilities
- **Google Custom Search API** - Up to 100 free searches/day
- **Bing Search API** - 1,000 free searches/month
- **DuckDuckGo Instant Answer API** - Always included (no API needed)
- **Dehashed Integration** - Optional breach database search

### Analysis Features
- **Pattern Analysis**: Names, locations, usernames
- **Confidence Score**: 0-100% accuracy rating
- **10 Search Formats**: Comprehensive format variations
- **Site-Specific Search**: Limit to whitepages.com, facebook.com, etc.
- **Keyword Enhancement**: Add custom keywords to searches

### Output Options
- **Verbose Mode**: Complete listings with URLs
- **Colorful Mode**: Rainbow terminal output
- **JSON/TXT Export**: Save results for later
- **Summary Comparison**: See patterns across results

## Quick Install

```bash
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
pip install -r requirements.txt
./telespot.py --setup
```

## API Setup (5 minutes)

Run the setup wizard:
```bash
./telespot.py --setup
```

This guides you through entering API keys. See [GUIDE_APIS.md](GUIDE_APIS.md) for detailed instructions.

**Don't have API keys?** DuckDuckGo works without any setup (limited results).

## Usage

### Basic Usage
```bash
./telespot.py 5555551212
```

### With Options
```bash
# Add keywords
./telespot.py 5555551212 -k "John Smith"

# Search specific site
./telespot.py 5555551212 -s whitepages.com

# Include breach database
./telespot.py 5555551212 --dehashed

# Verbose output
./telespot.py 5555551212 -v

# Save to JSON
./telespot.py 5555551212 -o results.json

# Rainbow colors
./telespot.py 5555551212 --colorful

# Everything
./telespot.py 5555551212 -v --colorful --dehashed -k "Philadelphia" -o results.json
```

### All Options

| Flag | Description |
|------|-------------|
| `-k, --keyword` | Add search keywords |
| `-s, --site` | Limit to specific site |
| `-c, --country` | Country code (default: +1) |
| `--dehashed` | Include breach database |
| `-o, --output` | Save to file (.json or .txt) |
| `-v, --verbose` | Show detailed listings |
| `--summary` | Show comparison summary |
| `--dtmf` | Show DTMF representation |
| `--colorful` | Rainbow color mode |
| `--no-color` | Disable colors |
| `--setup` | Configure API keys |
| `--api-status` | Show API status |
| `--update` | Update from repository |
| `-d, --debug` | Debug output |

## Search Formats

The script searches **10 format variations**:

**Basic (4):**
1. `215-555-1234` - Dashes
2. `2155551234` - Digits only
3. `(215) 555-1234` - Parentheses
4. `+1215-555-1234` - International

**Quoted (4):**
5. `"215-555-1234"` - Exact match
6. `"2155551234"` - Exact digits
7. `"(215) 555-1234"` - Exact parentheses
8. `"+1215-555-1234"` - Exact international

**Special (2):**
9. `(215-555-1234)` - Variant
10. `"(215) 555-1234)"` - Variant

## Output Example

```
================================================================================
PATTERN ANALYSIS SUMMARY
================================================================================

Confidence Score: HIGH (78%)

Total Results Found: 42
Unique URLs: 28

Results by Source:
  • Google: 20 results
  • Bing: 14 results
  • DuckDuckGo: 8 results

Names Found:
  • John Smith: mentioned 12 time(s) ⭐
  • Jane Doe: mentioned 3 time(s)

Locations Mentioned:
  • Philadelphia, PA: 15 occurrence(s) ⭐
  • PA: 10 occurrence(s)

Key Insights:
  • Most associated name: John Smith
  • Most associated location: Philadelphia, PA
================================================================================
```

## API Comparison

| API | Free Tier | Best For |
|-----|-----------|----------|
| Google | 100/day | Most comprehensive |
| Bing | 1,000/month | Good backup |
| DuckDuckGo | Unlimited | Always works |
| Dehashed | Paid | Breach data |

## Use Cases

- **OSINT Investigations**: Gather info on unknown numbers
- **Spam Identification**: Check spam/scam associations
- **Contact Verification**: Verify business numbers
- **Skip Tracing**: Locate associated names/addresses

## Troubleshooting

### No results
- Check your API keys with `--api-status`
- Try different phone formats
- Use `--debug` to see API responses

### API quota exceeded
- Google resets daily at midnight UTC
- Bing resets monthly
- DuckDuckGo has no limits

### Connection errors
- Check internet connection
- Some APIs may be temporarily down
- Use `--debug` to see errors

## Files

| File | Purpose |
|------|---------|
| `telespot.py` | Main script |
| `.telespot_config` | API keys (created by --setup) |
| `requirements.txt` | Dependencies |
| `GUIDE_APIS.md` | API setup guide |

## Author

Created by **Spin Apin** ([@thumpersecure](https://github.com/thumpersecure))

## License

MIT License - See [LICENSE](LICENSE)

## Links

- Repository: https://github.com/thumpersecure/Telespot
- Issues: https://github.com/thumpersecure/Telespot/issues

---

**Disclaimer:** This tool is for legitimate investigative and OSINT purposes only. Users are responsible for compliance with applicable laws.
