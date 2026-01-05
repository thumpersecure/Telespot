#!/usr/bin/env python3
"""
telespot - Phone Number OSINT Tool
Version 5.0-beta

API-based phone number search across Google, Bing, and DuckDuckGo
with pattern recognition for names, locations, and usernames.
"""

import requests
import time
import re
import sys
import os
import json
import random
import argparse
import subprocess
from collections import Counter
from datetime import datetime
from urllib.parse import quote_plus

VERSION = "5.0-beta"
REPO_URL = "https://github.com/thumpersecure/Telespot"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".telespot_config")

# ═══════════════════════════════════════════════════════════════════════════════
# ASCII LOGO
# ═══════════════════════════════════════════════════════════════════════════════

def get_ascii_logo():
    """Returns the ASCII logo with blue/red twinkle effect on white"""
    W = '\033[97m'
    B = '\033[94m'
    R = '\033[91m'
    E = '\033[0m'

    logo = f"""
{W}  _       {R}*{W}      _                     _   {B}*{W}
{W} | |_ ___| | ___  ___ _ __   ___ | |_
{W} | __/ _ \\ |/ _ \\/ __| '_ \\ / _ \\| __|{R}*{W}
{W} | ||  __/ |  __/\\__ \\ |_) | (_) | |_
{W}  \\__\\___|_|\\___||___/ .__/ \\___/ \\__|
{B}*{W}                    |_|    {R}*{W}   {B}v{VERSION}{E}
"""
    return logo


def get_ascii_logo_mono():
    """Returns monochrome ASCII logo"""
    return f"""
  _            _                     _
 | |_ ___| | ___  ___ _ __   ___ | |_
 | __/ _ \\ |/ _ \\/ __| '_ \\ / _ \\| __|
 | ||  __/ |  __/\\__ \\ |_) | (_) | |_
  \\__\\___|_|\\___||___/ .__/ \\___/ \\__|
                     |_|         v{VERSION}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    """ANSI color codes"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'
    RAINBOW = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']


class ColorMode:
    """Manages color output modes"""
    def __init__(self, mode='normal'):
        self.mode = mode  # 'normal', 'colorful', 'off'
        self._rainbow_idx = 0

    def _get_rainbow(self):
        color = Colors.RAINBOW[self._rainbow_idx % len(Colors.RAINBOW)]
        self._rainbow_idx += 1
        return color

    def text(self, text, color_type='normal'):
        if self.mode == 'off':
            return text
        if self.mode == 'colorful':
            return f"{self._get_rainbow()}{text}{Colors.END}"
        # Normal mode
        colors = {
            'header': Colors.CYAN,
            'success': Colors.GREEN,
            'warning': Colors.YELLOW,
            'error': Colors.RED,
            'info': Colors.BLUE,
        }
        c = colors.get(color_type, '')
        return f"{c}{text}{Colors.END}" if c else text

    def header(self, text):
        return self.text(text, 'header')
    def success(self, text):
        return self.text(text, 'success')
    def warning(self, text):
        return self.text(text, 'warning')
    def error(self, text):
        return self.text(text, 'error')
    def info(self, text):
        return self.text(text, 'info')


color = ColorMode('normal')

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class Config:
    """Configuration manager"""

    DEFAULT = {
        'google_api_key': '',
        'google_cse_id': '',
        'bing_api_key': '',
        'dehashed_api_key': '',
        'default_country_code': '+1',
        'delay_seconds': '2',
    }

    def __init__(self):
        self.settings = dict(self.DEFAULT)
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.settings[key.strip()] = value.strip()
            except Exception as e:
                print(f"Warning: Could not load config: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                f.write("# telespot Configuration\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write("# Google Custom Search API\n")
                f.write(f"google_api_key={self.settings.get('google_api_key', '')}\n")
                f.write(f"google_cse_id={self.settings.get('google_cse_id', '')}\n\n")
                f.write("# Bing Search API (Azure)\n")
                f.write(f"bing_api_key={self.settings.get('bing_api_key', '')}\n\n")
                f.write("# Dehashed API (optional)\n")
                f.write(f"dehashed_api_key={self.settings.get('dehashed_api_key', '')}\n\n")
                f.write("# Settings\n")
                f.write(f"default_country_code={self.settings.get('default_country_code', '+1')}\n")
                f.write(f"delay_seconds={self.settings.get('delay_seconds', '2')}\n")
            os.chmod(CONFIG_FILE, 0o600)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

    def get_api_status(self):
        return {
            'Google': bool(self.settings.get('google_api_key') and self.settings.get('google_cse_id')),
            'Bing': bool(self.settings.get('bing_api_key')),
            'DuckDuckGo': True,  # Always available (no API key needed)
            'Dehashed': bool(self.settings.get('dehashed_api_key')),
        }

    def display_api_status(self):
        print(f"\n{color.header('API Configuration Status:')}")
        print("-" * 40)
        apis = self.get_api_status()
        for api, loaded in apis.items():
            status = "CONFIGURED" if loaded else "NOT CONFIGURED"
            symbol = "[+]" if loaded else "[-]"
            status_color = color.success(status) if loaded else color.warning(status)
            print(f"  {symbol} {api}: {status_color}")
        print("-" * 40)
        configured = sum(1 for v in apis.values() if v)
        print(f"  {configured}/{len(apis)} APIs configured\n")


config = Config()

# ═══════════════════════════════════════════════════════════════════════════════
# USER AGENT ROTATION
# ═══════════════════════════════════════════════════════════════════════════════

USER_AGENTS = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    # Chrome on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # Chrome on Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    # Safari
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    # Mobile
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
]


