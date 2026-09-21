#!/usr/bin/env python3
"""
telespotx - Fast parallel phone number OSINT tool
v0.4.0

Uses httpx + asyncio for parallel API requests.
Includes captcha detection, retry logic, and DuckDuckGo HTML fallback.
United States phone numbers only (+1).
"""

import argparse
import asyncio
import json
import os
import random
import re
import sys
from datetime import datetime
from urllib.parse import unquote

try:
    import httpx
except ImportError:
    print("telespotx requires httpx. Install with: pip install httpx")
    sys.exit(1)

from telespot_common.colors import Colors
from telespot_common.config import read_simple_kv_config, resolve_config_path
from telespot_common.http_fingerprint import (
    detect_captcha,
    get_api_headers,
    get_random_headers,
    is_bot_challenge_page,
    merge_headers,
)
from telespot_common.patterns import (
    extract_emails,
    extract_locations,
    extract_names,
    extract_usernames,
)

# Version
VERSION = "0.4.0"


def print_banner(no_color=False):
    """Print the telespotx banner in red, white, and blue."""
    if no_color:
        banner = f"""
  _       _                      _
 | |_ ___| | ___  ___ _ __   ___ | |___  __
 | __/ _ \\ |/ _ \\/ __| '_ \\ / _ \\| __\\ \\/ /
 | ||  __/ |  __/\\__ \\ |_) | (_) | |_ >  <
  \\__\\___|_|\\___||___/ .__/ \\___/ \\__/_/\\_\\
                     |_|        v{VERSION}
        """
        print(banner)
    else:
        r = Colors.RED
        w = Colors.WHITE
        b = Colors.BLUE
        reset = Colors.RESET

        print(f"""
  {r}_{w} _       {b}_{r}                      {w}_{b} _
 {r}| |{w}_ ___{b}| |{r} ___  ___ {w}_ __   {b}___ {r}| |{w}___{b}  __
 {r}| __{w}/ _ \\{b}\\ |{r}/ _ \\/ __{w}| '_ \\ {b}/ _ \\{r}| __{w}\\ \\{b}/ /
 {r}| |{w}|  __/{b}| |{r}  __/{w}\\__ \\ |_) {b}| (_) {r}| |{w}_ >{b}  <
  {r}\\__\\{w}___|{b}_|{r}\\___||{w}___/ .__/ {b}\\___/ {r}\\__/{w}_/{b}\\_\\
                     {w}|_|        {b}v{VERSION}{reset}
        """)

def load_config():
    """Load API configuration from .telespot_config file."""
    defaults = {
        "google_api_key": "",
        "google_cse_id": "",
        "brave_api_key": "",
        "dehashed_api_key": "",
        "default_country_code": "+1",
    }

    config_path = resolve_config_path(local_dir=os.path.dirname(os.path.abspath(__file__)))
    return read_simple_kv_config(config_path, defaults)

def generate_formats(phone):
    """Generate 6 unique US phone number format variations."""
    digits = re.sub(r'\D', '', phone)

    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    elif len(digits) != 10:
        print(f"Error: Invalid US phone number. Expected 10 digits, got {len(digits)}.")
        return []

    area = digits[:3]
    exchange = digits[3:6]
    subscriber = digits[6:]

    formats = [
        f"{area}-{exchange}-{subscriber}",           # 888-555-1212
        f"{digits}",                                  # 8885551212
        f"({area}) {exchange}-{subscriber}",         # (888) 555-1212
        f"+1{digits}",                               # +18885551212
        f'"{area}-{exchange}-{subscriber}"',         # "888-555-1212"
        f'"{digits}"',                               # "8885551212"
    ]

    return formats

def print_api_status(config, no_color=False):
    """Display API configuration status."""
    c = Colors if not no_color else type('', (), {k: '' for k in dir(Colors) if not k.startswith('_')})()

    print(f"\n{c.BOLD}API Configuration Status:{c.RESET}")
    print("-" * 40)

    configured = 0
    total = 4

    apis = [
        ('Google', bool(config.get('google_api_key') and config.get('google_cse_id'))),
        ('Brave', bool(config.get('brave_api_key'))),
        ('DuckDuckGo', True),
        ('Dehashed', bool(config.get('dehashed_api_key'))),
    ]

    for name, is_configured in apis:
        if is_configured:
            print(f"  {c.GREEN}[+]{c.RESET} {name}: CONFIGURED")
            configured += 1
        else:
            print(f"  {c.RED}[-]{c.RESET} {name}: NOT CONFIGURED")

    print("-" * 40)
    print(f"  {configured}/{total} APIs configured")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC SEARCH FUNCTIONS WITH RETRY AND CAPTCHA DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

