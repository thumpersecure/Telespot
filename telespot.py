#!/usr/bin/env python3
"""
telespot - Multi-Engine Phone Number OSINT Tool
Version 5.0-beta

Searches for phone numbers across 10 search engines with intelligent
pattern analysis for names, locations, and business associations.
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

# Optional imports with graceful fallback
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

VERSION = "5.0-beta"
REPO_URL = "https://github.com/thumpersecure/Telespot"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.txt")

# ═══════════════════════════════════════════════════════════════════════════════
# ASCII LOGO - lowercase telespot with blue/red twinkle on white
# ═══════════════════════════════════════════════════════════════════════════════

def get_ascii_logo():
    """Returns the ASCII logo with blue/red twinkle effect on white"""
    # Color codes
    W = '\033[97m'   # Bright white
    B = '\033[94m'   # Blue
    R = '\033[91m'   # Red
    E = '\033[0m'    # End/reset

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
    """ANSI color codes for terminal output"""
    # Base colors
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    # Rainbow sequence
    RAINBOW = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']

    # Monotone (grayscale)
    MONO_LIGHT = '\033[37m'
    MONO_DARK = '\033[90m'


class ColorMode:
    """Manages color output modes"""
    def __init__(self, mode='mono'):
        self.mode = mode  # 'mono', 'colorful', 'off'
        self._rainbow_idx = 0

    def _get_rainbow(self):
        """Get next rainbow color"""
        color = Colors.RAINBOW[self._rainbow_idx % len(Colors.RAINBOW)]
        self._rainbow_idx += 1
        return color

    def text(self, text, color_type='normal'):
        """Apply color based on mode"""
        if self.mode == 'off':
            return text

        if self.mode == 'colorful':
            # Rainbow mode - each call gets next rainbow color
            return f"{self._get_rainbow()}{text}{Colors.END}"

        # Monotone mode - use grayscale
        if color_type == 'header':
            return f"{Colors.WHITE}{Colors.BOLD}{text}{Colors.END}"
        elif color_type == 'success':
            return f"{Colors.MONO_LIGHT}{text}{Colors.END}"
        elif color_type == 'warning':
            return f"{Colors.MONO_DARK}{text}{Colors.END}"
        elif color_type == 'error':
            return f"{Colors.WHITE}{text}{Colors.END}"
        elif color_type == 'info':
            return f"{Colors.MONO_LIGHT}{text}{Colors.END}"
        else:
            return f"{Colors.MONO_LIGHT}{text}{Colors.END}"

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


# Global color mode instance
color = ColorMode('mono')

# ═══════════════════════════════════════════════════════════════════════════════
# USER AGENT ROTATION
# ═══════════════════════════════════════════════════════════════════════════════

USER_AGENTS = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    # Chrome on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # Chrome on Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
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
    """Generate random request headers with rotating User-Agent"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }


