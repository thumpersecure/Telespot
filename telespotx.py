#!/usr/bin/env python3
"""
telespotx - Fast parallel phone number OSINT tool
Pre-release v0.1-alpha

Uses httpx + asyncio for parallel API requests.
No rate limiting - maximum speed.
United States phone numbers only (+1).
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime

try:
    import httpx
except ImportError:
    print("telespotx requires httpx. Install with: pip install httpx")
    sys.exit(1)

# Version
VERSION = "0.1-alpha"

# ANSI Colors
class Colors:
    RED = '\033[91m'
    WHITE = '\033[97m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
]

def get_random_headers():
    """Get headers with random user agent."""
    import random
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }

def print_banner(no_color=False):
    """Print the telespotx banner in red, white, and blue."""
    if no_color:
        banner = """
  _       _                      _
 | |_ ___| | ___  ___ _ __   ___ | |___  __
 | __/ _ \\ |/ _ \\/ __| '_ \\ / _ \\| __\\ \\/ /
 | ||  __/ |  __/\\__ \\ |_) | (_) | |_ >  <
  \\__\\___|_|\\___||___/ .__/ \\___/ \\__/_/\\_\\
                     |_|        v0.1-alpha
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
    config = {
        'google_api_key': '',
        'google_cse_id': '',
        'bing_api_key': '',
        'dehashed_api_key': '',
        'default_country_code': '+1',
    }

    config_path = os.path.expanduser('~/.telespot_config')
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.telespot_config')

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    return config

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
        ('Bing', bool(config.get('bing_api_key'))),
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

async def search_google(client, query, config, debug=False):
    """Search using Google Custom Search API."""
    api_key = config.get('google_api_key')
    cse_id = config.get('google_cse_id')

    if not api_key or not cse_id:
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': 10,
    }

    try:
        response = await client.get(url, params=params, headers=get_random_headers(), timeout=10.0)
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
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Google error: {e}")
    return []

async def search_bing(client, query, config, debug=False):
    """Search using Bing Search API."""
    api_key = config.get('bing_api_key')

    if not api_key:
        return []

    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = get_random_headers()
    headers['Ocp-Apim-Subscription-Key'] = api_key
    params = {'q': query, 'count': 10}

    try:
        response = await client.get(url, params=params, headers=headers, timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get('webPages', {}).get('value', []):
                results.append({
                    'title': item.get('name', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'Bing'
                })
            if debug:
                print(f"    [DEBUG] Bing returned {len(results)} results")
            return results
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Bing error: {e}")
    return []

async def search_duckduckgo(client, query, debug=False):
    """Search using DuckDuckGo Instant Answer API."""
    url = "https://api.duckduckgo.com/"
    params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1,
    }

    try:
        response = await client.get(url, params=params, headers=get_random_headers(), timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            results = []

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
                print(f"    [DEBUG] DuckDuckGo returned {len(results)} results")
            return results
    except Exception as e:
        if debug:
            print(f"    [DEBUG] DuckDuckGo error: {e}")
    return []

async def search_dehashed(client, query, config, debug=False):
    """Search using Dehashed API."""
    api_key = config.get('dehashed_api_key')

    if not api_key or ':' not in api_key:
        return []

    email, key = api_key.split(':', 1)
    url = "https://api.dehashed.com/search"
    params = {'query': f'phone:"{query}"'}

    try:
        response = await client.get(
            url,
            params=params,
            auth=(email, key),
            headers=get_random_headers(),
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            results = []
            for entry in data.get('entries', [])[:10]:
                results.append({
                    'title': f"Dehashed: {entry.get('email', 'Unknown')}",
                    'url': 'https://dehashed.com',
                    'snippet': f"Email: {entry.get('email', 'N/A')}, Username: {entry.get('username', 'N/A')}, Name: {entry.get('name', 'N/A')}",
                    'source': 'Dehashed'
                })
            if debug:
                print(f"    [DEBUG] Dehashed returned {len(results)} results")
            return results
    except Exception as e:
        if debug:
            print(f"    [DEBUG] Dehashed error: {e}")
    return []

async def search_format(client, query, config, include_dehashed=False, debug=False):
    """Search all APIs in parallel for a single format."""
    tasks = [
        search_google(client, query, config, debug),
        search_bing(client, query, config, debug),
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

async def search_all_formats(phone, config, keyword=None, site=None,
                             include_dehashed=False, verbose=False, no_color=False, debug=False):
    """Search all US phone formats in parallel."""
    c = Colors if not no_color else type('', (), {k: '' for k in dir(Colors) if not k.startswith('_')})()

    formats = generate_formats(phone)
    if not formats:
        return []

    all_results = []

    print(f"\n{c.BOLD}Searching for:{c.RESET} {phone}")
    print(f"Country: United States (+1)")
    print(f"Using {len(formats)} format variations")
    print(f"{c.CYAN}Mode: PARALLEL (no rate limiting){c.RESET}\n")

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
        for i, (fmt, _) in enumerate(queries):
            results = results_per_format[i] if isinstance(results_per_format[i], list) else []
            result_count = len(results)

            print(f"  [{i+1}/{len(formats)}] {fmt}: {c.GREEN}{result_count} results{c.RESET}")

            for r in results:
                r['format'] = fmt
            all_results.extend(results)

        print(f"\n{c.GREEN}Completed in {elapsed:.1f} seconds{c.RESET}")

    return all_results

def extract_patterns(results):
    """Extract names, locations, and usernames from results."""
    patterns = {
        'names': {},
        'locations': {},
        'usernames': {},
        'emails': {},
    }

    name_pattern = re.compile(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b')
    location_pattern = re.compile(r'\b([A-Z][a-z]+(?:,?\s+[A-Z]{2})?(?:\s+\d{5})?)\b')
    username_pattern = re.compile(r'@([A-Za-z0-9_]{3,20})')
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

    for result in results:
        text = f"{result.get('title', '')} {result.get('snippet', '')}"

        for name in name_pattern.findall(text):
            if len(name) > 5:
                patterns['names'][name] = patterns['names'].get(name, 0) + 1

        for loc in location_pattern.findall(text):
            if len(loc) > 3:
                patterns['locations'][loc] = patterns['locations'].get(loc, 0) + 1

        for user in username_pattern.findall(text):
            patterns['usernames'][f"@{user}"] = patterns['usernames'].get(f"@{user}", 0) + 1

        for email in email_pattern.findall(text):
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
