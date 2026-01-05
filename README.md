# telespot

```
  _       *      _                     _   *
 | |_ ___| | ___  ___ _ __   ___ | |_
 | __/ _ \ |/ _ \/ __| '_ \ / _ \| __|*
 | ||  __/ |  __/\__ \ |_) | (_) | |_
  \__\___|_|\___||___/ .__/ \___/ \__|
*                    |_|    *   v5.0-beta
```

[![Python](https://img.shields.io/badge/Python-3.6+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Phone number OSINT tool. Searches Google, Bing, DuckDuckGo & Dehashed APIs to find names, locations, and usernames.

## Quick Start

```bash
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
pip install -r requirements.txt
./telespot.py --setup
./telespot.py 8565705151
```

## Features

- **4 Search APIs**: Google, Bing, DuckDuckGo, Dehashed (optional)
- **10 Phone Formats**: Dashes, digits, parentheses, international, quoted variants
- **Pattern Analysis**: Extracts names, locations, usernames with confidence scoring
- **Anti-Detection**: User-agent rotation (11 profiles), random 3-5s delays
- **Output Options**: Verbose, colorful, JSON/TXT export, summary charts

## Usage

```bash
./telespot.py 8565705151              # Basic search
./telespot.py 8565705151 -v           # Verbose output
./telespot.py 8565705151 --colorful   # Rainbow mode
./telespot.py 8565705151 -k "name"    # Add keyword
./telespot.py 8565705151 -s site.com  # Specific site
./telespot.py 8565705151 --dehashed   # Include breach data
./telespot.py 8565705151 -o out.json  # Save to JSON
./telespot.py +442071234567 -c +44    # International
./telespot.py --api-status            # Check API config
./telespot.py --setup                 # Configure APIs
```

## Options

```
Search:   -k KEYWORD    Add search keyword
          -s SITE       Limit to site
          -c CODE       Country code (default: +1)
          --dehashed    Include Dehashed

Output:   -v            Verbose with URLs
          -o FILE       Save to .json or .txt
          --summary     Pattern comparison chart
          --dtmf        Show DTMF tones

Display:  --colorful    Rainbow colors
          --no-color    Disable colors

Config:   --setup       Setup API keys
          --api-status  Show API status
          --update      Update from GitHub
          -d            Debug mode
```

## API Setup

Run `./telespot.py --setup` or see [GUIDE_APIS.md](GUIDE_APIS.md).

| API | Free Tier |
|-----|-----------|
| Google Custom Search | 100/day |
| Bing (Azure) | 1,000/month |
| DuckDuckGo | Unlimited |
| Dehashed | Paid |

No API keys? DuckDuckGo works without setup.

## Config File

API keys stored in `.telespot_config`:

```
google_api_key=YOUR_KEY
google_cse_id=YOUR_CSE_ID
bing_api_key=YOUR_KEY
dehashed_api_key=email:key
```

## Credits

- **Spin Apin** ([@thumpersecure](https://github.com/thumpersecure))
- User-Agent rotation from [@kaifcodec](https://github.com/kaifcodec)

## License

MIT - See [LICENSE](LICENSE)

---

**Disclaimer:** For legitimate OSINT purposes only. Users must comply with applicable laws.