def rate_limit():
    """Random rate limiting between 3-5 seconds"""
    delay = random.uniform(3.0, 5.0)
    time.sleep(delay)
    return delay

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class Config:
    """Configuration manager for API keys and settings"""

    DEFAULT_CONFIG = {
        'numverify_api_key': '',
        'abstract_api_key': '',
        'twilio_account_sid': '',
        'twilio_auth_token': '',
        'opencnam_account_sid': '',
        'opencnam_auth_token': '',
        'telnyx_api_key': '',
        'default_country_code': '+1',
        'rate_limit_min': '3',
        'rate_limit_max': '5',
        'default_output_format': 'text',
        'verbose': 'false',
        'colorful_mode': 'false',
    }

    def __init__(self, config_path=CONFIG_FILE):
        self.config_path = config_path
        self.settings = dict(self.DEFAULT_CONFIG)
        self.load()

    def load(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            self.settings[key.strip()] = value.strip()
            except Exception as e:
                print(f"Warning: Could not load config: {e}")

    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                f.write("# telespot Configuration File\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

                f.write("# API Keys\n")
                for key in ['numverify_api_key', 'abstract_api_key', 'twilio_account_sid',
                           'twilio_auth_token', 'opencnam_account_sid', 'opencnam_auth_token',
                           'telnyx_api_key']:
                    f.write(f"{key}={self.settings.get(key, '')}\n")

                f.write("\n# Settings\n")
                for key in ['default_country_code', 'rate_limit_min', 'rate_limit_max',
                           'default_output_format', 'verbose', 'colorful_mode']:
                    f.write(f"{key}={self.settings.get(key, '')}\n")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

    def get_api_status(self):
        """Return status of all APIs (loaded/unloaded)"""
        apis = {
            'NumVerify': bool(self.settings.get('numverify_api_key')),
            'AbstractAPI': bool(self.settings.get('abstract_api_key')),
            'Twilio': bool(self.settings.get('twilio_account_sid') and self.settings.get('twilio_auth_token')),
            'OpenCNAM': bool(self.settings.get('opencnam_account_sid') and self.settings.get('opencnam_auth_token')),
            'Telnyx': bool(self.settings.get('telnyx_api_key')),
        }
        return apis

    def display_api_status(self):
        """Display API configuration status"""
        print(f"\n{color.header('API Configuration Status:')}")
        print("-" * 40)
        apis = self.get_api_status()
        for api, loaded in apis.items():
            status = "LOADED" if loaded else "NOT CONFIGURED"
            symbol = "[+]" if loaded else "[-]"
            print(f"  {symbol} {api}: {status}")
        print("-" * 40)
        loaded_count = sum(1 for v in apis.values() if v)
        print(f"  {loaded_count}/{len(apis)} APIs configured\n")


# Global config instance
config = Config()

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

# International country codes
COUNTRY_CODES = {
    '+1': 'USA/Canada',
    '+44': 'United Kingdom',
    '+49': 'Germany',
    '+33': 'France',
    '+61': 'Australia',
    '+81': 'Japan',
    '+86': 'China',
    '+91': 'India',
    '+7': 'Russia',
    '+55': 'Brazil',
    '+52': 'Mexico',
    '+34': 'Spain',
    '+39': 'Italy',
    '+31': 'Netherlands',
    '+46': 'Sweden',
    '+47': 'Norway',
    '+45': 'Denmark',
    '+358': 'Finland',
    '+353': 'Ireland',
    '+41': 'Switzerland',
    '+43': 'Austria',
    '+48': 'Poland',
    '+420': 'Czech Republic',
    '+36': 'Hungary',
    '+30': 'Greece',
    '+90': 'Turkey',
    '+972': 'Israel',
    '+971': 'UAE',
    '+966': 'Saudi Arabia',
    '+65': 'Singapore',
    '+82': 'South Korea',
    '+64': 'New Zealand',
    '+27': 'South Africa',
    '+234': 'Nigeria',
    '+20': 'Egypt',
    '+63': 'Philippines',
    '+62': 'Indonesia',
    '+60': 'Malaysia',
    '+66': 'Thailand',
    '+84': 'Vietnam',
}

# DTMF tones mapping
DTMF_MAP = {
    '0': '0', '1': '1', '2': '2ABC', '3': '3DEF',
    '4': '4GHI', '5': '5JKL', '6': '6MNO',
    '7': '7PQRS', '8': '8TUV', '9': '9WXYZ',
    '*': '*', '#': '#'
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHONE NUMBER FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def generate_phone_formats(phone_number, country_code='+1'):
    """Generate various phone number formats for searching"""
    digits = re.sub(r'\D', '', phone_number)

    # Handle country code in input
    if country_code == '+1':
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        if len(digits) != 10:
            return []
        area = digits[0:3]
        prefix = digits[3:6]
        line = digits[6:10]
        cc = '1'
    else:
        # International numbers - more flexible
        cc = country_code.lstrip('+')
        if len(digits) < 7:
            return []
        # Use last 10 digits if available, otherwise use what we have
        if len(digits) >= 10:
            area = digits[-10:-7]
            prefix = digits[-7:-4]
            line = digits[-4:]
        else:
            area = digits[:3] if len(digits) >= 3 else digits
            prefix = digits[3:6] if len(digits) >= 6 else ''
            line = digits[6:] if len(digits) > 6 else ''

    formats = [
        f'+{cc}{area}{prefix}{line}',
        f'"+{cc}{area}{prefix}{line}"',
        f'({area}) {prefix}-{line}',
        f'"{cc} ({area}) {prefix}-{line}"',
        f'"{area}-{prefix}-{line}"',
        f'{area}-{prefix}-{line}',
        f'{area}.{prefix}.{line}',
        f'{area}{prefix}{line}',
        f'"{area}{prefix}{line}"',
        f'{area} {prefix} {line}',
    ]

    return formats


def get_dtmf_representation(phone_number):
    """Convert phone number to DTMF representation"""
    digits = re.sub(r'\D', '', phone_number)
    dtmf = []
    for d in digits:
        if d in DTMF_MAP:
            dtmf.append(DTMF_MAP[d])
    return ' '.join(dtmf)

# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH ENGINES (10 Total)
# ═══════════════════════════════════════════════════════════════════════════════

def search_google(query, verbose=False, debug=False):
    """Search Google"""
    results = []
    try:
        url = f'https://www.google.com/search?q={quote_plus(query)}&num=15'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] Google status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for g in soup.find_all('div', class_='g'):
                title_elem = g.find('h3')
                title = title_elem.get_text() if title_elem else ''

                link_elem = g.find('a')
                url_found = link_elem.get('href', '') if link_elem else ''

                snippet_elem = g.find('div', class_=['VwiC3b', 'yXK7lf', 'MUxGbd'])
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'Google'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Google error: {e}")
    return results


def search_bing(query, verbose=False, debug=False):
    """Search Bing"""
    results = []
    try:
        url = f'https://www.bing.com/search?q={quote_plus(query)}&count=15'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] Bing status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('li', class_='b_algo'):
                title_elem = item.find('h2')
                title = title_elem.get_text() if title_elem else ''

                link_elem = item.find('a')
                url_found = link_elem.get('href', '') if link_elem else ''

                snippet_elem = item.find('p')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'Bing'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Bing error: {e}")
    return results


def search_duckduckgo(query, verbose=False, debug=False):
    """Search DuckDuckGo"""
    results = []
    try:
        url = f'https://html.duckduckgo.com/html/?q={quote_plus(query)}'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] DuckDuckGo status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for result in soup.find_all('div', class_='result')[:15]:
                title_elem = result.find('a', class_='result__a')
                title = title_elem.get_text() if title_elem else ''
                url_found = title_elem.get('href', '') if title_elem else ''

                snippet_elem = result.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'DuckDuckGo'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] DuckDuckGo error: {e}")
    return results


