#!/usr/bin/env python3
"""
telespot - Phone Number OSINT Tool
Version 6.0.0

One tool, three speeds. telespot.py (sequential, requests) and telespotx.py
(parallel, httpx) are merged into a single async engine:

  * every search engine is called concurrently for a format, and several
    formats are searched at once (``--mode fast`` / ``balanced`` / ``safe``);
  * each engine sits behind its own rate gate, so parallelism never exceeds
    what the engine tolerates (Brave free tier: 1 query/s; DuckDuckGo's web
    search challenges bursts; Google CSE and Dehashed are plain APIs);
  * gates back off automatically when an engine rate-limits or challenges,
    and DuckDuckGo's web fallback is switched off after repeated challenges.

Requires httpx (pip install -r requirements.txt).
"""

import argparse
import asyncio
import json
import os
import random
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from urllib.parse import unquote

try:
    import httpx
except ImportError:
    print("telespot requires httpx. Install with: pip install -r requirements.txt  (or: pip install httpx brotli)")
    sys.exit(1)

from telespot_common.colors import Colors
from telespot_common.config import resolve_config_path
from telespot_common.dedupe import deduplicate_results_dict
from telespot_common.http_fingerprint import (
    detect_captcha,
    get_api_headers,
    get_random_headers,
    is_bot_challenge_page,
    merge_headers,
)
from telespot_common.patterns import (
    US_STATES,
    extract_emails,
    extract_locations,
    extract_names,
    extract_usernames,
)

VERSION = "6.0.0"
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
            'dim': Colors.DIM,
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
    def dim(self, text):
        return self.text(text, 'dim')


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
        'default_mode': 'balanced',
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
                f.write(f"default_mode={self.settings.get('default_mode', 'balanced')}\n")
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
# SPEED MODES AND RATE GATES
# ═══════════════════════════════════════════════════════════════════════════════

# Every mode runs all engines concurrently for a format. The differences are
# how many formats are in flight at once, how DuckDuckGo's web search is
# paced (it is the only engine that challenges bursts), and whether a delay
# is inserted between formats. API engines are always paced by their own
# gates (Brave free tier is 1 request/second) regardless of mode.
MODES = {
    'fast': {
        'description': 'all formats at once; DuckDuckGo web search 3-wide',
        'format_workers': 10,
        'ddg_workers': 3,
        'ddg_spacing': (0.3, 0.8),
        'format_delay': (0.0, 0.0),
    },
    'balanced': {
        'description': '4 formats at once; DuckDuckGo web search 2-wide, jittered (default)',
        'format_workers': 4,
        'ddg_workers': 2,
        'ddg_spacing': (1.0, 2.5),
        'format_delay': (0.0, 0.0),
    },
    'safe': {
        'description': 'one format at a time with adaptive delays (classic telespot)',
        'format_workers': 1,
        'ddg_workers': 1,
        'ddg_spacing': (2.5, 4.5),
        'format_delay': (2.0, 4.0),
    },
}

# Minimum spacing between consecutive requests to one API, in seconds.
ENGINE_INTERVALS = {
    'google': 0.25,
    'brave': 1.05,   # free plan: 1 query/second
    'dehashed': 0.5,
    'ddg_api': 0.4,
}


class RateGate:
    """Async gate: caps concurrency and enforces a minimum interval per engine.

    ``penalty`` grows when the engine rate-limits or challenges us and decays
    on success, so a parallel run slows down only for the engine that
    complains, not for all of them.
    """

    def __init__(self, min_interval=0.0, jitter=(0.0, 0.0), concurrency=1,
                 max_penalty=15.0):
        self.min_interval = min_interval
        self.jitter = jitter
        self.max_penalty = max_penalty
        self.penalty = 0.0
        self.blocks = 0
        self.waited = 0.0
        self.closed = False   # engine given up on: let waiters through at once
        self._lock = asyncio.Lock()
        self._sem = asyncio.Semaphore(max(1, concurrency))
        self._next_at = 0.0

    async def __aenter__(self):
        await self._sem.acquire()
        if self.closed:
            return self
        async with self._lock:
            if self.closed:
                return self
            wait = self._next_at - time.monotonic()
            if wait > 0:
                self.waited += wait
                await asyncio.sleep(wait)
            spacing = self.min_interval + self.penalty + random.uniform(*self.jitter)
            self._next_at = time.monotonic() + spacing
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._sem.release()
        return False

    def widen(self):
        """Widen the spacing without counting a rate-limit event."""
        self.penalty = min(self.max_penalty, max(1.5, self.penalty * 1.8))

    def punish(self):
        """Engine rate-limited us: count it and widen the spacing."""
        self.blocks += 1
        self.widen()

    def close(self):
        """Stop pacing: callers still enter, but check their own disabled flag."""
        self.closed = True

    def reward(self):
        """Engine answered normally: relax the spacing gradually."""
        self.penalty = max(0.0, self.penalty * 0.7)