async def async_request_with_retry(client, method, url, max_retries=2, backoff_base=1.5, debug=False, **kwargs):
    """Make an async HTTP request with retry logic and captcha detection.

    Returns (response, was_blocked) tuple.
    """
    # Read the API-mode flag once. It used to be popped inside the loop, so
    # retries fell back to browser headers, and the caller's headers were
    # replaced wholesale on retry, which dropped the Brave/Dehashed auth
    # headers and turned every retry into a guaranteed 401.
    api_mode = bool(kwargs.pop('_api_mode', False))
    caller_headers = dict(kwargs.get('headers') or {})

    for attempt in range(max_retries + 1):
        try:
            # Fresh fingerprint on each attempt, merged under caller headers.
            fresh = get_api_headers() if api_mode else get_random_headers()
            kwargs['headers'] = merge_headers(fresh, caller_headers)

            if 'timeout' not in kwargs:
                kwargs['timeout'] = 12.0

            if method == 'get':
                response = await client.get(url, **kwargs)
            else:
                response = await client.post(url, **kwargs)

            if detect_captcha(response, api_mode=api_mode):
                if debug:
                    print(f"      [DEBUG] Captcha/block detected (attempt {attempt + 1}), status={response.status_code}")
                if attempt < max_retries:
                    await asyncio.sleep(backoff_base * (2 ** attempt) + random.uniform(0.5, 1.5))
                    continue
                return response, True

            if response.status_code == 429:
                if attempt < max_retries:
                    wait = backoff_base * (2 ** attempt) + random.uniform(1.0, 2.0)
                    if debug:
                        print(f"      [DEBUG] Rate limited, waiting {wait:.1f}s...")
                    await asyncio.sleep(wait)
                    continue
                return response, True

            return response, False

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if debug:
                print(f"      [DEBUG] Network error (attempt {attempt + 1}): {e}")
            if attempt < max_retries:
                await asyncio.sleep(backoff_base * (2 ** attempt))
                continue
            raise

    return None, True


async def search_google(client, query, config, debug=False):
    """Search using Google Custom Search API with retry."""
    api_key = config.get('google_api_key')
    cse_id = config.get('google_cse_id')

    if not api_key or not cse_id:
        return []

    url = "https://www.googleapis.com/customsearch/v1"

    # Google CSE honors quoted phrases natively in `q`, so pass the query
    # through unchanged. Only use exactTerms for the bare digits-only format
    # (quoted phone formats over-filter to near-zero when forced via exactTerms).
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': 10,
    }

    digits_only = re.sub(r'\D', '', query)
    if query.strip() == digits_only and digits_only:
        params['exactTerms'] = digits_only

    try:
        response, was_blocked = await async_request_with_retry(
            client, 'get', url, params=params, _api_mode=True, debug=debug
        )

        if was_blocked:
            if debug:
                print(f"    [DEBUG] Google blocked/rate limited")
            return []

        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Google'
                })
            if debug:
                print(f"    [DEBUG] Google returned {len(results)} results")
            return results
        _warn_once('google', f"Google API error {response.status_code}: {_api_error_message(response)}")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Google error: {e}")
    return []


_warned = set()


def _warn_once(key, message):
    """Print a warning a single time per run (formats run in parallel)."""
    if key not in _warned:
        _warned.add(key)
        print(f"  {Colors.YELLOW}Warning: {message}{Colors.RESET}")


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