def search_yahoo(query, verbose=False, debug=False):
    """Search Yahoo"""
    results = []
    try:
        url = f'https://search.yahoo.com/search?p={quote_plus(query)}&n=15'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] Yahoo status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('div', class_=['dd', 'algo'])[:15]:
                title_elem = item.find('h3') or item.find('a')
                title = title_elem.get_text() if title_elem else ''

                link_elem = item.find('a')
                url_found = link_elem.get('href', '') if link_elem else ''

                snippet_elem = item.find('p') or item.find('span', class_='fc-falcon')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'Yahoo'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Yahoo error: {e}")
    return results


def search_ask(query, verbose=False, debug=False):
    """Search Ask.com"""
    results = []
    try:
        url = f'https://www.ask.com/web?q={quote_plus(query)}'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] Ask status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('div', class_=['PartialSearchResults-item', 'result'])[:15]:
                title_elem = item.find('a', class_='PartialSearchResults-item-title-link') or item.find('a')
                title = title_elem.get_text() if title_elem else ''
                url_found = title_elem.get('href', '') if title_elem else ''

                snippet_elem = item.find('p', class_='PartialSearchResults-item-abstract') or item.find('p')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'Ask'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Ask error: {e}")
    return results


def search_aol(query, verbose=False, debug=False):
    """Search AOL"""
    results = []
    try:
        url = f'https://search.aol.com/aol/search?q={quote_plus(query)}'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] AOL status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all(['div', 'li'], class_=['dd', 'algo', 'ov-a'])[:15]:
                title_elem = item.find('h3') or item.find('a')
                title = title_elem.get_text() if title_elem else ''

                link_elem = item.find('a')
                url_found = link_elem.get('href', '') if link_elem else ''

                snippet_elem = item.find('p')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'AOL'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] AOL error: {e}")
    return results


def search_ecosia(query, verbose=False, debug=False):
    """Search Ecosia"""
    results = []
    try:
        url = f'https://www.ecosia.org/search?method=index&q={quote_plus(query)}'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] Ecosia status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('div', class_=['result', 'result__body'])[:15]:
                title_elem = item.find('a', class_='result-title') or item.find('h2') or item.find('a')
                title = title_elem.get_text() if title_elem else ''
                url_found = title_elem.get('href', '') if title_elem else ''

                snippet_elem = item.find('p', class_='result-snippet') or item.find('p')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'Ecosia'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Ecosia error: {e}")
    return results


def search_startpage(query, verbose=False, debug=False):
    """Search Startpage"""
    results = []
    try:
        url = f'https://www.startpage.com/do/search?query={quote_plus(query)}'
        headers = get_random_headers()
        headers['Accept'] = 'text/html'
        response = requests.get(url, headers=headers, timeout=15)

        if debug:
            print(f"    [DEBUG] Startpage status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('div', class_=['w-gl__result', 'result'])[:15]:
                title_elem = item.find('a', class_='w-gl__result-title') or item.find('h3') or item.find('a')
                title = title_elem.get_text() if title_elem else ''
                url_found = title_elem.get('href', '') if title_elem else ''

                snippet_elem = item.find('p', class_='w-gl__description') or item.find('p')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'Startpage'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Startpage error: {e}")
    return results


def search_qwant(query, verbose=False, debug=False):
    """Search Qwant"""
    results = []
    try:
        url = f'https://www.qwant.com/?q={quote_plus(query)}&t=web'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] Qwant status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all(['div', 'article'], class_=['result', 'web-result'])[:15]:
                title_elem = item.find('a') or item.find('h2')
                title = title_elem.get_text() if title_elem else ''
                url_found = title_elem.get('href', '') if title_elem else ''

                snippet_elem = item.find('p') or item.find('span')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'Qwant'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Qwant error: {e}")
    return results


