#!/usr/bin/env python3
"""
telespot - Phone Number OSINT Tool
Version 5.2.0

API-based phone number search across Google, Brave, and DuckDuckGo
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

from telespot_common.colors import Colors
from telespot_common.config import resolve_config_path
from telespot_common.http_fingerprint import (
    detect_captcha,
    get_api_headers,
    get_random_headers,
    is_bot_challenge_page,
    merge_headers,
)
from telespot_common.patterns import (
    US_STATES,
    extract_locations,
    extract_names,
    extract_usernames,
)

VERSION = "5.2.0"
REPO_URL = "https://github.com/thumpersecure/Telespot"
CONFIG_FILE = resolve_config_path(local_dir=os.path.dirname(os.path.abspath(__file__)))

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
        'brave_api_key': '',
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
                f.write("# Brave Search API (free tier ~2000/mo)\n")
                f.write(f"brave_api_key={self.settings.get('brave_api_key', '')}\n\n")
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
            'Brave': bool(self.settings.get('brave_api_key')),
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


def create_session():
    """Create a requests.Session with connection pooling and retry-friendly settings"""
    session = requests.Session()
    # Connection pooling for better performance and less suspicious traffic patterns
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=10,
        max_retries=0,  # We handle retries ourselves
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# Global session for connection reuse
_session = None

def get_session():
    """Get or create the global requests session"""
    global _session
    if _session is None:
        _session = create_session()
    return _session


def request_with_retry(method, url, max_retries=3, backoff_base=2.0, debug=False, **kwargs):
    """Make an HTTP request with retry logic and captcha detection.

    Retries on transient failures (429, 503, network errors) with exponential backoff.
    Detects captcha/block pages and retries with fresh headers.

    Returns (response, was_blocked) tuple. was_blocked indicates if all retries
    were exhausted due to captcha/rate limiting.
    """
    session = get_session()
    last_exception = None

    # Read the API-mode flag once, up front. It used to be popped from kwargs
    # inside the loop, so every retry silently switched to browser-style
    # headers and to browser-style captcha detection.
    api_mode = bool(kwargs.pop('_api_mode', False))
    caller_headers = dict(kwargs.get('headers') or {})

    for attempt in range(max_retries + 1):
        try:
            # Use fresh fingerprint headers on each attempt to vary the
            # fingerprint, but MERGE them under the caller-supplied headers so
            # auth headers (Brave subscription key, Dehashed API key, ...)
            # survive retries.
            fresh = get_api_headers() if api_mode else get_random_headers()
            kwargs['headers'] = merge_headers(fresh, caller_headers)

            if 'timeout' not in kwargs:
                kwargs['timeout'] = 15

            response = getattr(session, method)(url, **kwargs)

            # Check for captcha/blocking
            if detect_captcha(response, api_mode=api_mode):
                if debug:
                    print(f"      [DEBUG] Captcha/block detected (attempt {attempt + 1}/{max_retries + 1}), status={response.status_code}")

                if attempt < max_retries:
                    wait = backoff_base * (2 ** attempt) + random.uniform(0.5, 2.0)
                    if debug:
                        print(f"      [DEBUG] Backing off {wait:.1f}s before retry...")
                    time.sleep(wait)
                    continue
                else:
                    return response, True  # All retries exhausted, was blocked

            # Check for rate limiting specifically (429)
            if response.status_code == 429:
                if attempt < max_retries:
                    # Respect Retry-After header if present
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait = float(retry_after)
                        except ValueError:
                            wait = backoff_base * (2 ** attempt)
                    else:
                        wait = backoff_base * (2 ** attempt) + random.uniform(1.0, 3.0)
                    if debug:
                        print(f"      [DEBUG] Rate limited (429), waiting {wait:.1f}s...")
                    time.sleep(wait)
                    continue
                return response, True

            return response, False

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exception = e
            if debug:
                print(f"      [DEBUG] Network error (attempt {attempt + 1}/{max_retries + 1}): {e}")
            if attempt < max_retries:
                wait = backoff_base * (2 ** attempt) + random.uniform(0.5, 1.5)
                time.sleep(wait)
                continue
            raise

        except Exception as e:
            last_exception = e
            if debug:
                print(f"      [DEBUG] Unexpected error: {e}")
            raise

    # Should not reach here, but just in case
    if last_exception:
        raise last_exception
    return None, True


# ═══════════════════════════════════════════════════════════════════════════════
# ADAPTIVE RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════════════

class AdaptiveRateLimiter:
    """Rate limiter that adjusts delay based on observed blocking/success patterns.

    Starts with a moderate delay and increases if blocks are detected,
    or decreases (to a minimum) if requests succeed consistently.
    """

    def __init__(self, base_delay=2.0, min_delay=1.5, max_delay=15.0):
        self.base_delay = base_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.current_delay = base_delay
        self.consecutive_successes = 0
        self.consecutive_blocks = 0
        self.total_blocks = 0

    def record_success(self):
        """Record a successful request"""
        self.consecutive_successes += 1
        self.consecutive_blocks = 0
        # Gradually reduce delay after sustained success
        if self.consecutive_successes >= 3:
            self.current_delay = max(self.min_delay, self.current_delay * 0.85)

    def record_block(self):
        """Record a blocked/rate-limited request"""
        self.consecutive_blocks += 1
        self.consecutive_successes = 0
        self.total_blocks += 1
        # Increase delay on blocks
        self.current_delay = min(self.max_delay, self.current_delay * 1.8)

    def wait(self):
        """Sleep for the adaptive delay with jitter"""
        jitter = random.uniform(-0.5, 1.5)
        delay = max(self.min_delay, self.current_delay + jitter)
        time.sleep(delay)
        return delay

    def get_stats(self):
        """Get rate limiter statistics"""
        return {
            'current_delay': round(self.current_delay, 1),
            'total_blocks': self.total_blocks,
        }


def rate_limit():
    """Legacy rate limiting - random 3-5 seconds (used when adaptive limiter not active)"""
    delay = random.uniform(3.0, 5.0)
    time.sleep(delay)
    return delay

# ═══════════════════════════════════════════════════════════════════════════════
# US STATES AND LOCATION DATA
# ═══════════════════════════════════════════════════════════════════════════════

# US_STATES is imported from telespot_common.patterns (shared with telespotx).

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
        # Strip a leading country code that the user typed into the number
        # itself (e.g. "+442071234567" with -c +44) so it is not doubled.
        if digits.startswith(cc) and len(digits) - len(cc) >= 7:
            digits = digits[len(cc):]
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

    intl = f'+{country_code.lstrip("+")}'

    # 4 Basic formats
    basic = [
        f'{area}-{prefix}-{line}',                    # 215-555-1234
        f'{area}{prefix}{line}',                      # 2155551234
        f'({area}) {prefix}-{line}',                  # (215) 555-1234
        f'{intl}{area}-{prefix}-{line}',              # +1215-555-1234 / +44207-123-4567
    ]

    # 4 Quoted formats (exact match)
    quoted = [
        f'"{area}-{prefix}-{line}"',                  # "215-555-1234"
        f'"{area}{prefix}{line}"',                    # "2155551234"
        f'"({area}) {prefix}-{line}"',                # "(215) 555-1234"
        f'"{intl}{area}-{prefix}-{line}"',            # "+1215-555-1234"
    ]

    # 2 Special formats
    special = [
        f'({area}-{prefix}-{line})',                  # (215-555-1234)
        f'"{area}.{prefix}.{line}"',                  # "215.555.1234" (dot-separated)
    ]

    return basic + quoted + special


def get_dtmf_representation(phone_number):
    """Convert phone number to DTMF representation"""
    digits = re.sub(r'\D', '', phone_number)
    return ' '.join(DTMF_MAP.get(d, d) for d in digits)

# ═══════════════════════════════════════════════════════════════════════════════
# API SEARCH FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def search_google_api(query, api_key, cse_id, num_results=10, verbose=False, debug=False, rate_limiter=None):
    """Search using Google Custom Search API with retry and captcha detection"""
    results = []

    if not api_key or not cse_id:
        if debug:
            print("    [DEBUG] Google API not configured")
        return results

    try:
        url = "https://www.googleapis.com/customsearch/v1"

        # Google CSE honors quoted phrases natively inside `q`, so pass the
        # query (quotes and all) straight through. Only use exactTerms for the
        # bare digits-only format, where it usefully narrows without the
        # over-filtering that a quoted phone format triggers.
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': query,
            'num': min(num_results, 10),
        }

        digits_only = re.sub(r'\D', '', query)
        if query.strip() == digits_only and digits_only:
            params['exactTerms'] = digits_only

        response, was_blocked = request_with_retry(
            'get', url, params=params, _api_mode=True, debug=debug
        )

        if was_blocked:
            if rate_limiter:
                rate_limiter.record_block()
            print(f"    {color.warning('Google API blocked/rate limited - backing off')}")
            return results

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
            if rate_limiter:
                rate_limiter.record_success()
        elif response.status_code == 429:
            print(f"    {color.warning('Google API quota exceeded')}")
            if rate_limiter:
                rate_limiter.record_block()
        else:
            # 400 = malformed key/cx, 403 = key invalid, API not enabled or
            # daily quota exhausted. Always say so instead of hiding it.
            print(f"    {color.warning(f'Google API error {response.status_code}: {_api_error_message(response)}')}")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] Google exception: {e}")

    return results


def _api_error_message(response, limit=120):
    """Best-effort human-readable error from a JSON API error response."""
    try:
        data = response.json()
        err = data.get('error', data)
        if isinstance(err, dict):
            msg = err.get('message') or err.get('detail') or err.get('code')
            if msg:
                return str(msg)[:limit]
        if isinstance(err, str):
            return err[:limit]
    except Exception:
        pass
    text = (getattr(response, 'text', '') or '').strip()
    return text[:limit] if text else 'no error details'


def search_brave_api(query, api_key, num_results=10, verbose=False, debug=False, rate_limiter=None):
    """Search using the Brave Search API with retry and captcha detection.

    Replaces the retired Bing Search API (Microsoft shut down
    api.bing.microsoft.com/v7.0/search in Aug 2025). Brave's free tier allows
    ~2000 queries/month. Requires the X-Subscription-Token header.
    """
    results = []

    if not api_key:
        if debug:
            print("    [DEBUG] Brave API not configured")
        return results

    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = get_api_headers()
        headers['X-Subscription-Token'] = api_key
        headers['Accept'] = 'application/json'
        params = {
            'q': query,
            'count': min(num_results, 20),
        }

        response, was_blocked = request_with_retry(
            'get', url, headers=headers, params=params, _api_mode=True, debug=debug
        )

        if was_blocked:
            if rate_limiter:
                rate_limiter.record_block()
            print(f"    {color.warning('Brave API blocked/rate limited - backing off')}")
            return results

        if debug:
            print(f"    [DEBUG] Brave API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for item in data.get('web', {}).get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('description', ''),
                    'source': 'Brave'
                })
                if verbose:
                    print(f"      Found: {item.get('title', '')[:60]}...")
            if rate_limiter:
                rate_limiter.record_success()
        elif response.status_code in (401, 403):
            print(f"    {color.warning('Brave API key invalid or subscription inactive')}")
        elif response.status_code == 429:
            print(f"    {color.warning('Brave API quota exceeded')}")
            if rate_limiter:
                rate_limiter.record_block()
        else:
            print(f"    {color.warning(f'Brave API error {response.status_code}: {_api_error_message(response)}')}")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] Brave exception: {e}")

    return results


def search_duckduckgo_api(query, num_results=10, verbose=False, debug=False, rate_limiter=None):
    """Search using DuckDuckGo Instant Answer API with HTML fallback.

    The Instant Answer API only returns knowledge-graph style results,
    which are often empty for phone numbers. When the API returns no results,
    falls back to scraping the DuckDuckGo HTML lite search page for
    actual web results.
    """
    results = []

    # --- Phase 1: Try the Instant Answer API first ---
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1,
        }

        response, was_blocked = request_with_retry(
            'get', url, params=params, _api_mode=True, debug=debug
        )

        if was_blocked:
            if debug:
                print(f"    [DEBUG] DuckDuckGo API blocked, trying HTML fallback...")
        elif response is not None and 200 <= response.status_code < 300:
            # The Instant Answer API now answers with HTTP 202 (not 200) for
            # most queries while still returning a full JSON body. Accept any
            # 2xx and let the JSON parse decide.
            if debug:
                print(f"    [DEBUG] DuckDuckGo API status: {response.status_code}")

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
            print(f"    [DEBUG] DuckDuckGo API exception: {e}")

    # --- Phase 2: HTML fallback when API returns few/no results ---
    if len(results) < 3 and not _ddg_html_disabled:
        html_results = _search_duckduckgo_html(query, num_results, verbose, debug, rate_limiter)
        results.extend(html_results)

    if rate_limiter and results:
        rate_limiter.record_success()

    return results


# DuckDuckGo serves a "bots use DuckDuckGo too" picture challenge (HTTP 202)
# to clients it does not trust. It is intermittent (a retry often succeeds),
# but once three formats in a row have been challenged on every attempt
# there is no point burning backoff on the remaining ones, so the HTML
# fallback is switched off for the rest of the run and the user is told why.
_DDG_CHALLENGE_LIMIT = 3
_ddg_challenge_streak = 0
_ddg_html_disabled = False


def _note_ddg_challenge(debug=False):
    global _ddg_challenge_streak, _ddg_html_disabled
    _ddg_challenge_streak += 1
    if _ddg_challenge_streak == 1:
        print(f"\n    {color.warning('DuckDuckGo answered with a bot challenge instead of results')}")
    if _ddg_challenge_streak >= _DDG_CHALLENGE_LIMIT and not _ddg_html_disabled:
        _ddg_html_disabled = True
        print(f"    {color.warning('DuckDuckGo is challenging this client; skipping its web search for the remaining formats.')}")
        print(f"    {color.warning('Try again later or from another network. Google/Brave keys give reliable results.')}")


def _search_duckduckgo_html(query, num_results=10, verbose=False, debug=False, rate_limiter=None):
    """Scrape DuckDuckGo HTML lite search for actual web results.

    This is the fallback when the Instant Answer API returns nothing,
    which is common for phone number queries. The HTML lite version is
    lightweight and less likely to trigger captchas.
    """
    global _ddg_challenge_streak
    results = []

    try:
        # The lite endpoint (GET with q=) is far more scrape-friendly than
        # the old html.duckduckgo.com POST form, which stopped returning the
        # result__a/result__snippet markup to non-browser clients.
        url = "https://lite.duckduckgo.com/lite/"
        params = {'q': query}

        response, was_blocked = request_with_retry(
            'get', url, params=params, max_retries=1, debug=debug
        )

        if was_blocked:
            if debug:
                print(f"    [DEBUG] DuckDuckGo HTML search blocked")
            if response is not None and is_bot_challenge_page(response.text):
                # A bot challenge is not rate limiting: waiting longer between
                # formats does not make it go away, so it is not fed to the
                # adaptive limiter (which would otherwise stretch every
                # remaining delay to its maximum).
                _note_ddg_challenge(debug)
            elif rate_limiter:
                rate_limiter.record_block()
            return results

        if response is not None and 200 <= response.status_code < 300:
            body = response.text

            if is_bot_challenge_page(body):
                # HTTP 202 challenge page that slipped past detect_captcha.
                _note_ddg_challenge(debug)
                return results

            _ddg_challenge_streak = 0

            # lite endpoint markup (single-quoted class attributes):
            #   <a rel="nofollow" href="...uddg=..." class='result-link'>title</a>
            #   <td class='result-snippet'>snippet text</td>
            link_pattern = r"<a[^>]*href=\"([^\"]*)\"[^>]*class=['\"]result-link['\"][^>]*>(.*?)</a>"
            links = re.findall(link_pattern, body, re.DOTALL)

            snippet_pattern = r"<td[^>]*class=['\"]result-snippet['\"][^>]*>(.*?)</td>"
            snippets = re.findall(snippet_pattern, body, re.DOTALL)

            if not links:
                if 'no results' in body.lower() or 'no more results' in body.lower():
                    if debug:
                        print(f"    [DEBUG] DuckDuckGo HTML: no results for this format")
                else:
                    # Silent breakage guard: 2xx but nothing parsed usually
                    # means DDG changed its markup again. Warn, don't swallow it.
                    print(f"    {color.warning(f'DuckDuckGo HTML: HTTP {response.status_code} but 0 results parsed (selectors may be stale)')}")
                    if debug:
                        print(f"    [DEBUG] response body length={len(body)}")

            for i, (href, title) in enumerate(links[:num_results]):
                # Clean HTML tags from title and snippet
                clean_title = re.sub(r'<[^>]+>', '', title).strip()
                clean_snippet = ''
                if i < len(snippets):
                    clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()

                # DuckDuckGo wraps URLs in a redirect - extract the actual URL
                actual_url = href
                if 'uddg=' in href:
                    url_match = re.search(r'uddg=([^&]+)', href)
                    if url_match:
                        from urllib.parse import unquote
                        actual_url = unquote(url_match.group(1))

                if clean_title and actual_url:
                    results.append({
                        'title': clean_title,
                        'url': actual_url,
                        'snippet': clean_snippet,
                        'source': 'DuckDuckGo'
                    })
                    if verbose:
                        print(f"      Found: {clean_title[:60]}...")

            if debug:
                print(f"    [DEBUG] DuckDuckGo HTML returned {len(results)} results")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] DuckDuckGo HTML exception: {e}")

    return results


def search_dehashed_api(query, api_key, verbose=False, debug=False, rate_limiter=None):
    """Search Dehashed breach database (optional) with retry and captcha detection"""
    results = []

    if not api_key:
        if debug:
            print("    [DEBUG] Dehashed API not configured")
        return results

    try:
        # Dehashed v2: POST JSON to /v2/search with a Dehashed-Api-Key header.
        # The v1 GET + basic-auth endpoint is retired. The API key is just the
        # raw key now; tolerate a legacy "email:key" value by taking the key
        # part after the colon.
        url = "https://api.dehashed.com/v2/search"
        raw_key = api_key.split(':', 1)[1] if ':' in api_key else api_key
        headers = get_api_headers()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'
        headers['Dehashed-Api-Key'] = raw_key
        payload = {'query': f'phone:"{query}"'}

        response, was_blocked = request_with_retry(
            'post', url, json=payload, headers=headers, _api_mode=True, debug=debug
        )

        if was_blocked:
            if rate_limiter:
                rate_limiter.record_block()
            print(f"    {color.warning('Dehashed API blocked/rate limited')}")
            return results

        if debug:
            print(f"    [DEBUG] Dehashed API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            def _flatten(v, default=''):
                # v2 returns most fields as lists of strings.
                if isinstance(v, list):
                    return ' '.join(str(x) for x in v) if v else default
                return v if v else default

            for entry in data.get('entries', [])[:10]:
                # v2: 'name' (and other fields) are now lists, not strings.
                raw_name = _flatten(entry.get('name', ''))
                raw_username = _flatten(entry.get('username', ''))
                email = _flatten(entry.get('email', ''), 'N/A')
                database = _flatten(entry.get('database_name', ''), 'N/A')
                name = f"{raw_name} {raw_username}".strip()
                results.append({
                    'title': name or 'Dehashed Entry',
                    'url': database if database != 'N/A' else '',
                    'snippet': f"Email: {email} | Database: {database}",
                    'source': 'Dehashed'
                })
                if verbose:
                    print(f"      Found: {name[:60]}...")
            if rate_limiter:
                rate_limiter.record_success()
        elif response.status_code in (401, 403):
            print(f"    {color.warning('Dehashed API key invalid or out of credits')}")
        else:
            print(f"    {color.warning(f'Dehashed API error {response.status_code}: {_api_error_message(response)}')}")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] Dehashed exception: {e}")

    return results

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

# extract_names / extract_locations / extract_usernames are imported from
# telespot_common.patterns (shared, canonical implementations).


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


def deduplicate_results(all_results):
    """Remove duplicate results across all format groups by URL."""
    from telespot_common.dedupe import deduplicate_results_dict

    return deduplicate_results_dict(all_results)

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

    # Brave
    print(color.info("\nBrave Search API (free tier ~2000 queries/month)"))
    print("  Get key at: https://api.search.brave.com/")
    print("  1. Sign up for the Data for Search API")
    print("  2. Copy the subscription token")

    current_brave = config.get('brave_api_key', '')
    masked = f"[{current_brave[:8]}...]" if len(current_brave) > 8 else "[not set]"
    print(f"\n  Current Brave Key: {masked}")
    brave = input("  Enter Brave API Key (or Enter to skip): ").strip()
    if brave:
        config.set('brave_api_key', brave)

    # Dehashed
    print(color.info("\nDehashed API (optional - for breach database search)"))
    print("  Get key at: https://www.dehashed.com/ (v2 API)")
    print("  Format: your raw API key (legacy email:key is also accepted)")

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
    """Main search orchestration with adaptive rate limiting and captcha resilience"""
    global color, _ddg_challenge_streak, _ddg_html_disabled

    # Fresh DuckDuckGo challenge bookkeeping for every run
    _ddg_challenge_streak = 0
    _ddg_html_disabled = False

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
    brave_key = config.get('brave_api_key', '')
    dehashed_key = config.get('dehashed_api_key', '')

    # Initialize adaptive rate limiter
    limiter = AdaptiveRateLimiter(
        base_delay=float(config.get('delay_seconds', '2')),
        min_delay=1.5,
        max_delay=15.0,
    )

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
            print(f"  -> Google API...", end=' ', flush=True)
            results = search_google_api(query, google_key, google_cse, 10, args.verbose, args.debug, limiter)
            format_results.extend(results)
            print(f"({len(results)} results)")
            time.sleep(1)

        # Brave API
        if brave_key:
            print(f"  -> Brave API...", end=' ', flush=True)
            results = search_brave_api(query, brave_key, 10, args.verbose, args.debug, limiter)
            format_results.extend(results)
            print(f"({len(results)} results)")
            time.sleep(1)

        # DuckDuckGo (always available, with HTML fallback)
        print(f"  -> DuckDuckGo...", end=' ', flush=True)
        results = search_duckduckgo_api(query, 10, args.verbose, args.debug, limiter)
        format_results.extend(results)
        print(f"({len(results)} results)")

        # Dehashed (optional)
        if dehashed_key and args.dehashed:
            print(f"  -> Dehashed...", end=' ', flush=True)
            clean_query = re.sub(r'\D', '', fmt)
            results = search_dehashed_api(clean_query, dehashed_key, args.verbose, args.debug, limiter)
            format_results.extend(results)
            print(f"({len(results)} results)")

        all_results[fmt] = format_results
        total_found += len(format_results)

        print(f"  {color.success(f'+ {len(format_results)} total for this format')}")

        # Adaptive rate limiting (adjusts based on block/success patterns)
        if i < len(formats):
            delay_time = limiter.wait()
            stats = limiter.get_stats()
            status = f"delay={stats['current_delay']}s"
            if stats['total_blocks'] > 0:
                status += f", blocks={stats['total_blocks']}"
            print(f"  {color.warning(f'Waited {delay_time:.1f}s ({status})')}\n")
        else:
            print()

    # Deduplicate results across formats
    raw_total = total_found
    all_results = deduplicate_results(all_results)
    deduped_total = sum(len(r) for r in all_results.values())

    print(f"\n{color.header(f'Total Results: {deduped_total}')}", end='')
    if deduped_total < raw_total:
        print(f" ({raw_total - deduped_total} duplicates removed)")
    else:
        print()

    # Show rate limiter summary if there were blocks
    stats = limiter.get_stats()
    if stats['total_blocks'] > 0:
        block_count = stats['total_blocks']
        print(color.warning(f'Rate limit events: {block_count} (delays auto-adjusted)'))
    print()

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
║  API-based search across Google, Brave, and DuckDuckGo with     ║
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
  At minimum, configure Google or Brave for best results.
  DuckDuckGo works without an API key.

SEARCH ENGINES:
  • Google Custom Search API (requires API key + CSE ID)
  • Brave Search API (requires subscription token; free tier ~2000/mo)
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

        if result and not args.output and sys.stdin.isatty():
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