class AdaptiveRateLimiter:
    """Delay between formats in safe mode; grows on blocks, shrinks on success."""

    def __init__(self, base_delay=2.0, min_delay=1.5, max_delay=15.0):
        self.base_delay = base_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.current_delay = base_delay
        self.consecutive_successes = 0
        self.total_blocks = 0

    def record_success(self):
        self.consecutive_successes += 1
        if self.consecutive_successes >= 3:
            self.current_delay = max(self.min_delay, self.current_delay * 0.85)

    def record_block(self):
        self.consecutive_successes = 0
        self.total_blocks += 1
        self.current_delay = min(self.max_delay, self.current_delay * 1.8)

    async def wait(self):
        jitter = random.uniform(-0.5, 1.5)
        delay = max(self.min_delay, self.current_delay + jitter)
        await asyncio.sleep(delay)
        return delay

# ═══════════════════════════════════════════════════════════════════════════════
# US STATES AND LOCATION DATA
# ═══════════════════════════════════════════════════════════════════════════════

# US_STATES is imported from telespot_common.patterns.

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
# HTTP: RETRY + CAPTCHA DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def create_client():
    """Create the shared httpx.AsyncClient (connection pooling, HTTP/1.1)."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(15.0),
        follow_redirects=True,
        limits=httpx.Limits(max_connections=24, max_keepalive_connections=12),
    )


async def request_with_retry(client, method, url, max_retries=3, backoff_base=2.0,
                             api_mode=False, debug=False, **kwargs):
    """Make an HTTP request with retry logic and captcha detection.

    Retries on transient failures (429, 503, network errors) with exponential
    backoff. Detects captcha/block pages and retries with a fresh fingerprint.
    Caller-supplied headers (API keys) are kept on every attempt.

    Returns (response, was_blocked). ``was_blocked`` is True when all
    retries were exhausted on captcha/rate limiting.
    """
    caller_headers = dict(kwargs.pop('headers', None) or {})
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            fresh = get_api_headers() if api_mode else get_random_headers()
            kwargs['headers'] = merge_headers(fresh, caller_headers)

            response = await client.request(method.upper(), url, **kwargs)

            if detect_captcha(response, api_mode=api_mode):
                if debug:
                    print(f"      [DEBUG] Captcha/block detected (attempt {attempt + 1}/{max_retries + 1}), status={response.status_code}")
                if attempt < max_retries:
                    wait = backoff_base * (2 ** attempt) + random.uniform(0.5, 2.0)
                    if debug:
                        print(f"      [DEBUG] Backing off {wait:.1f}s before retry...")
                    await asyncio.sleep(wait)
                    continue
                return response, True

            if response.status_code == 429:
                if attempt < max_retries:
                    retry_after = response.headers.get('Retry-After')
                    try:
                        wait = float(retry_after) if retry_after else backoff_base * (2 ** attempt) + random.uniform(1.0, 3.0)
                    except ValueError:
                        wait = backoff_base * (2 ** attempt)
                    if debug:
                        print(f"      [DEBUG] Rate limited (429), waiting {wait:.1f}s...")
                    await asyncio.sleep(wait)
                    continue
                return response, True

            return response, False

        except (httpx.TimeoutException, httpx.TransportError) as e:
            last_exception = e
            if debug:
                # str(e) is often empty for httpx transport errors; name the type.
                print(f"      [DEBUG] Network error (attempt {attempt + 1}/{max_retries + 1}): {type(e).__name__} {e}".rstrip())
            if attempt < max_retries:
                await asyncio.sleep(backoff_base * (2 ** attempt) + random.uniform(0.5, 1.5))
                continue
            raise

    if last_exception:
        raise last_exception
    return None, True


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

# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH RUN (shared state for one investigation)
# ═══════════════════════════════════════════════════════════════════════════════

class SearchRun:
    """Holds the client, rate gates, warnings and DuckDuckGo state for one run.

    Must be created inside the running event loop (asyncio primitives bind to
    the loop on creation in older Pythons).
    """

    DDG_CHALLENGE_LIMIT = 3

    def __init__(self, client, mode, workers=None, verbose=False, debug=False):
        self.client = client
        self.mode = mode
        settings = MODES[mode]
        self.format_workers = max(1, workers or settings['format_workers'])
        self.format_delay = settings['format_delay']
        self.verbose = verbose
        self.debug = debug
        self.gates = {
            'google': RateGate(ENGINE_INTERVALS['google'], concurrency=4),
            'brave': RateGate(ENGINE_INTERVALS['brave'], concurrency=1),
            'dehashed': RateGate(ENGINE_INTERVALS['dehashed'], concurrency=2),
            'ddg_api': RateGate(ENGINE_INTERVALS['ddg_api'], concurrency=2),
            'ddg_html': RateGate(0.0, jitter=settings['ddg_spacing'],
                                 concurrency=settings['ddg_workers']),
        }
        self.format_sem = asyncio.Semaphore(self.format_workers)
        self._warned = set()
        self.ddg_challenge_streak = 0
        self.ddg_html_disabled = False
        self.ddg_challenges = 0

    def warn_once(self, key, message):
        if key not in self._warned:
            self._warned.add(key)
            print(f"  {color.warning(message)}")

    def note_ddg_challenge(self):
        """Record a fully-challenged DuckDuckGo web search for one format."""
        self.ddg_challenges += 1
        self.ddg_challenge_streak += 1
        # A challenge is not rate limiting (it is counted separately), but it
        # does mean DuckDuckGo wants more space between requests.
        self.gates['ddg_html'].widen()
        self.warn_once('ddg-challenge',
                       'DuckDuckGo answered with a bot challenge instead of results (retrying each format once)')
        if self.ddg_challenge_streak >= self.DDG_CHALLENGE_LIMIT and not self.ddg_html_disabled:
            self.ddg_html_disabled = True
            # Formats already queued on the gate must not sit out its widened
            # spacing just to find out the fallback is off.
            self.gates['ddg_html'].close()
            self.warn_once('ddg-disabled',
                           'DuckDuckGo is challenging this client; skipping its web search for the remaining formats. '
                           'Try again later or from another network. Google/Brave keys give reliable results.')

    def note_ddg_success(self):
        self.ddg_challenge_streak = 0
        self.gates['ddg_html'].reward()

    def total_blocks(self):
        return sum(g.blocks for g in self.gates.values())

# ═══════════════════════════════════════════════════════════════════════════════
# API SEARCH FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def search_google_api(run, query, api_key, cse_id, num_results=10):
    """Search using Google Custom Search API with retry and captcha detection"""
    results = []
    if not api_key or not cse_id:
        return results

    gate = run.gates['google']
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        # Google CSE honors quoted phrases natively inside `q`. Only use
        # exactTerms for the bare digits-only format, where it usefully narrows
        # without the over-filtering a quoted phone format triggers.
        params = {'key': api_key, 'cx': cse_id, 'q': query, 'num': min(num_results, 10)}
        digits_only = re.sub(r'\D', '', query)
        if query.strip() == digits_only and digits_only:
            params['exactTerms'] = digits_only

        async with gate:
            response, was_blocked = await request_with_retry(
                run.client, 'get', url, params=params, api_mode=True, debug=run.debug
            )

        if was_blocked:
            gate.punish()
            run.warn_once('google-blocked', 'Google API rate limited - backing off')
            return results

        if run.debug:
            print(f"    [DEBUG] Google API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Google',
                })
                if run.verbose:
                    print(f"      [Google] {item.get('title', '')[:60]}")
            gate.reward()
        elif response.status_code == 429:
            gate.punish()
            run.warn_once('google-quota', 'Google API quota exceeded')
        else:
            # 400 = malformed key/cx, 403 = key invalid, API not enabled or
            # daily quota exhausted. Always say so instead of hiding it.
            run.warn_once('google-error', f'Google API error {response.status_code}: {_api_error_message(response)}')

    except Exception as e:
        if run.debug:
            print(f"    [DEBUG] Google exception: {e}")

    return results


async def search_brave_api(run, query, api_key, num_results=10):
    """Search using the Brave Search API (free tier: ~2000/month, 1 query/s)."""
    results = []
    if not api_key:
        return results

    gate = run.gates['brave']
    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {'X-Subscription-Token': api_key, 'Accept': 'application/json'}
        params = {'q': query, 'count': min(num_results, 20)}

        async with gate:
            response, was_blocked = await request_with_retry(
                run.client, 'get', url, headers=headers, params=params, api_mode=True, debug=run.debug
            )

        if was_blocked:
            gate.punish()
            run.warn_once('brave-blocked', 'Brave API rate limited - backing off')
            return results

        if run.debug:
            print(f"    [DEBUG] Brave API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            for item in data.get('web', {}).get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('description', ''),
                    'source': 'Brave',
                })
                if run.verbose:
                    print(f"      [Brave] {item.get('title', '')[:60]}")
            gate.reward()
        elif response.status_code in (401, 403):
            run.warn_once('brave-auth', 'Brave API key invalid or subscription inactive')
        elif response.status_code == 429:
            gate.punish()
            run.warn_once('brave-quota', 'Brave API quota exceeded')
        else:
            run.warn_once('brave-error', f'Brave API error {response.status_code}: {_api_error_message(response)}')

    except Exception as e:
        if run.debug:
            print(f"    [DEBUG] Brave exception: {e}")

    return results


async def search_duckduckgo_api(run, query, num_results=10):
    """DuckDuckGo Instant Answer API, then the lite web search as fallback.

    The Instant Answer API only returns knowledge-graph style results, which
    are usually empty for phone numbers; the lite HTML search supplies real
    web results when that happens.
    """
    results = []

    # --- Phase 1: Instant Answer API ---
    try:
        url = "https://api.duckduckgo.com/"
        params = {'q': query, 'format': 'json', 'no_html': 1, 'skip_disambig': 1}

        async with run.gates['ddg_api']:
            response, was_blocked = await request_with_retry(
                run.client, 'get', url, params=params, api_mode=True, debug=run.debug
            )

        if was_blocked:
            if run.debug:
                print("    [DEBUG] DuckDuckGo API blocked, trying HTML fallback...")
        elif response is not None and 200 <= response.status_code < 300:
            # The API answers with HTTP 202 (not 200) for most queries while
            # still returning a full JSON body, so accept any 2xx.
            if run.debug:
                print(f"    [DEBUG] DuckDuckGo API status: {response.status_code}")
            data = response.json()

            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Result'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'source': 'DuckDuckGo',
                })
                if run.verbose:
                    print(f"      [DuckDuckGo] {data.get('Heading', '')[:60]}")

            for topic in data.get('RelatedTopics', [])[:num_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '')[:80],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'DuckDuckGo',
                    })
                    if run.verbose:
                        print(f"      [DuckDuckGo] {topic.get('Text', '')[:60]}")

            for item in data.get('Results', [])[:num_results]:
                results.append({
                    'title': item.get('Text', ''),
                    'url': item.get('FirstURL', ''),
                    'snippet': item.get('Text', ''),
                    'source': 'DuckDuckGo',
                })

    except Exception as e:
        if run.debug:
            print(f"    [DEBUG] DuckDuckGo API exception: {e}")

    # --- Phase 2: HTML fallback when the API returns few/no results ---
    if len(results) < 3 and not run.ddg_html_disabled:
        results.extend(await _search_duckduckgo_html(run, query, num_results))

    return results


async def _search_duckduckgo_html(run, query, num_results=10):
    """Scrape DuckDuckGo's lite search page for real web results."""
    results = []

    try:
        url = "https://lite.duckduckgo.com/lite/"
        params = {'q': query}

        async with run.gates['ddg_html']:
            if run.ddg_html_disabled:
                return results
            response, was_blocked = await request_with_retry(
                run.client, 'get', url, params=params, max_retries=1, debug=run.debug
            )

        if was_blocked:
            if run.debug:
                print("    [DEBUG] DuckDuckGo HTML search blocked")
            if response is not None and is_bot_challenge_page(response.text):
                # A bot challenge is not rate limiting; it is intermittent,
                # so it is tracked separately and only widens DDG's own gate.
                run.note_ddg_challenge()
            else:
                run.gates['ddg_html'].punish()
            return results

        if response is not None and 200 <= response.status_code < 300:
            body = response.text

            if is_bot_challenge_page(body):
                # HTTP 202 challenge page that slipped past detect_captcha.
                run.note_ddg_challenge()
                return results

            run.note_ddg_success()

            # lite markup (single-quoted class attributes):
            #   <a rel="nofollow" href="...uddg=..." class='result-link'>title</a>
            #   <td class='result-snippet'>snippet text</td>
            link_pattern = r"<a[^>]*href=\"([^\"]*)\"[^>]*class=['\"]result-link['\"][^>]*>(.*?)</a>"
            links = re.findall(link_pattern, body, re.DOTALL)
            snippet_pattern = r"<td[^>]*class=['\"]result-snippet['\"][^>]*>(.*?)</td>"
            snippets = re.findall(snippet_pattern, body, re.DOTALL)

            if not links:
                lowered = body.lower()
                if 'no results' in lowered or 'no more results' in lowered:
                    if run.debug:
                        print("    [DEBUG] DuckDuckGo HTML: no results for this format")
                else:
                    # 2xx but nothing parsed usually means DDG changed its
                    # markup again. Warn, don't swallow it.
                    run.warn_once('ddg-parse',
                                  f'DuckDuckGo HTML: HTTP {response.status_code} but 0 results parsed (selectors may be stale)')

            for i, (href, title) in enumerate(links[:num_results]):
                clean_title = re.sub(r'<[^>]+>', '', title).strip()
                clean_snippet = ''
                if i < len(snippets):
                    clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()

                actual_url = href
                if 'uddg=' in href:
                    url_match = re.search(r'uddg=([^&]+)', href)
                    if url_match:
                        actual_url = unquote(url_match.group(1))

                if clean_title and actual_url:
                    results.append({
                        'title': clean_title,
                        'url': actual_url,
                        'snippet': clean_snippet,
                        'source': 'DuckDuckGo',
                    })
                    if run.verbose:
                        print(f"      [DuckDuckGo] {clean_title[:60]}")

            if run.debug:
                print(f"    [DEBUG] DuckDuckGo HTML returned {len(results)} results")

    except Exception as e:
        if run.debug:
            print(f"    [DEBUG] DuckDuckGo HTML exception: {e}")

    return results