async def search_brave(client, query, config, debug=False):
    """Search using the Brave Search API with retry.

    Replaces the retired Bing Search API (api.bing.microsoft.com/v7.0/search,
    shut down Aug 2025). Brave free tier ~2000 queries/month; needs the
    X-Subscription-Token header.
    """
    api_key = config.get('brave_api_key')

    if not api_key:
        return []

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = get_api_headers()
    headers['X-Subscription-Token'] = api_key
    headers['Accept'] = 'application/json'
    params = {'q': query, 'count': 10}

    try:
        response, was_blocked = await async_request_with_retry(
            client, 'get', url, params=params, headers=headers, _api_mode=True, debug=debug
        )

        if was_blocked:
            if debug:
                print(f"    [DEBUG] Brave blocked/rate limited")
            return []

        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get('web', {}).get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('description', ''),
                    'source': 'Brave'
                })
            if debug:
                print(f"    [DEBUG] Brave returned {len(results)} results")
            return results
        if response.status_code in (401, 403):
            _warn_once('brave', 'Brave API key invalid or subscription inactive')
        else:
            _warn_once('brave', f"Brave API error {response.status_code}: {_api_error_message(response)}")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Brave error: {e}")
    return []

async def search_duckduckgo(client, query, debug=False):
    """Search DuckDuckGo with Instant Answer API + HTML fallback."""
    results = []

    # Phase 1: Instant Answer API
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1,
        }

        response, was_blocked = await async_request_with_retry(
            client, 'get', url, params=params, _api_mode=True, debug=debug
        )

        # The Instant Answer API now returns HTTP 202 (not 200) with a full
        # JSON body for most queries; accept any 2xx.
        if not was_blocked and response is not None and 200 <= response.status_code < 300:
            data = response.json()

            if data.get('AbstractText'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Result'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('AbstractText', ''),
                    'source': 'DuckDuckGo'
                })

            for topic in data.get('RelatedTopics', [])[:5]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '')[:50],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'DuckDuckGo'
                    })

            if debug:
                print(f"    [DEBUG] DuckDuckGo API returned {len(results)} results")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] DuckDuckGo API error: {e}")

    # Phase 2: HTML fallback when API returns few results
    if len(results) < 3:
        html_results = await _search_duckduckgo_html(client, query, debug)
        results.extend(html_results)

    return results


async def _search_duckduckgo_html(client, query, debug=False):
    """Scrape DuckDuckGo HTML lite search for actual web results."""
    results = []

    try:
        # lite endpoint (GET) is more scrape-friendly than the old
        # html.duckduckgo.com POST form, which no longer returns the
        # result__a/result__snippet markup to non-browser clients.
        url = "https://lite.duckduckgo.com/lite/"
        params = {'q': query}

        response, was_blocked = await async_request_with_retry(
            client, 'get', url, params=params, max_retries=1, debug=debug
        )

        if was_blocked:
            if debug:
                print(f"    [DEBUG] DuckDuckGo HTML blocked")
            if response is not None and is_bot_challenge_page(response.text):
                _warn_once('ddg-challenge', 'DuckDuckGo answered with a bot challenge instead of results. '
                           'Try again later or from another network; Google/Brave keys give reliable results.')
            return results

        if response is not None and 200 <= response.status_code < 300:
            body = response.text

            if is_bot_challenge_page(body):
                # HTTP 202 "bots use DuckDuckGo too" page.
                _warn_once('ddg-challenge', 'DuckDuckGo answered with a bot challenge instead of results. '
                           'Try again later or from another network; Google/Brave keys give reliable results.')
                return results

            # lite markup (single-quoted class attrs):
            #   <a rel="nofollow" href="...uddg=..." class='result-link'>title</a>
            #   <td class='result-snippet'>snippet</td>
            link_pattern = r"<a[^>]*href=\"([^\"]*)\"[^>]*class=['\"]result-link['\"][^>]*>(.*?)</a>"
            links = re.findall(link_pattern, body, re.DOTALL)

            snippet_pattern = r"<td[^>]*class=['\"]result-snippet['\"][^>]*>(.*?)</td>"
            snippets = re.findall(snippet_pattern, body, re.DOTALL)

            if not links and 'no results' not in body.lower():
                # 2xx but nothing parsed => markup likely changed. Warn once.
                _warn_once('ddg-parse', f"DuckDuckGo HTML returned {response.status_code} but 0 results parsed (selectors may be stale)")

            for i, (href, title) in enumerate(links[:10]):
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
                        'source': 'DuckDuckGo'
                    })

            if debug:
                print(f"    [DEBUG] DuckDuckGo HTML returned {len(results)} results")

    except Exception as e:
        if debug:
            print(f"    [DEBUG] DuckDuckGo HTML error: {e}")

    return results