def search_brave(query, verbose=False, debug=False):
    """Search Brave"""
    results = []
    try:
        url = f'https://search.brave.com/search?q={quote_plus(query)}'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] Brave status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('div', class_=['snippet', 'result'])[:15]:
                title_elem = item.find('a', class_='result-header') or item.find('a') or item.find('h2')
                title = title_elem.get_text() if title_elem else ''
                url_found = title_elem.get('href', '') if title_elem else ''

                snippet_elem = item.find('p', class_=['snippet-description']) or item.find('p')
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': 'Brave'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Brave error: {e}")
    return results


# Site-specific searches
def search_site(query, site, verbose=False, debug=False):
    """Search a specific site via Google"""
    results = []
    try:
        site_query = f'site:{site} {query}'
        url = f'https://www.google.com/search?q={quote_plus(site_query)}&num=10'
        response = requests.get(url, headers=get_random_headers(), timeout=15)

        if debug:
            print(f"    [DEBUG] Site search ({site}) status: {response.status_code}")

        if response.status_code == 200 and BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, 'html.parser')
            for g in soup.find_all('div', class_='g')[:10]:
                title_elem = g.find('h3')
                title = title_elem.get_text() if title_elem else ''

                link_elem = g.find('a')
                url_found = link_elem.get('href', '') if link_elem else ''

                snippet_elem = g.find('div', class_=['VwiC3b', 'yXK7lf'])
                snippet = snippet_elem.get_text() if snippet_elem else ''

                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'url': url_found,
                        'source': f'Site:{site}'
                    })
                    if verbose:
                        print(f"      Found: {title[:60]}...")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Site search error: {e}")
    return results


# Ordered list of all 10 search engines
SEARCH_ENGINES = [
    ('Google', search_google),
    ('Bing', search_bing),
    ('DuckDuckGo', search_duckduckgo),
    ('Yahoo', search_yahoo),
    ('Ask', search_ask),
    ('AOL', search_aol),
    ('Ecosia', search_ecosia),
    ('Startpage', search_startpage),
    ('Qwant', search_qwant),
    ('Brave', search_brave),
]

# People search sites
PEOPLE_SEARCH_SITES = [
    'truepeoplesearch.com',
    'whitepages.com',
    'spokeo.com',
    'fastpeoplesearch.com',
    'thatsthem.com',
    'truecaller.com',
    'beenverified.com',
    'intelius.com',
    'zabasearch.com',
    'peoplefinder.com',
]

# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTION AND ANALYSIS
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
        'Please Wait', 'Click Here', 'Read More', 'Learn More',
        'Sign Up', 'Log In', 'Privacy Policy', 'Terms Service',
    }

    filtered_names = []
    for name in names:
        if name not in excluded and len(name.split()) >= 2:
            filtered_names.append(name)

    return filtered_names


def extract_locations(text):
    """Extract potential locations from text"""
    locations = []

    state_pattern = r'\b(' + '|'.join(US_STATES.keys()) + r')\b'
    state_matches = re.findall(state_pattern, text)
    locations.extend(state_matches)

    city_state_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+(' + '|'.join(US_STATES.keys()) + r')\b'
    city_state_matches = re.findall(city_state_pattern, text)
    for city, state in city_state_matches:
        locations.append(f"{city}, {state}")

    for abbr, full_name in US_STATES.items():
        if full_name in text:
            locations.append(full_name)

    zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
    zip_matches = re.findall(zip_pattern, text)
    locations.extend(zip_matches)

    return list(set(locations))


def extract_businesses(text):
    """Extract potential business names from text and URLs"""
    businesses = []

    # Business indicators in text
    biz_patterns = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|LLC|Corp|Co|Ltd|Company|Services|Solutions|Group))\b',
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Restaurant|Hotel|Store|Shop|Market|Center|Centre))\b',
    ]

    for pattern in biz_patterns:
        matches = re.findall(pattern, text)
        businesses.extend(matches)

    return list(set(businesses))


def extract_emails(text):
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(email_pattern, text)))