def get_random_headers():
    """Get request headers with random User-Agent"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
    }


def rate_limit():
    """Random rate limiting between 3-5 seconds"""
    delay = random.uniform(3.0, 5.0)
    time.sleep(delay)
    return delay

# ═══════════════════════════════════════════════════════════════════════════════
# US STATES AND LOCATION DATA
# ═══════════════════════════════════════════════════════════════════════════════

US_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
}

COUNTRY_CODES = {
    '+1': 'USA/Canada', '+44': 'United Kingdom', '+49': 'Germany',
    '+33': 'France', '+61': 'Australia', '+81': 'Japan',
    '+86': 'China', '+91': 'India', '+7': 'Russia',
    '+55': 'Brazil', '+52': 'Mexico', '+34': 'Spain',
}

DTMF_MAP = {
    '0': '0', '1': '1', '2': '2ABC', '3': '3DEF',
    '4': '4GHI', '5': '5JKL', '6': '6MNO',
    '7': '7PQRS', '8': '8TUV', '9': '9WXYZ',
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHONE NUMBER FORMATS (10 total: 4 basic + 4 quoted + 2 special)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_phone_formats(phone_number, country_code='+1'):
    """Generate 10 phone number format variations for searching"""
    digits = re.sub(r'\D', '', phone_number)

    if country_code == '+1':
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        if len(digits) != 10:
            return []
        area = digits[0:3]
        prefix = digits[3:6]
        line = digits[6:10]
    else:
        cc = country_code.lstrip('+')
        if len(digits) < 7:
            return []
        if len(digits) >= 10:
            area = digits[-10:-7]
            prefix = digits[-7:-4]
            line = digits[-4:]
        else:
            area = digits[:3] if len(digits) >= 3 else digits
            prefix = digits[3:6] if len(digits) >= 6 else ''
            line = digits[6:] if len(digits) > 6 else ''

    # 4 Basic formats
    basic = [
        f'{area}-{prefix}-{line}',                    # 215-555-1234
        f'{area}{prefix}{line}',                      # 2155551234
        f'({area}) {prefix}-{line}',                  # (215) 555-1234
        f'+1{area}-{prefix}-{line}',                  # +1215-555-1234
    ]

    # 4 Quoted formats (exact match)
    quoted = [
        f'"{area}-{prefix}-{line}"',                  # "215-555-1234"
        f'"{area}{prefix}{line}"',                    # "2155551234"
        f'"({area}) {prefix}-{line}"',                # "(215) 555-1234"
        f'"+1{area}-{prefix}-{line}"',                # "+1215-555-1234"
    ]

    # 2 Special formats
    special = [
        f'({area}-{prefix}-{line})',                  # (215-555-1234)
        f'"({area}) {prefix}-{line})"',               # "(215) 555-1234)"
    ]

    return basic + quoted + special


def get_dtmf_representation(phone_number):
    """Convert phone number to DTMF representation"""
    digits = re.sub(r'\D', '', phone_number)
    return ' '.join(DTMF_MAP.get(d, d) for d in digits)

# ═══════════════════════════════════════════════════════════════════════════════
# API SEARCH FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def search_google_api(query, api_key, cse_id, num_results=10, verbose=False, debug=False):
    """Search using Google Custom Search API"""
    results = []

    if not api_key or not cse_id:
        if debug:
            print("    [DEBUG] Google API not configured")
        return results

    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': query,
            'num': min(num_results, 10),
        }

        headers = get_random_headers()
        response = requests.get(url, params=params, headers=headers, timeout=15)

        if debug:
            print(f"    [DEBUG] Google API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Google'
                })
                if verbose:
                    print(f"      Found: {item.get('title', '')[:60]}...")
        elif response.status_code == 429:
            print(f"    {color.warning('Google API quota exceeded')}")
        elif debug:
            print(f"    [DEBUG] Google error: {response.text[:100]}")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] Google exception: {e}")

    return results


def search_bing_api(query, api_key, num_results=10, verbose=False, debug=False):
    """Search using Bing Search API (Azure Cognitive Services)"""
    results = []

    if not api_key:
        if debug:
            print("    [DEBUG] Bing API not configured")
        return results

    try:
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = get_random_headers()
        headers['Ocp-Apim-Subscription-Key'] = api_key
        params = {
            'q': query,
            'count': num_results,
            'mkt': 'en-US',
        }

        response = requests.get(url, headers=headers, params=params, timeout=15)

        if debug:
            print(f"    [DEBUG] Bing API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for item in data.get('webPages', {}).get('value', []):
                results.append({
                    'title': item.get('name', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Bing'
                })
                if verbose:
                    print(f"      Found: {item.get('name', '')[:60]}...")
        elif response.status_code == 401:
            print(f"    {color.warning('Bing API key invalid')}")
        elif response.status_code == 429:
            print(f"    {color.warning('Bing API quota exceeded')}")
        elif debug:
            print(f"    [DEBUG] Bing error: {response.text[:100]}")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] Bing exception: {e}")

    return results


def search_duckduckgo_api(query, num_results=10, verbose=False, debug=False):
    """Search using DuckDuckGo Instant Answer API"""
    results = []

    try:
        # DuckDuckGo Instant Answer API
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1,
        }

        headers = get_random_headers()
        response = requests.get(url, params=params, headers=headers, timeout=15)

        if debug:
            print(f"    [DEBUG] DuckDuckGo API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Abstract
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Result'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'source': 'DuckDuckGo'
                })
                if verbose:
                    print(f"      Found: {data.get('Heading', '')[:60]}...")

            # Related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '')[:80],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'DuckDuckGo'
                    })
                    if verbose:
                        print(f"      Found: {topic.get('Text', '')[:60]}...")

            # Results
            for item in data.get('Results', [])[:num_results]:
                results.append({
                    'title': item.get('Text', ''),
                    'url': item.get('FirstURL', ''),
                    'snippet': item.get('Text', ''),
                    'source': 'DuckDuckGo'
                })

    except Exception as e:
        if debug:
            print(f"    [DEBUG] DuckDuckGo exception: {e}")

    return results


def search_dehashed_api(query, api_key, verbose=False, debug=False):
    """Search Dehashed breach database (optional)"""
    results = []

    if not api_key:
        if debug:
            print("    [DEBUG] Dehashed API not configured")
        return results

    try:
        url = "https://api.dehashed.com/search"
        params = {'query': f'phone:"{query}"'}
        headers = get_random_headers()
        headers['Accept'] = 'application/json'
        auth = (api_key.split(':')[0], api_key.split(':')[1]) if ':' in api_key else (api_key, '')

        response = requests.get(url, params=params, headers=headers, auth=auth, timeout=15)

        if debug:
            print(f"    [DEBUG] Dehashed API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for entry in data.get('entries', [])[:10]:
                name = f"{entry.get('name', '')} {entry.get('username', '')}".strip()
                results.append({
                    'title': name or 'Dehashed Entry',
                    'url': entry.get('database_name', ''),
                    'snippet': f"Email: {entry.get('email', 'N/A')} | Database: {entry.get('database_name', 'N/A')}",
                    'source': 'Dehashed'
                })
                if verbose:
                    print(f"      Found: {name[:60]}...")
        elif response.status_code == 401:
            print(f"    {color.warning('Dehashed API key invalid')}")
        elif debug:
            print(f"    [DEBUG] Dehashed error: {response.text[:100]}")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] Dehashed exception: {e}")

    return results

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

def extract_names(text):
    """Extract potential names from text"""
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    names = re.findall(name_pattern, text)

    excluded = {
        'Phone', 'Number', 'Call', 'Contact', 'Email', 'Address',
        'Street', 'City', 'State', 'Country', 'The', 'This', 'That',
        'Search', 'Results', 'View', 'More', 'Less', 'Show', 'Hide',
        'United States', 'New York', 'Los Angeles', 'San Francisco',
        'Google', 'Bing', 'Yahoo', 'Facebook', 'Twitter', 'Instagram',
        'Best', 'Top', 'Free', 'Online', 'Reviews', 'About', 'Home',
        'Business', 'Service', 'Services', 'Company', 'Companies',
        'True People', 'White Pages', 'Fast People', 'People Search',
        'Phone Number', 'Reverse Phone', 'Phone Lookup', 'Cell Phone',
    }

    return [n for n in names if n not in excluded and len(n.split()) >= 2]


def extract_locations(text):
    """Extract potential locations from text"""
    locations = []

    # State abbreviations
    state_pattern = r'\b(' + '|'.join(US_STATES.keys()) + r')\b'
    locations.extend(re.findall(state_pattern, text))

    # City, State combinations
    city_state_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+(' + '|'.join(US_STATES.keys()) + r')\b'
    for city, state in re.findall(city_state_pattern, text):
        locations.append(f"{city}, {state}")

    # Full state names
    for abbr, full_name in US_STATES.items():
        if full_name in text:
            locations.append(full_name)

    # Zip codes
    locations.extend(re.findall(r'\b\d{5}(?:-\d{4})?\b', text))

    return list(set(locations))


def extract_usernames(text):
    """Extract potential usernames from text and URLs"""
    usernames = []

    # @username pattern
    usernames.extend(re.findall(r'@([A-Za-z0-9_]{3,20})', text))

    # URL path usernames (e.g., facebook.com/username)
    url_pattern = r'(?:facebook|twitter|instagram|linkedin)\.com/([A-Za-z0-9_.-]{3,30})'
    usernames.extend(re.findall(url_pattern, text, re.IGNORECASE))

    excluded = {'search', 'profile', 'user', 'pages', 'groups', 'photos', 'videos'}
    return list(set(u for u in usernames if u.lower() not in excluded))


def analyze_results(all_results, verbose=False):
    """Analyze all results for patterns"""
    all_text = []
    source_counts = Counter()

    for format_str, results in all_results.items():
        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')} {result.get('url', '')}"
            all_text.append(text)
            source_counts[result.get('source', 'Unknown')] += 1

    combined_text = ' '.join(all_text)

    names = extract_names(combined_text)
    name_counter = Counter(names)

    locations = extract_locations(combined_text)
    location_counter = Counter(locations)

    usernames = extract_usernames(combined_text)
    username_counter = Counter(usernames)

    # Calculate confidence score
    total = len(all_text)
    name_consistency = len([n for n, c in name_counter.items() if c >= 2])
    location_consistency = len([l for l, c in location_counter.items() if c >= 2])

    if total >= 20 and name_consistency >= 2:
        confidence = 'HIGH'
        confidence_pct = min(100, 60 + name_consistency * 10 + location_consistency * 5)
    elif total >= 10 or name_consistency >= 1:
        confidence = 'MEDIUM'
        confidence_pct = min(74, 40 + total + name_consistency * 5)
    else:
        confidence = 'LOW'
        confidence_pct = min(39, total * 3)

    return {
        'total_results': total,
        'unique_urls': len(set(r.get('url', '') for results in all_results.values() for r in results)),
        'results_by_source': dict(source_counts),
        'names': name_counter.most_common(10),
        'locations': location_counter.most_common(10),
        'usernames': username_counter.most_common(10),
        'confidence': confidence,
        'confidence_pct': confidence_pct,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def print_results(patterns, phone_number, all_results, verbose=False):
    """Print formatted results"""
    print(f"\n{'='*70}")
    print(color.header("PATTERN ANALYSIS SUMMARY"))
    print(f"{'='*70}\n")

    # Confidence
    conf_color = color.success if patterns['confidence'] == 'HIGH' else (
        color.warning if patterns['confidence'] == 'MEDIUM' else color.error)
    conf_text = f"{patterns['confidence']} ({patterns['confidence_pct']}%)"
    print(f"Confidence Score: {conf_color(conf_text)}\n")

    print(f"Total Results Found: {patterns['total_results']}")
    print(f"Unique URLs: {patterns['unique_urls']}\n")

    # Source breakdown
    if patterns['results_by_source']:
        print(color.header("Results by Source:"))
        for source, count in sorted(patterns['results_by_source'].items(), key=lambda x: -x[1]):
            print(f"  • {source}: {count} results")
        print()

    # Names
    if patterns['names']:
        print(color.header("Names Found:"))
        for name, count in patterns['names']:
            indicator = " ⭐" if count >= 2 else ""
            print(f"  • {name}: mentioned {count} time(s){indicator}")
        print()

    # Locations
    if patterns['locations']:
        print(color.header("Locations Mentioned:"))
        for location, count in patterns['locations']:
            indicator = " ⭐" if count >= 2 else ""
            print(f"  • {location}: {count} occurrence(s){indicator}")
        print()

    # Usernames
    if patterns['usernames']:
        print(color.header("Usernames Found:"))
        for username, count in patterns['usernames']:
            indicator = " ⭐" if count >= 2 else ""
            print(f"  • @{username}: {count} occurrence(s){indicator}")
        print()

    # Key insights
    print(color.header("Key Insights:"))
    if patterns['names']:
        print(f"  • Most associated name: {color.success(patterns['names'][0][0])}")
    if patterns['locations']:
        print(f"  • Most associated location: {color.success(patterns['locations'][0][0])}")
    if not patterns['names'] and not patterns['locations']:
        print(f"  • {color.warning('No clear patterns found in results')}")

    print(f"\n{'='*70}\n")

    # Verbose: show all listings
    if verbose and all_results:
        print(color.header("VERBOSE RESULTS - ALL LISTINGS"))
        print(f"{'='*70}\n")

        for fmt, results in all_results.items():
            if results:
                print(f"Format: {fmt}")
                print("-" * 70)
                for i, r in enumerate(results, 1):
                    print(f"\n[{i}] {r.get('title', 'N/A')}")
                    print(f"    URL: {r.get('url', 'N/A')}")
                    print(f"    Source: {r.get('source', 'N/A')}")
                    if r.get('snippet'):
                        print(f"    Description: {r.get('snippet', '')[:200]}...")
                print()


def save_json_results(phone_number, formats, all_results, patterns, filename=None):
    """Save results to JSON file"""
    if not filename:
        clean_phone = re.sub(r'\D', '', phone_number)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"telespot_{clean_phone}_{timestamp}.json"

    output = {
        'version': VERSION,
        'timestamp': datetime.now().isoformat(),
        'phone_number': phone_number,
        'search_formats': formats,
        'patterns': patterns,
        'results': {fmt: results for fmt, results in all_results.items()},
    }

    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    return filename


def save_txt_results(phone_number, formats, all_results, patterns, filename=None):
    """Save results to TXT file"""
    if not filename:
        clean_phone = re.sub(r'\D', '', phone_number)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"telespot_{clean_phone}_{timestamp}.txt"

    with open(filename, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("TELESPOT SEARCH RESULTS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Phone Number: {phone_number}\n")
        f.write(f"Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Confidence Score: {patterns['confidence']} ({patterns['confidence_pct']}%)\n\n")

        f.write("=" * 70 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total Results: {patterns['total_results']}\n")
        f.write(f"Unique URLs: {patterns['unique_urls']}\n\n")

        f.write("Results by Source:\n")
        for source, count in patterns['results_by_source'].items():
            f.write(f"  - {source}: {count} results\n")
        f.write("\n")

        if patterns['names']:
            f.write("Names Found:\n")
            for name, count in patterns['names']:
                f.write(f"  - {name}: {count} mention(s)\n")
            f.write("\n")

        if patterns['locations']:
            f.write("Locations Mentioned:\n")
            for loc, count in patterns['locations']:
                f.write(f"  - {loc}: {count} occurrence(s)\n")
            f.write("\n")

        if patterns['usernames']:
            f.write("Usernames Found:\n")
            for user, count in patterns['usernames']:
                f.write(f"  - @{user}: {count} occurrence(s)\n")
            f.write("\n")

        f.write("=" * 70 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 70 + "\n\n")

        for fmt, results in all_results.items():
            if results:
                f.write(f"Format: {fmt}\n")
                f.write("-" * 70 + "\n\n")
                for i, r in enumerate(results, 1):
                    f.write(f"[{i}] {r.get('title', 'N/A')}\n")
                    f.write(f"URL: {r.get('url', 'N/A')}\n")
                    f.write(f"Source: {r.get('source', 'N/A')}\n")
                    if r.get('snippet'):
                        f.write(f"Description: {r.get('snippet', '')}\n")
                    f.write("\n")

    return filename

# ═══════════════════════════════════════════════════════════════════════════════
# INTERACTIVE SETUP
# ═══════════════════════════════════════════════════════════════════════════════

def interactive_setup():
    """Interactive API key setup"""
    print(color.header("\n" + "=" * 60))
    print(color.header("TELESPOT API CONFIGURATION"))
    print(color.header("=" * 60))
    print("\nThis will configure your API keys for searching.")
    print("Press Enter to skip any API you don't want to configure.\n")

    # Google
    print(color.info("Google Custom Search API"))
    print("  Get keys at: https://console.cloud.google.com/")
    print("  1. Enable 'Custom Search API'")
    print("  2. Create credentials (API Key)")
    print("  3. Create a Custom Search Engine at https://cse.google.com/")

    current_key = config.get('google_api_key', '')
    masked = f"[{current_key[:8]}...]" if len(current_key) > 8 else "[not set]"
    print(f"\n  Current API Key: {masked}")
    key = input("  Enter Google API Key (or Enter to skip): ").strip()
    if key:
        config.set('google_api_key', key)

    current_cse = config.get('google_cse_id', '')
    masked = f"[{current_cse[:8]}...]" if len(current_cse) > 8 else "[not set]"
    print(f"  Current CSE ID: {masked}")
    cse = input("  Enter Google CSE ID (or Enter to skip): ").strip()
    if cse:
        config.set('google_cse_id', cse)

    # Bing
    print(color.info("\nBing Search API (Azure Cognitive Services)"))
    print("  Get key at: https://portal.azure.com/")
    print("  1. Create 'Bing Search v7' resource")
    print("  2. Copy the API key")

    current_bing = config.get('bing_api_key', '')
    masked = f"[{current_bing[:8]}...]" if len(current_bing) > 8 else "[not set]"
    print(f"\n  Current Bing Key: {masked}")
    bing = input("  Enter Bing API Key (or Enter to skip): ").strip()
    if bing:
        config.set('bing_api_key', bing)

    # Dehashed
    print(color.info("\nDehashed API (optional - for breach database search)"))
    print("  Get key at: https://www.dehashed.com/")
    print("  Format: email:api_key")

    current_dh = config.get('dehashed_api_key', '')
    masked = f"[{current_dh[:8]}...]" if len(current_dh) > 8 else "[not set]"
    print(f"\n  Current Dehashed Key: {masked}")
    dh = input("  Enter Dehashed API Key (or Enter to skip): ").strip()
    if dh:
        config.set('dehashed_api_key', dh)

    # Country code
    print(color.info("\nDefault Country Code"))
    print(f"  Current: {config.get('default_country_code', '+1')}")
    cc = input("  Enter country code (e.g., +1, +44) or Enter to keep: ").strip()
    if cc:
        if not cc.startswith('+'):
            cc = '+' + cc
        config.set('default_country_code', cc)

    # Save
    if config.save():
        print(color.success("\nConfiguration saved successfully!"))
    else:
        print(color.error("\nFailed to save configuration."))

    config.display_api_status()

# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def update_from_repo():
    """Update telespot from the repository"""
    print(color.header("\nUpdating telespot from repository..."))

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        git_dir = os.path.join(script_dir, '.git')

        if os.path.exists(git_dir):
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=script_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(color.success("Update successful!"))
                print(result.stdout)
                return True
            else:
                print(f"Update failed: {result.stderr}")
                return False
        else:
            print("Not a git repository. Please run:")
            print(f"  git clone {REPO_URL}")
            return False

    except Exception as e:
        print(f"Update error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SEARCH FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def run_search(phone_number, args):
    """Main search orchestration"""
    global color

    # Set color mode
    if args.no_color:
        color = ColorMode('off')
    elif args.colorful:
        color = ColorMode('colorful')
    else:
        color = ColorMode('normal')

    # Get country code
    country_code = args.country or config.get('default_country_code', '+1')

    # Generate formats
    formats = generate_phone_formats(phone_number, country_code)
    if not formats:
        print(color.error("Invalid phone number format. Please enter a valid 10-digit number."))
        return None

    print(f"\nSearching for: {color.header(phone_number)}")
    print(f"Country code: {country_code}")
    print(f"Using {len(formats)} format variations\n")

    # Show API status
    config.display_api_status()

    # DTMF display
    if args.dtmf:
        dtmf = get_dtmf_representation(phone_number)
        print(f"DTMF: {dtmf}\n")

    # Get API keys
    google_key = config.get('google_api_key', '')
    google_cse = config.get('google_cse_id', '')
    bing_key = config.get('bing_api_key', '')
    dehashed_key = config.get('dehashed_api_key', '')
    delay = int(config.get('delay_seconds', '2'))

    all_results = {}
    total_found = 0

    # Keyword addition
    keyword_suffix = f" {args.keyword}" if args.keyword else ""

    # Site restriction
    site_prefix = f"site:{args.site} " if args.site else ""

    for i, fmt in enumerate(formats, 1):
        query = f"{site_prefix}{fmt}{keyword_suffix}"
        print(f"{color.header(f'[{i}/{len(formats)}]')} Searching: {fmt}")

        format_results = []

        # Google API
        if google_key and google_cse:
            print(f"  → Google API...", end=' ', flush=True)
            results = search_google_api(query, google_key, google_cse, 10, args.verbose, args.debug)
            format_results.extend(results)
            print(f"({len(results)} results)")
            time.sleep(1)

        # Bing API
        if bing_key:
            print(f"  → Bing API...", end=' ', flush=True)
            results = search_bing_api(query, bing_key, 10, args.verbose, args.debug)
            format_results.extend(results)
            print(f"({len(results)} results)")
            time.sleep(1)

        # DuckDuckGo (always available)
        print(f"  → DuckDuckGo...", end=' ', flush=True)
        results = search_duckduckgo_api(query, 10, args.verbose, args.debug)
        format_results.extend(results)
        print(f"({len(results)} results)")

        # Dehashed (optional)
        if dehashed_key and args.dehashed:
            print(f"  → Dehashed...", end=' ', flush=True)
            clean_query = re.sub(r'\D', '', fmt)
            results = search_dehashed_api(clean_query, dehashed_key, args.verbose, args.debug)
            format_results.extend(results)
            print(f"({len(results)} results)")

        all_results[fmt] = format_results
        total_found += len(format_results)

        print(f"  {color.success(f'✓ {len(format_results)} total for this format')}")

        # Rate limiting (random 3-5 seconds)
        if i < len(formats):
            delay_time = rate_limit()
            print(f"  {color.warning(f'⏳ Waited {delay_time:.1f} seconds')}\n")
        else:
            print()

    print(f"\n{color.header(f'Total Results: {total_found}')}\n")

    # Analyze
    print("Analyzing patterns...")
    patterns = analyze_results(all_results, args.verbose)

    # Print results
    print_results(patterns, phone_number, all_results, args.verbose)

    # Summary comparison
    if args.summary:
        print(color.header("SUMMARY COMPARISON"))
        print("=" * 70)
        print("\nItems appearing in multiple results (higher confidence):\n")

        for name, count in patterns['names']:
            if count >= 2:
                bar = "█" * min(count, 20)
                print(f"  NAME     | {bar} | {name} ({count}x)")

        for loc, count in patterns['locations']:
            if count >= 2:
                bar = "█" * min(count, 20)
                print(f"  LOCATION | {bar} | {loc} ({count}x)")

        for user, count in patterns['usernames']:
            if count >= 2:
                bar = "█" * min(count, 20)
                print(f"  USERNAME | {bar} | @{user} ({count}x)")
        print()

    # Save to file
    if args.output:
        if args.output.endswith('.json'):
            filename = save_json_results(phone_number, formats, all_results, patterns, args.output)
        else:
            filename = save_txt_results(phone_number, formats, all_results, patterns, args.output)
        print(color.success(f"Results saved to: {filename}"))

    return {
        'phone_number': phone_number,
        'formats': formats,
        'results': all_results,
        'patterns': patterns,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='telespot',
        description=f'''
╔══════════════════════════════════════════════════════════════════╗
║  telespot v{VERSION} - Phone Number OSINT Tool                     ║
╠══════════════════════════════════════════════════════════════════╣
║  API-based search across Google, Bing, and DuckDuckGo with      ║
║  pattern recognition for names, locations, and usernames.        ║
╚══════════════════════════════════════════════════════════════════╝
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
EXAMPLES:
  telespot 2155551234                    Basic search
  telespot 2155551234 -k "John Smith"    Search with keywords
  telespot 2155551234 -s whitepages.com  Search specific site
  telespot 2155551234 --dehashed         Include breach database
  telespot 2155551234 -v -o results.json Verbose + JSON output
  telespot --setup                       Configure API keys

API SETUP:
  Run 'telespot --setup' to configure your API keys.
  At minimum, configure Google or Bing for best results.
  DuckDuckGo works without an API key.

SEARCH ENGINES:
  • Google Custom Search API (requires API key + CSE ID)
  • Bing Search API (requires Azure API key)
  • DuckDuckGo Instant Answer API (no key required)
  • Dehashed (optional, requires API key)

For more information: https://github.com/thumpersecure/Telespot
''')

    parser.add_argument('phone', nargs='?', help='Phone number to search')

    search = parser.add_argument_group('Search Options')
    search.add_argument('-k', '--keyword', metavar='WORD', help='Add keyword to search')
    search.add_argument('-s', '--site', metavar='DOMAIN', help='Limit search to specific site')
    search.add_argument('-c', '--country', metavar='CODE', help='Country code (default: +1)')
    search.add_argument('--dehashed', action='store_true', help='Include Dehashed breach search')

    output = parser.add_argument_group('Output Options')
    output.add_argument('-o', '--output', metavar='FILE', help='Save results to file (.json or .txt)')
    output.add_argument('-v', '--verbose', action='store_true', help='Show detailed listings')
    output.add_argument('--summary', action='store_true', help='Show comparison summary')
    output.add_argument('--dtmf', action='store_true', help='Show DTMF representation')

    display = parser.add_argument_group('Display Options')
    display.add_argument('--colorful', action='store_true', help='Enable rainbow colors')
    display.add_argument('--no-color', action='store_true', help='Disable colors')

    config_grp = parser.add_argument_group('Configuration')
    config_grp.add_argument('--setup', action='store_true', help='Configure API keys')
    config_grp.add_argument('--api-status', action='store_true', help='Show API status')

    maint = parser.add_argument_group('Maintenance')
    maint.add_argument('--update', action='store_true', help='Update from repository')
    maint.add_argument('--version', action='version', version=f'telespot v{VERSION}')

    debug = parser.add_argument_group('Debug')
    debug.add_argument('-d', '--debug', action='store_true', help='Enable debug output')

    return parser

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    global color

    parser = create_parser()
    args = parser.parse_args()

    # Set color mode
    if args.no_color:
        color = ColorMode('off')
    elif args.colorful:
        color = ColorMode('colorful')
    else:
        color = ColorMode('normal')

    # Print logo
    if not args.no_color:
        print(get_ascii_logo())
    else:
        print(get_ascii_logo_mono())

    # Handle commands
    if args.setup:
        interactive_setup()
        return 0

    if args.api_status:
        config.display_api_status()
        return 0

    if args.update:
        update_from_repo()
        return 0

    # Get phone number
    phone_number = args.phone

    if not phone_number:
        # Interactive mode
        print("Enter phone number to search.")
        print(f"Default country code: {config.get('default_country_code', '+1')}")

        use_intl = input("\nUse international number? (y/N): ").strip().lower()
        if use_intl == 'y':
            print("\nCommon country codes:")
            for code, country in list(COUNTRY_CODES.items())[:6]:
                print(f"  {code}: {country}")
            args.country = input("\nEnter country code: ").strip()
            if args.country and not args.country.startswith('+'):
                args.country = '+' + args.country

        phone_number = input("\nPhone number: ").strip()

        if not phone_number:
            print(color.error("No phone number provided."))
            parser.print_help()
            return 1

    # Run search
    try:
        result = run_search(phone_number, args)

        if result and not args.output:
            save = input("\nSave results to file? (y/N): ").strip().lower()
            if save == 'y':
                fmt = input("Format (txt/json) [txt]: ").strip().lower() or 'txt'
                if fmt == 'json':
                    filename = save_json_results(
                        phone_number, result['formats'],
                        result['results'], result['patterns']
                    )
                else:
                    filename = save_txt_results(
                        phone_number, result['formats'],
                        result['results'], result['patterns']
                    )
                print(color.success(f"Results saved to: {filename}"))

        return 0

    except KeyboardInterrupt:
        print(color.warning("\n\nSearch interrupted by user."))
        return 130


if __name__ == "__main__":
    sys.exit(main())