def _flatten_field(v, default=''):
    """Dehashed v2 returns most fields as lists of strings; flatten to str."""
    if isinstance(v, list):
        return ' '.join(str(x) for x in v) if v else default
    return v if v else default


async def search_dehashed(client, query, config, debug=False):
    """Search using the Dehashed v2 API with retry.

    v2: POST JSON to /v2/search with a Dehashed-Api-Key header (v1 GET +
    basic-auth is retired). Response 'name'/'username'/'email' are now lists.
    """
    api_key = config.get('dehashed_api_key')

    if not api_key:
        return []

    # v2 uses the raw key; tolerate a legacy "email:key" value.
    raw_key = api_key.split(':', 1)[1] if ':' in api_key else api_key
    url = "https://api.dehashed.com/v2/search"
    headers = get_api_headers()
    headers['Accept'] = 'application/json'
    headers['Content-Type'] = 'application/json'
    headers['Dehashed-Api-Key'] = raw_key
    payload = {'query': f'phone:"{query}"'}

    try:
        response, was_blocked = await async_request_with_retry(
            client, 'post', url, json=payload, headers=headers, _api_mode=True, debug=debug
        )

        if was_blocked:
            if debug:
                print(f"    [DEBUG] Dehashed blocked/rate limited")
            return []

        if response.status_code == 200:
            data = response.json()
            results = []
            for entry in data.get('entries', [])[:10]:
                email = _flatten_field(entry.get('email', ''), 'N/A')
                username = _flatten_field(entry.get('username', ''), 'N/A')
                name = _flatten_field(entry.get('name', ''), 'N/A')
                results.append({
                    'title': f"Dehashed: {email}",
                    'url': 'https://dehashed.com',
                    'snippet': f"Email: {email}, Username: {username}, Name: {name}",
                    'source': 'Dehashed'
                })
            if debug:
                print(f"    [DEBUG] Dehashed returned {len(results)} results")
            return results
        if response.status_code in (401, 403):
            _warn_once('dehashed', 'Dehashed API key invalid or out of credits')
        else:
            _warn_once('dehashed', f"Dehashed API error {response.status_code}: {_api_error_message(response)}")
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Dehashed error: {e}")
    return []

async def search_format(client, query, config, include_dehashed=False, debug=False):
    """Search all APIs in parallel for a single format."""
    tasks = [
        search_google(client, query, config, debug),
        search_brave(client, query, config, debug),
        search_duckduckgo(client, query, debug),
    ]

    if include_dehashed:
        tasks.append(search_dehashed(client, query, config, debug))

    results_list = await asyncio.gather(*tasks, return_exceptions=True)

    all_results = []
    for results in results_list:
        if isinstance(results, list):
            all_results.extend(results)

    return all_results


def deduplicate_results(results):
    """Remove duplicate results by URL."""
    from telespot_common.dedupe import deduplicate_results_list

    return deduplicate_results_list(results)


async def search_all_formats(phone, config, keyword=None, site=None,
                             include_dehashed=False, verbose=False, no_color=False, debug=False):
    """Search all US phone formats in parallel with captcha resilience."""
    c = Colors if not no_color else type('', (), {k: '' for k in dir(Colors) if not k.startswith('_')})()

    formats = generate_formats(phone)
    if not formats:
        return []

    all_results = []

    print(f"\n{c.BOLD}Searching for:{c.RESET} {phone}")
    print(f"Country: United States (+1)")
    print(f"Using {len(formats)} format variations")
    print(f"{c.CYAN}Mode: PARALLEL (with captcha detection + retry){c.RESET}\n")

    async with httpx.AsyncClient() as client:
        # Build queries for all formats
        queries = []
        for fmt in formats:
            query = fmt
            if keyword:
                query = f'{fmt} {keyword}'
            if site:
                query = f'{query} site:{site}'
            queries.append((fmt, query))

        # Search all formats in parallel
        print(f"{c.YELLOW}Launching parallel searches...{c.RESET}")
        start_time = datetime.now()

        tasks = [search_format(client, query, config, include_dehashed, debug) for _, query in queries]
        results_per_format = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = (datetime.now() - start_time).total_seconds()

        # Process results
        raw_total = 0
        for i, (fmt, _) in enumerate(queries):
            results = results_per_format[i] if isinstance(results_per_format[i], list) else []
            result_count = len(results)
            raw_total += result_count

            print(f"  [{i+1}/{len(formats)}] {fmt}: {c.GREEN}{result_count} results{c.RESET}")

            for r in results:
                r['format'] = fmt
            all_results.extend(results)

        # Deduplicate
        all_results = deduplicate_results(all_results)
        deduped_total = len(all_results)

        print(f"\n{c.GREEN}Completed in {elapsed:.1f} seconds{c.RESET}")
        print(f"Total: {deduped_total} unique results", end='')
        if deduped_total < raw_total:
            print(f" ({raw_total - deduped_total} duplicates removed)")
        else:
            print()

    return all_results