async def search_dehashed_api(run, query, api_key):
    """Search the Dehashed v2 breach database (optional)."""
    results = []
    if not api_key:
        return results

    gate = run.gates['dehashed']
    try:
        # v2: POST JSON to /v2/search with a Dehashed-Api-Key header. The key
        # is the raw key; tolerate a legacy "email:key" value.
        url = "https://api.dehashed.com/v2/search"
        raw_key = api_key.split(':', 1)[1] if ':' in api_key else api_key
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
                   'Dehashed-Api-Key': raw_key}
        payload = {'query': f'phone:"{query}"'}

        async with gate:
            response, was_blocked = await request_with_retry(
                run.client, 'post', url, json=payload, headers=headers, api_mode=True, debug=run.debug
            )

        if was_blocked:
            gate.punish()
            run.warn_once('dehashed-blocked', 'Dehashed API rate limited')
            return results

        if run.debug:
            print(f"    [DEBUG] Dehashed API status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            def _flatten(v, default=''):
                if isinstance(v, list):
                    return ' '.join(str(x) for x in v) if v else default
                return v if v else default

            for entry in data.get('entries', [])[:10]:
                raw_name = _flatten(entry.get('name', ''))
                raw_username = _flatten(entry.get('username', ''))
                email = _flatten(entry.get('email', ''), 'N/A')
                database = _flatten(entry.get('database_name', ''), 'N/A')
                name = f"{raw_name} {raw_username}".strip()
                results.append({
                    'title': name or 'Dehashed Entry',
                    'url': database if database != 'N/A' else '',
                    'snippet': f"Email: {email} | Database: {database}",
                    'source': 'Dehashed',
                })
                if run.verbose:
                    print(f"      [Dehashed] {name[:60]}")
            gate.reward()
        elif response.status_code in (401, 403):
            run.warn_once('dehashed-auth', 'Dehashed API key invalid or out of credits')
        else:
            run.warn_once('dehashed-error', f'Dehashed API error {response.status_code}: {_api_error_message(response)}')

    except Exception as e:
        if run.debug:
            print(f"    [DEBUG] Dehashed exception: {e}")

    return results

# ═══════════════════════════════════════════════════════════════════════════════
# PATTERN EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

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

    name_counter = Counter(extract_names(combined_text))
    location_counter = Counter(extract_locations(combined_text))
    username_counter = Counter(extract_usernames(combined_text))
    email_counter = Counter(extract_emails(combined_text))

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
        'emails': email_counter.most_common(10),
        'confidence': confidence,
        'confidence_pct': confidence_pct,
    }