def extract_urls_intel(text, url=''):
    """Extract intelligence from URLs (domains often contain names/business info)"""
    intel = []

    # Extract domain parts that might be names
    domain_pattern = r'https?://(?:www\.)?([a-zA-Z0-9-]+)\.'
    domains = re.findall(domain_pattern, url + ' ' + text)

    for domain in domains:
        # Skip common domains
        if domain.lower() not in ['google', 'bing', 'yahoo', 'facebook', 'twitter',
                                   'instagram', 'linkedin', 'youtube', 'reddit',
                                   'amazon', 'ebay', 'wikipedia', 'github']:
            # Could be a business name
            intel.append(domain)

    return intel


def analyze_results(all_results, verbose=False):
    """Analyze all results for patterns"""
    all_text = []
    all_urls = []
    source_counts = Counter()
    url_domains = Counter()

    for format_str, results in all_results.items():
        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}"
            url = result.get('url', '')
            all_text.append(text)
            all_urls.append(url)
            source_counts[result.get('source', 'Unknown')] += 1

            # Track domains
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if domain_match:
                url_domains[domain_match.group(1)] += 1

    combined_text = ' '.join(all_text)
    combined_urls = ' '.join(all_urls)

    names = extract_names(combined_text)
    name_counter = Counter(names)

    locations = extract_locations(combined_text)
    location_counter = Counter(locations)

    businesses = extract_businesses(combined_text)
    business_counter = Counter(businesses)

    emails = extract_emails(combined_text)

    url_intel = extract_urls_intel(combined_text, combined_urls)
    url_intel_counter = Counter(url_intel)

    return {
        'total_results': len(all_text),
        'results_by_source': dict(source_counts),
        'common_names': name_counter.most_common(15),
        'common_locations': location_counter.most_common(10),
        'common_businesses': business_counter.most_common(10),
        'emails_found': emails,
        'url_intel': url_intel_counter.most_common(10),
        'top_domains': url_domains.most_common(10),
    }


def generate_summary(all_results, patterns):
    """Generate a weighted summary - more appearances = more detail"""
    summary = {
        'confidence': 'LOW',
        'primary_name': None,
        'primary_location': None,
        'primary_business': None,
        'duplicate_intel': [],
    }

    # Find items that appear more than once
    for name, count in patterns['common_names']:
        if count >= 2:
            summary['duplicate_intel'].append(('NAME', name, count))
            if not summary['primary_name']:
                summary['primary_name'] = name

    for location, count in patterns['common_locations']:
        if count >= 2:
            summary['duplicate_intel'].append(('LOCATION', location, count))
            if not summary['primary_location']:
                summary['primary_location'] = location

    for business, count in patterns['common_businesses']:
        if count >= 2:
            summary['duplicate_intel'].append(('BUSINESS', business, count))
            if not summary['primary_business']:
                summary['primary_business'] = business

    # Calculate confidence
    duplicate_count = len(summary['duplicate_intel'])
    if duplicate_count >= 5:
        summary['confidence'] = 'HIGH'
    elif duplicate_count >= 3:
        summary['confidence'] = 'MEDIUM'
    elif duplicate_count >= 1:
        summary['confidence'] = 'LOW'
    else:
        summary['confidence'] = 'NONE'

    return summary

# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def print_results(patterns, summary, phone_number, verbose=False):
    """Print formatted results"""
    print(f"\n{'='*70}")
    print(color.header(f"TELESPOT ANALYSIS RESULTS"))
    print(f"{'='*70}")
    print(f"Phone: {phone_number}")
    print(f"Total Results: {patterns['total_results']}")
    print(f"Confidence: {summary['confidence']}")
    print(f"{'='*70}\n")

    # Source breakdown
    if patterns['results_by_source']:
        print(color.header("Results by Source:"))
        for source, count in sorted(patterns['results_by_source'].items(), key=lambda x: -x[1]):
            print(f"  [{count:3d}] {source}")
        print()

    # Primary findings
    if summary['primary_name'] or summary['primary_location'] or summary['primary_business']:
        print(color.header("Primary Findings:"))
        if summary['primary_name']:
            print(f"  Name: {summary['primary_name']}")
        if summary['primary_location']:
            print(f"  Location: {summary['primary_location']}")
        if summary['primary_business']:
            print(f"  Business: {summary['primary_business']}")
        print()

    # Names found
    if patterns['common_names']:
        print(color.header("Names Detected:"))
        for name, count in patterns['common_names'][:10]:
            indicator = " **" if count >= 2 else ""
            print(f"  [{count}x] {name}{indicator}")
        print()

    # Locations found
    if patterns['common_locations']:
        print(color.header("Locations Detected:"))
        for location, count in patterns['common_locations'][:10]:
            indicator = " **" if count >= 2 else ""
            print(f"  [{count}x] {location}{indicator}")
        print()

    # Businesses found
    if patterns['common_businesses']:
        print(color.header("Businesses Detected:"))
        for business, count in patterns['common_businesses'][:10]:
            print(f"  [{count}x] {business}")
        print()

    # Emails found
    if patterns['emails_found']:
        print(color.header("Emails Found:"))
        for email in patterns['emails_found'][:5]:
            print(f"  {email}")
        print()

    # URL intelligence
    if patterns['url_intel'] and verbose:
        print(color.header("URL Intelligence:"))
        for intel, count in patterns['url_intel'][:10]:
            print(f"  [{count}x] {intel}")
        print()

    # Duplicate summary (items appearing 2+ times)
    if summary['duplicate_intel']:
        print(color.header("High-Confidence Intel (2+ appearances):"))
        for intel_type, value, count in sorted(summary['duplicate_intel'], key=lambda x: -x[2]):
            print(f"  [{intel_type}] {value} (appeared {count}x)")
        print()

    print(f"{'='*70}\n")