def extract_patterns(results):
    """Extract names, locations, usernames, and emails from results.

    Uses the shared, canonical extractors in telespot_common.patterns so
    telespot.py and telespotx.py behave identically. This replaces the old
    local regexes here, which were broken: the location regex made everything
    after the first group optional (matching ANY single capitalized word), and
    names were filtered by raw char length (>5) instead of word count.
    """
    patterns = {
        'names': {},
        'locations': {},
        'usernames': {},
        'emails': {},
    }

    for result in results:
        text = f"{result.get('title', '')} {result.get('snippet', '')}"

        for name in extract_names(text):
            patterns['names'][name] = patterns['names'].get(name, 0) + 1

        for loc in extract_locations(text):
            patterns['locations'][loc] = patterns['locations'].get(loc, 0) + 1

        for user in extract_usernames(text):
            key = f"@{user}"
            patterns['usernames'][key] = patterns['usernames'].get(key, 0) + 1

        for email in extract_emails(text):
            patterns['emails'][email] = patterns['emails'].get(email, 0) + 1

    # Calculate confidence
    total_patterns = sum(len(v) for v in patterns.values())
    if total_patterns > 10:
        confidence = 'HIGH'
        confidence_pct = min(95, 60 + total_patterns * 2)
    elif total_patterns > 5:
        confidence = 'MEDIUM'
        confidence_pct = 40 + total_patterns * 3
    else:
        confidence = 'LOW'
        confidence_pct = max(10, total_patterns * 8)

    patterns['confidence'] = confidence
    patterns['confidence_pct'] = confidence_pct

    return patterns

def print_summary(results, patterns, no_color=False):
    """Print analysis summary."""
    c = Colors if not no_color else type('', (), {k: '' for k in dir(Colors) if not k.startswith('_')})()

    print(f"\n{'=' * 60}")
    print(f"{c.BOLD}PATTERN ANALYSIS SUMMARY{c.RESET}")
    print('=' * 60)

    conf = patterns['confidence']
    pct = patterns['confidence_pct']
    if conf == 'HIGH':
        conf_color = c.GREEN
    elif conf == 'MEDIUM':
        conf_color = c.YELLOW
    else:
        conf_color = c.RED

    print(f"\nConfidence Score: {conf_color}{conf} ({pct}%){c.RESET}")
    print(f"Total Results: {len(results)}")

    # Results by source
    sources = {}
    for r in results:
        src = r.get('source', 'Unknown')
        sources[src] = sources.get(src, 0) + 1

    print(f"\n{c.BOLD}Results by Source:{c.RESET}")
    for src, count in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {src}: {count}")

    # Names
    if patterns['names']:
        print(f"\n{c.BOLD}Names Found:{c.RESET}")
        for name, count in sorted(patterns['names'].items(), key=lambda x: -x[1])[:5]:
            star = " *" if count > 2 else ""
            print(f"  {name}: {count}x{star}")

    # Locations
    if patterns['locations']:
        print(f"\n{c.BOLD}Locations:{c.RESET}")
        for loc, count in sorted(patterns['locations'].items(), key=lambda x: -x[1])[:5]:
            star = " *" if count > 2 else ""
            print(f"  {loc}: {count}x{star}")

    # Usernames
    if patterns['usernames']:
        print(f"\n{c.BOLD}Usernames:{c.RESET}")
        for user, count in sorted(patterns['usernames'].items(), key=lambda x: -x[1])[:5]:
            print(f"  {user}: {count}x")

    # Emails
    if patterns['emails']:
        print(f"\n{c.BOLD}Emails:{c.RESET}")
        for email, count in sorted(patterns['emails'].items(), key=lambda x: -x[1])[:5]:
            print(f"  {email}: {count}x")

    print('=' * 60)