def deduplicate_results(all_results):
    """Remove duplicate results across all format groups by URL."""
    return deduplicate_results_dict(all_results)

# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def print_results(patterns, phone_number, all_results, verbose=False):
    """Print formatted results"""
    print(f"\n{'='*70}")
    print(color.header("PATTERN ANALYSIS SUMMARY"))
    print(f"{'='*70}\n")

    conf_color = color.success if patterns['confidence'] == 'HIGH' else (
        color.warning if patterns['confidence'] == 'MEDIUM' else color.error)
    conf_text = f"{patterns['confidence']} ({patterns['confidence_pct']}%)"
    print(f"Confidence Score: {conf_color(conf_text)}\n")

    print(f"Total Results Found: {patterns['total_results']}")
    print(f"Unique URLs: {patterns['unique_urls']}\n")

    if patterns['results_by_source']:
        print(color.header("Results by Source:"))
        for source, count in sorted(patterns['results_by_source'].items(), key=lambda x: -x[1]):
            print(f"  • {source}: {count} results")
        print()

    if patterns['names']:
        print(color.header("Names Found:"))
        for name, count in patterns['names']:
            indicator = " ⭐" if count >= 2 else ""
            print(f"  • {name}: mentioned {count} time(s){indicator}")
        print()

    if patterns['locations']:
        print(color.header("Locations Mentioned:"))
        for location, count in patterns['locations']:
            indicator = " ⭐" if count >= 2 else ""
            print(f"  • {location}: {count} occurrence(s){indicator}")
        print()

    if patterns['usernames']:
        print(color.header("Usernames Found:"))
        for username, count in patterns['usernames']:
            indicator = " ⭐" if count >= 2 else ""
            print(f"  • @{username}: {count} occurrence(s){indicator}")
        print()

    if patterns.get('emails'):
        print(color.header("Emails Found:"))
        for email, count in patterns['emails']:
            indicator = " ⭐" if count >= 2 else ""
            print(f"  • {email}: {count} occurrence(s){indicator}")
        print()

    print(color.header("Key Insights:"))
    if patterns['names']:
        print(f"  • Most associated name: {color.success(patterns['names'][0][0])}")
    if patterns['locations']:
        print(f"  • Most associated location: {color.success(patterns['locations'][0][0])}")
    if not patterns['names'] and not patterns['locations']:
        print(f"  • {color.warning('No clear patterns found in results')}")

    print(f"\n{'='*70}\n")

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