def save_json_results(phone_number, formats, all_results, patterns, summary, filename=None):
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
        'results': {},
        'patterns': {
            'total_results': patterns['total_results'],
            'results_by_source': patterns['results_by_source'],
            'names': [{'name': n, 'count': c} for n, c in patterns['common_names']],
            'locations': [{'location': l, 'count': c} for l, c in patterns['common_locations']],
            'businesses': [{'business': b, 'count': c} for b, c in patterns['common_businesses']],
            'emails': patterns['emails_found'],
        },
        'summary': {
            'confidence': summary['confidence'],
            'primary_name': summary['primary_name'],
            'primary_location': summary['primary_location'],
            'primary_business': summary['primary_business'],
            'high_confidence_intel': [
                {'type': t, 'value': v, 'count': c}
                for t, v, c in summary['duplicate_intel']
            ],
        },
    }

    # Add results (with some cleanup for JSON)
    for fmt, results in all_results.items():
        output['results'][fmt] = results

    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    return filename

# ═══════════════════════════════════════════════════════════════════════════════
# API FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def query_numverify(phone_number, api_key):
    """Query NumVerify API for phone validation"""
    if not api_key:
        return None
    try:
        url = f"http://apilayer.net/api/validate?access_key={api_key}&number={phone_number}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def query_abstract_api(phone_number, api_key):
    """Query Abstract API for phone validation"""
    if not api_key:
        return None
    try:
        url = f"https://phonevalidation.abstractapi.com/v1/?api_key={api_key}&phone={phone_number}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def update_from_repo():
    """Update telespot from the repository"""
    print(color.header("\nUpdating telespot from repository..."))

    try:
        # Check if git is available
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Git not found. Please install git or download manually from:")
            print(f"  {REPO_URL}")
            return False

        # Check if we're in a git repo
        script_dir = os.path.dirname(os.path.abspath(__file__))
        git_dir = os.path.join(script_dir, '.git')

        if os.path.exists(git_dir):
            # Pull latest changes
            print("Pulling latest changes...")
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
            # Not a git repo, try to clone
            print("Not a git repository. Please run:")
            print(f"  git clone {REPO_URL}")
            return False

    except Exception as e:
        print(f"Update error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# INTERACTIVE SETUP
# ═══════════════════════════════════════════════════════════════════════════════

def interactive_api_setup():
    """Interactive setup for API keys"""
    print(color.header("\n" + "="*60))
    print(color.header("TELESPOT API CONFIGURATION"))
    print(color.header("="*60))
    print("\nThis will help you configure API keys for enhanced lookups.")
    print("Press Enter to skip any API you don't want to configure.\n")

    apis = [
        ('numverify_api_key', 'NumVerify', 'Phone validation (free tier available)'),
        ('abstract_api_key', 'AbstractAPI', 'Phone validation (free tier available)'),
        ('twilio_account_sid', 'Twilio Account SID', 'Caller ID lookup'),
        ('twilio_auth_token', 'Twilio Auth Token', 'Twilio authentication'),
        ('opencnam_account_sid', 'OpenCNAM Account SID', 'Caller ID name lookup'),
        ('opencnam_auth_token', 'OpenCNAM Auth Token', 'OpenCNAM authentication'),
        ('telnyx_api_key', 'Telnyx', 'Phone number intelligence'),
    ]

    for key, name, description in apis:
        current = config.get(key, '')
        masked = f"[{current[:4]}...{current[-4:]}]" if len(current) > 8 else "[not set]"

        print(f"\n{name} - {description}")
        print(f"  Current: {masked}")
        value = input(f"  Enter new value (or Enter to keep): ").strip()

        if value:
            config.set(key, value)

    # Country code setting
    print(f"\nDefault Country Code")
    print(f"  Current: {config.get('default_country_code', '+1')}")
    print("  Common codes: +1 (USA/Canada), +44 (UK), +49 (Germany), +33 (France)")
    cc = input("  Enter country code (or Enter to keep): ").strip()
    if cc:
        if not cc.startswith('+'):
            cc = '+' + cc
        config.set('default_country_code', cc)

    # Save configuration
    if config.save():
        print(color.success("\nConfiguration saved successfully!"))
    else:
        print(color.error("\nFailed to save configuration."))

    config.display_api_status()

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
        color = ColorMode('mono')

    # Get country code
    country_code = args.country or config.get('default_country_code', '+1')

    # Generate search formats
    formats = generate_phone_formats(phone_number, country_code)
    if not formats:
        print(color.error("Invalid phone number format. Please check and try again."))
        return None

    print(f"\nPhone Number: {phone_number}")
    print(f"Country Code: {country_code}")
    print(f"Search Formats: {len(formats)}")
    if args.verbose:
        for fmt in formats:
            print(f"  - {fmt}")
    print()

    # Show API status
    if args.verbose:
        config.display_api_status()

    # DTMF display
    if args.dtmf:
        dtmf = get_dtmf_representation(phone_number)
        print(f"DTMF Representation: {dtmf}\n")

    all_results = {}
    total_found = 0

    # Keyword addition
    keyword_suffix = f" {args.keyword}" if args.keyword else ""

    # Run searches
    for fmt in formats:
        query = fmt + keyword_suffix
        print(color.header(f"Searching: {query}"))
        format_results = []

        # Search specific site if requested
        if args.site:
            print(f"  -> Site: {args.site}")
            site_results = search_site(query, args.site, args.verbose, args.debug)
            format_results.extend(site_results)
            print(f"     Found: {len(site_results)} results")
            delay = rate_limit()
            if args.verbose:
                print(f"     Rate limit: {delay:.1f}s")
        else:
            # Search all 10 engines
            for engine_name, search_func in SEARCH_ENGINES:
                print(f"  -> {engine_name}...", end=' ', flush=True)
                results = search_func(query, args.verbose, args.debug)
                format_results.extend(results)
                print(f"({len(results)})")

                delay = rate_limit()
                if args.verbose:
                    print(f"     Rate limit: {delay:.1f}s")

        # Also search people search sites
        if not args.site:
            for site in PEOPLE_SEARCH_SITES[:3]:  # Top 3 people search sites
                print(f"  -> site:{site}...", end=' ', flush=True)
                site_results = search_site(query, site, args.verbose, args.debug)
                format_results.extend(site_results)
                print(f"({len(site_results)})")
                delay = rate_limit()

        all_results[fmt] = format_results
        total_found += len(format_results)
        print(f"  Total for format: {len(format_results)}\n")

    print(color.header(f"\nTotal Results Collected: {total_found}"))

    # Analyze results
    print("\nAnalyzing patterns...")
    patterns = analyze_results(all_results, args.verbose)
    summary = generate_summary(all_results, patterns)

    # Print results
    print_results(patterns, summary, phone_number, args.verbose)

    # Print summary comparison if requested
    if args.summary:
        print(color.header("\n" + "="*70))
        print(color.header("SUMMARY COMPARISON"))
        print("="*70)

        if summary['duplicate_intel']:
            print("\nItems appearing multiple times (higher confidence):\n")

            # Sort by count descending
            sorted_intel = sorted(summary['duplicate_intel'], key=lambda x: -x[2])

            for intel_type, value, count in sorted_intel:
                # More appearances = more detail
                bar = "█" * min(count, 20)
                spaces = " " * (20 - min(count, 20))
                print(f"  {intel_type:10} | {bar}{spaces} | {value} ({count}x)")

            print()
        else:
            print("\nNo items appeared multiple times.")
            print("Try searching with different formats or keywords.\n")

    # Save to JSON if requested
    if args.output:
        filename = save_json_results(phone_number, formats, all_results, patterns, summary, args.output)
        print(color.success(f"\nResults saved to: {filename}"))

    return {
        'phone_number': phone_number,
        'formats': formats,
        'results': all_results,
        'patterns': patterns,
        'summary': summary,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def create_parser():
    """Create argument parser with all options"""
    parser = argparse.ArgumentParser(
        prog='telespot',
        description=f'''
╔══════════════════════════════════════════════════════════════════╗
║  telespot v{VERSION} - Multi-Engine Phone Number OSINT Tool       ║
╠══════════════════════════════════════════════════════════════════╣
║  Searches 10 search engines + people search sites for phone     ║
║  number intelligence including names, locations, and business   ║
║  associations.                                                   ║
╚══════════════════════════════════════════════════════════════════╝
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
EXAMPLES:
  telespot 2155551234                    Basic search (US number)
  telespot +442071234567 -c +44          UK number search
  telespot 2155551234 -k "pizza"         Search with keyword
  telespot 2155551234 -s whitepages.com  Search specific site
  telespot 2155551234 -v -o results.json Verbose with JSON output
  telespot 2155551234 --summary          Show comparison summary
  telespot --setup                       Configure API keys
  telespot --update                      Update from repository

API SETUP:
  Run 'telespot --setup' to configure API keys for enhanced lookups.
  Supported APIs: NumVerify, AbstractAPI, Twilio, OpenCNAM, Telnyx

SEARCH ENGINES (in order):
  1. Google      2. Bing        3. DuckDuckGo   4. Yahoo
  5. Ask         6. AOL         7. Ecosia       8. Startpage
  9. Qwant      10. Brave

PEOPLE SEARCH SITES:
  truepeoplesearch.com, whitepages.com, spokeo.com, fastpeoplesearch.com,
  thatsthem.com, truecaller.com, beenverified.com, and more

For more information: https://github.com/thumpersecure/Telespot
''')

    # Positional argument
    parser.add_argument('phone', nargs='?', help='Phone number to search')

    # Search options
    search_group = parser.add_argument_group('Search Options')
    search_group.add_argument('-k', '--keyword', metavar='WORD',
                              help='Add keyword to search (e.g., "pizza", "owner")')
    search_group.add_argument('-s', '--site', metavar='DOMAIN',
                              help='Search specific site (e.g., whitepages.com)')
    search_group.add_argument('-c', '--country', metavar='CODE',
                              help='Country code (default: +1 for US)')

    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('-o', '--output', metavar='FILE',
                              help='Save results to JSON file')
    output_group.add_argument('-v', '--verbose', action='store_true',
                              help='Show verbose output with all findings')
    output_group.add_argument('--summary', action='store_true',
                              help='Show comparison summary of duplicate results')
    output_group.add_argument('--dtmf', action='store_true',
                              help='Show DTMF tone representation')

    # Display options
    display_group = parser.add_argument_group('Display Options')
    display_group.add_argument('--colorful', action='store_true',
                               help='Enable rainbow color mode')
    display_group.add_argument('--no-color', action='store_true',
                               help='Disable all colors')

    # Configuration options
    config_group = parser.add_argument_group('Configuration')
    config_group.add_argument('--setup', action='store_true',
                              help='Interactive API key setup')
    config_group.add_argument('--api-status', action='store_true',
                              help='Show API configuration status')

    # Maintenance options
    maint_group = parser.add_argument_group('Maintenance')
    maint_group.add_argument('--update', action='store_true',
                             help='Update telespot from repository')
    maint_group.add_argument('--version', action='version',
                             version=f'telespot v{VERSION}')

    # Debug options
    debug_group = parser.add_argument_group('Debug')
    debug_group.add_argument('-d', '--debug', action='store_true',
                             help='Enable debug mode for troubleshooting')

    return parser

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    global color

    parser = create_parser()
    args = parser.parse_args()

    # Set initial color mode
    if args.no_color:
        color = ColorMode('off')
    elif args.colorful:
        color = ColorMode('colorful')
    else:
        color = ColorMode('mono')

    # Print logo (always with colors unless --no-color)
    if not args.no_color:
        print(get_ascii_logo())
    else:
        print(get_ascii_logo_mono())

    # Check for BS4
    if not BS4_AVAILABLE:
        print(color.warning("Warning: beautifulsoup4 not installed. Install with:"))
        print("  pip install beautifulsoup4 lxml")
        print()

    # Handle special commands
    if args.setup:
        interactive_api_setup()
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

        # Prompt for international
        use_intl = input("\nUse international number? (y/N): ").strip().lower()
        if use_intl == 'y':
            print("\nCommon country codes:")
            for code, country in list(COUNTRY_CODES.items())[:10]:
                print(f"  {code}: {country}")
            args.country = input("\nEnter country code (e.g., +44): ").strip()
            if not args.country.startswith('+'):
                args.country = '+' + args.country

        phone_number = input("\nPhone number: ").strip()

        if not phone_number:
            print(color.error("No phone number provided."))
            parser.print_help()
            return 1

    # Run search
    try:
        result = run_search(phone_number, args)

        if result:
            # Prompt to save if not already saving
            if not args.output:
                save = input("\nSave results to JSON? (y/N): ").strip().lower()
                if save == 'y':
                    filename = save_json_results(
                        phone_number,
                        result['formats'],
                        result['results'],
                        result['patterns'],
                        result['summary']
                    )
                    print(color.success(f"Results saved to: {filename}"))

        return 0

    except KeyboardInterrupt:
        print(color.warning("\n\nSearch interrupted by user."))
        return 130


if __name__ == "__main__":
    sys.exit(main())