def print_verbose_results(results, no_color=False):
    """Print detailed results."""
    c = Colors if not no_color else type('', (), {k: '' for k in dir(Colors) if not k.startswith('_')})()

    print(f"\n{c.BOLD}Detailed Results:{c.RESET}")
    print("-" * 60)

    seen_urls = set()
    for r in results:
        url = r.get('url', '')
        if url in seen_urls:
            continue
        seen_urls.add(url)

        print(f"\n{c.CYAN}[{r.get('source', 'Unknown')}]{c.RESET} {r.get('title', 'No title')}")
        print(f"  URL: {url}")
        snippet = r.get('snippet', '')[:150]
        if snippet:
            print(f"  {snippet}...")

def save_results(results, patterns, output_file):
    """Save results to file."""
    if output_file.endswith('.json'):
        data = {
            'timestamp': datetime.now().isoformat(),
            'version': VERSION,
            'results': results,
            'patterns': {
                'names': patterns['names'],
                'locations': patterns['locations'],
                'usernames': patterns['usernames'],
                'emails': patterns['emails'],
                'confidence': patterns['confidence'],
                'confidence_pct': patterns['confidence_pct'],
            }
        }
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        with open(output_file, 'w') as f:
            f.write(f"TelespotX Results - {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Results: {len(results)}\n")
            f.write(f"Confidence: {patterns['confidence']} ({patterns['confidence_pct']}%)\n\n")

            if patterns['names']:
                f.write("Names:\n")
                for name, count in sorted(patterns['names'].items(), key=lambda x: -x[1])[:10]:
                    f.write(f"  {name}: {count}x\n")
                f.write("\n")

            if patterns['locations']:
                f.write("Locations:\n")
                for loc, count in sorted(patterns['locations'].items(), key=lambda x: -x[1])[:10]:
                    f.write(f"  {loc}: {count}x\n")
                f.write("\n")

            f.write("Results:\n")
            f.write("-" * 40 + "\n")
            seen = set()
            for r in results:
                url = r.get('url', '')
                if url not in seen:
                    seen.add(url)
                    f.write(f"\n[{r.get('source')}] {r.get('title', 'No title')}\n")
                    f.write(f"  {url}\n")

    print(f"\nResults saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='TelespotX - Fast parallel phone OSINT (US numbers only)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  telespotx.py 8885551212
  telespotx.py 8885551212 -v
  telespotx.py 8885551212 -k "owner" -o results.json
  telespotx.py 8885551212 --dehashed

Note: This tool only supports United States phone numbers (+1).
        """
    )

    parser.add_argument('phone', nargs='?', help='US phone number to search (10 digits)')
    parser.add_argument('-k', '--keyword', help='Add keyword to search')
    parser.add_argument('-s', '--site', help='Limit to specific site')
    parser.add_argument('-o', '--output', help='Save results to file (.json or .txt)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed results')
    parser.add_argument('--dehashed', action='store_true', help='Include Dehashed search')
    parser.add_argument('--no-color', action='store_true', help='Disable colors')
    parser.add_argument('--api-status', action='store_true', help='Show API configuration')
    parser.add_argument('--version', action='store_true', help='Show version')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')

    args = parser.parse_args()

    # Handle version
    if args.version:
        print(f"telespotx v{VERSION}")
        sys.exit(0)

    # Print banner
    print_banner(args.no_color)

    # Load config
    config = load_config()

    # Handle API status
    if args.api_status:
        print_api_status(config, args.no_color)
        sys.exit(0)

    # Require phone number
    if not args.phone:
        parser.print_help()
        sys.exit(1)

    # Show API status
    print_api_status(config, args.no_color)

    # Run search
    results = asyncio.run(search_all_formats(
        args.phone,
        config,
        keyword=args.keyword,
        site=args.site,
        include_dehashed=args.dehashed,
        verbose=args.verbose,
        no_color=args.no_color,
        debug=args.debug
    ))

    if not results:
        print("\nNo results found.")
        sys.exit(0)

    # Extract patterns
    patterns = extract_patterns(results)

    # Print verbose results
    if args.verbose:
        print_verbose_results(results, args.no_color)

    # Print summary
    print_summary(results, patterns, args.no_color)

    # Save output
    if args.output:
        save_results(results, patterns, args.output)

if __name__ == '__main__':
    main()