def save_json_results(phone_number, formats, all_results, patterns, filename=None, meta=None):
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
    if meta:
        output['run'] = meta

    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)

    return filename


def save_txt_results(phone_number, formats, all_results, patterns, filename=None, meta=None):
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
        if meta:
            f.write(f"Mode: {meta.get('mode')} ({meta.get('elapsed_seconds')}s)\n")
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

        for label, key, prefix in (("Names Found", 'names', ''), ("Locations Mentioned", 'locations', ''),
                                   ("Usernames Found", 'usernames', '@'), ("Emails Found", 'emails', '')):
            if patterns.get(key):
                f.write(f"{label}:\n")
                for item, count in patterns[key]:
                    f.write(f"  - {prefix}{item}: {count} occurrence(s)\n")
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

    # Speed mode
    print(color.info("\nDefault Speed Mode"))
    for name, settings in MODES.items():
        print(f"  {name:<9} {settings['description']}")
    print(f"  Current: {config.get('default_mode', 'balanced')}")
    mode = input("  Enter mode (fast/balanced/safe) or Enter to keep: ").strip().lower()
    if mode in MODES:
        config.set('default_mode', mode)
    elif mode:
        print(color.warning(f"  Unknown mode '{mode}', keeping {config.get('default_mode', 'balanced')}"))

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
            print(f"Update failed: {result.stderr}")
            return False
        print("Not a git repository. Please run:")
        print(f"  git clone {REPO_URL}")
        return False

    except Exception as e:
        print(f"Update error: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SEARCH FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

async def search_one_format(run, index, total, fmt, query, keys, include_dehashed, limiter=None):
    """Search every configured engine for one format, concurrently."""
    async with run.format_sem:
        started = time.monotonic()
        blocks_before = run.total_blocks() + run.ddg_challenges
        tasks = {}
        if keys['google_key'] and keys['google_cse']:
            tasks['Google'] = search_google_api(run, query, keys['google_key'], keys['google_cse'])
        if keys['brave_key']:
            tasks['Brave'] = search_brave_api(run, query, keys['brave_key'])
        tasks['DuckDuckGo'] = search_duckduckgo_api(run, query)
        if include_dehashed and keys['dehashed_key']:
            tasks['Dehashed'] = search_dehashed_api(run, re.sub(r'\D', '', fmt), keys['dehashed_key'])

        outcomes = await asyncio.gather(*tasks.values(), return_exceptions=True)

        format_results = []
        parts = []
        for name, outcome in zip(tasks.keys(), outcomes):
            if isinstance(outcome, Exception):
                if run.debug:
                    print(f"    [DEBUG] {name} failed: {outcome}")
                parts.append(f"{name} err")
                continue
            format_results.extend(outcome)
            parts.append(f"{name} {len(outcome)}")

        elapsed = time.monotonic() - started
        count_text = color.success(f"{len(format_results)} results") if format_results else color.dim("0 results")
        print(f"{color.header(f'[{index}/{total}]')} {fmt:<20} {' · '.join(parts)}  → {count_text} {color.dim(f'({elapsed:.1f}s)')}")

        if limiter is not None:
            if run.total_blocks() + run.ddg_challenges > blocks_before:
                limiter.record_block()
            else:
                limiter.record_success()
            if index < total:
                waited = await limiter.wait()
                print(f"  {color.dim(f'waited {waited:.1f}s (safe mode, delay={limiter.current_delay:.1f}s)')}")

        return fmt, format_results


async def run_search_async(phone_number, args):
    """Search orchestration: all engines per format, formats in parallel by mode."""
    country_code = args.country or config.get('default_country_code', '+1')

    formats = generate_phone_formats(phone_number, country_code)
    if not formats:
        print(color.error("Invalid phone number format. Please enter a valid 10-digit number."))
        return None

    mode = args.mode or config.get('default_mode', 'balanced')
    if mode not in MODES:
        mode = 'balanced'

    print(f"\nSearching for: {color.header(phone_number)}")
    print(f"Country code: {country_code}")
    print(f"Using {len(formats)} format variations")
    print(f"Mode: {color.info(mode)} - {MODES[mode]['description']}\n")

    config.display_api_status()

    if args.dtmf:
        print(f"DTMF: {get_dtmf_representation(phone_number)}\n")

    keys = {
        'google_key': config.get('google_api_key', ''),
        'google_cse': config.get('google_cse_id', ''),
        'brave_key': config.get('brave_api_key', ''),
        'dehashed_key': config.get('dehashed_api_key', ''),
    }
    if args.dehashed and not keys['dehashed_key']:
        print(color.warning("--dehashed given but no Dehashed key configured (run --setup)\n"))
    if mode == 'fast' and not (keys['google_key'] and keys['google_cse']) and not keys['brave_key']:
        print(color.warning("Fast mode with DuckDuckGo only: bursts are more likely to be challenged. "
                            "Balanced mode or a Google/Brave key gives better results.\n"))

    keyword_suffix = f" {args.keyword}" if args.keyword else ""
    site_prefix = f"site:{args.site} " if args.site else ""

    started = time.monotonic()
    async with create_client() as client:
        run = SearchRun(client, mode, workers=args.workers, verbose=args.verbose, debug=args.debug)

        limiter = None
        if run.format_workers == 1 and MODES[mode]['format_delay'][1] > 0:
            limiter = AdaptiveRateLimiter(base_delay=float(config.get('delay_seconds', '2')))

        coros = [
            search_one_format(run, i, len(formats), fmt, f"{site_prefix}{fmt}{keyword_suffix}",
                              keys, args.dehashed, limiter)
            for i, fmt in enumerate(formats, 1)
        ]
        outcomes = await asyncio.gather(*coros, return_exceptions=True)

    elapsed = time.monotonic() - started

    all_results = {}
    for fmt, outcome in zip(formats, outcomes):
        if isinstance(outcome, Exception):
            if args.debug:
                print(f"    [DEBUG] format {fmt} failed: {outcome}")
            all_results[fmt] = []
        else:
            all_results[outcome[0]] = outcome[1]

    raw_total = sum(len(r) for r in all_results.values())
    all_results = deduplicate_results(all_results)
    deduped_total = sum(len(r) for r in all_results.values())

    print(f"\n{color.header(f'Total Results: {deduped_total}')}", end='')
    if deduped_total < raw_total:
        print(f" ({raw_total - deduped_total} duplicates removed)", end='')
    print(f"  {color.dim(f'in {elapsed:.1f}s, mode={mode}')}")

    blocks = run.total_blocks()
    if blocks or run.ddg_challenges:
        bits = []
        if blocks:
            bits.append(f"rate-limit events: {blocks}")
        if run.ddg_challenges:
            bits.append(f"DuckDuckGo challenges: {run.ddg_challenges}")
        print(color.warning(f"{', '.join(bits)} (engine spacing auto-adjusted)"))
    print()

    print("Analyzing patterns...")
    patterns = analyze_results(all_results, args.verbose)
    print_results(patterns, phone_number, all_results, args.verbose)

    if args.summary:
        print(color.header("SUMMARY COMPARISON"))
        print("=" * 70)
        print("\nItems appearing in multiple results (higher confidence):\n")
        for label, key, prefix in (("NAME", 'names', ''), ("LOCATION", 'locations', ''),
                                   ("USERNAME", 'usernames', '@'), ("EMAIL", 'emails', '')):
            for item, count in patterns.get(key, []):
                if count >= 2:
                    bar = "█" * min(count, 20)
                    print(f"  {label:<8} | {bar} | {prefix}{item} ({count}x)")
        print()

    meta = {'mode': mode, 'elapsed_seconds': round(elapsed, 1), 'format_workers': run.format_workers,
            'rate_limit_events': blocks, 'ddg_challenges': run.ddg_challenges}

    if args.output:
        if args.output.endswith('.json'):
            filename = save_json_results(phone_number, formats, all_results, patterns, args.output, meta)
        else:
            filename = save_txt_results(phone_number, formats, all_results, patterns, args.output, meta)
        print(color.success(f"Results saved to: {filename}"))

    return {
        'phone_number': phone_number,
        'formats': formats,
        'results': all_results,
        'patterns': patterns,
        'meta': meta,
    }


def run_search(phone_number, args):
    """Synchronous wrapper around the async search (keeps the old entrypoint)."""
    global color
    if args.no_color:
        color = ColorMode('off')
    elif args.colorful:
        color = ColorMode('colorful')
    else:
        color = ColorMode('normal')
    return asyncio.run(run_search_async(phone_number, args))

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
║  Parallel search across Google, Brave and DuckDuckGo with        ║
║  pattern recognition for names, locations, usernames, emails.    ║
╚══════════════════════════════════════════════════════════════════╝
''',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
EXAMPLES:
  telespot 2155551234                    Balanced search (default)
  telespot 2155551234 --fast             Everything at once (~5-15s)
  telespot 2155551234 --safe             One format at a time, adaptive delays
  telespot 2155551234 -k "John Smith"    Search with keywords
  telespot 2155551234 -s whitepages.com  Search specific site
  telespot 2155551234 --dehashed         Include breach database
  telespot 2155551234 -v -o results.json Verbose + JSON output
  telespot +442071234567 -c +44          International number
  telespot --setup                       Configure API keys and default mode

SPEED MODES:
  fast      all formats at once; DuckDuckGo web search 3-wide
  balanced  4 formats at once; DuckDuckGo 2-wide with jitter (default)
  safe      one format at a time with adaptive delays (classic telespot)
  Every mode calls all engines concurrently per format. API engines are
  paced by their own limits (Brave free tier: 1 query/second).

API SETUP:
  Run 'telespot --setup' to configure your API keys.
  At minimum, configure Google or Brave for best results.
  DuckDuckGo works without an API key.

SEARCH ENGINES:
  • Google Custom Search API (requires API key + CSE ID)
  • Brave Search API (requires subscription token; free tier ~2000/mo)
  • DuckDuckGo Instant Answers + lite web search (no key required)
  • Dehashed (optional, requires API key)

For more information: https://github.com/thumpersecure/Telespot
''')

    parser.add_argument('phone', nargs='?', help='Phone number to search')

    search = parser.add_argument_group('Search Options')
    search.add_argument('-k', '--keyword', metavar='WORD', help='Add keyword to search')
    search.add_argument('-s', '--site', metavar='DOMAIN', help='Limit search to specific site')
    search.add_argument('-c', '--country', metavar='CODE', help='Country code (default: +1)')
    search.add_argument('--dehashed', action='store_true', help='Include Dehashed breach search')

    speed = parser.add_argument_group('Speed Options')
    speed.add_argument('--mode', choices=sorted(MODES), metavar='MODE',
                       help='fast, balanced or safe (default: balanced, or default_mode in config)')
    speed.add_argument('--fast', action='store_const', const='fast', dest='mode',
                       help='Shortcut for --mode fast')
    speed.add_argument('--safe', action='store_const', const='safe', dest='mode',
                       help='Shortcut for --mode safe')
    speed.add_argument('--workers', type=int, metavar='N',
                       help='Formats searched concurrently (overrides the mode default)')

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

def main(argv=None):
    """Main entry point"""
    global color

    parser = create_parser()
    args = parser.parse_args(argv)

    if args.no_color:
        color = ColorMode('off')
    elif args.colorful:
        color = ColorMode('colorful')
    else:
        color = ColorMode('normal')

    if not args.no_color:
        print(get_ascii_logo())
    else:
        print(get_ascii_logo_mono())

    if args.setup:
        interactive_setup()
        return 0

    if args.api_status:
        config.display_api_status()
        return 0

    if args.update:
        update_from_repo()
        return 0

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

    try:
        result = run_search(phone_number, args)

        if result and not args.output and sys.stdin.isatty():
            save = input("\nSave results to file? (y/N): ").strip().lower()
            if save == 'y':
                fmt = input("Format (txt/json) [txt]: ").strip().lower() or 'txt'
                saver = save_json_results if fmt == 'json' else save_txt_results
                filename = saver(phone_number, result['formats'], result['results'],
                                 result['patterns'], meta=result.get('meta'))
                print(color.success(f"Results saved to: {filename}"))

        return 0

    except KeyboardInterrupt:
        print(color.warning("\n\nSearch interrupted by user."))
        return 130


if __name__ == "__main__":
    sys.exit(main())
