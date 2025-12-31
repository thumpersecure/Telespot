#!/usr/bin/env python3
"""
TeleSpot - Multi-Engine Phone Number Search
Searches for phone numbers using Google Custom Search API, Bing Search API, and DuckDuckGo
Focuses on name and location pattern analysis with advanced features
"""

import requests
import time
import re
import sys
import os
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import threading

ASCII_LOGO = """
████████╗███████╗██╗     ███████╗███████╗██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     █████╗  ███████╗██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██╔═══╝ ██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗███████║██║     ╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝    ╚═╝   
                                                         version 4.5
"""

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_RED = '\033[91m'
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'


# Common US states for location detection
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
    'WI': 'Wisconsin', 'WY': 'Wyoming'
}

# DTMF frequencies for phone number tones
DTMF_FREQS = {
    '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
    '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
    '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
    '*': (941, 1209), '0': (941, 1336), '#': (941, 1477)
}

# People search and social media sites for site: operator
PEOPLE_SEARCH_SITES = [
    'yellowpages.com',
    'whitepages.com',
    'thatsthem.com',
    'information.com',
    'instantcheckmate.com',
    'facebook.com',
    'yahoo.com'
]


def play_dtmf_tone(digit, duration=0.2):
    """Generate DTMF tone for a digit using system beep (cross-platform)"""
    try:
        # For visual/audio feedback - print the digit being "dialed"
        print(f"\r{Colors.CYAN}📞 Dialing: {digit}{Colors.END}", end='', flush=True)
        
        # Try to use system beep on Unix-like systems
        if os.name != 'nt':  # Unix/Linux/Mac
            # Use a simple beep - actual DTMF would require audio library
            os.system(f'printf "\\007" > /dev/tty 2>/dev/null')
        else:  # Windows
            import winsound
            # Simple beep - actual DTMF would require more complex implementation
            winsound.Beep(800, int(duration * 1000))
        
        time.sleep(duration)
    except:
        # Fallback - just visual feedback
        pass


def play_phone_number_tones(phone_number):
    """Play DTMF tones for entire phone number"""
    digits = re.sub(r'\D', '', phone_number)
    print(f"\n{Colors.BRIGHT_CYAN}🎵 Playing DTMF tones for: {phone_number}{Colors.END}")
    
    for digit in digits:
        play_dtmf_tone(digit)
    
    print(f"\n{Colors.GREEN}✓ Dial complete!{Colors.END}\n")
    time.sleep(0.5)


def load_api_keys():
    """Load API keys from environment variables or config file"""
    config = {
        'google_api_key': os.environ.get('GOOGLE_API_KEY'),
        'google_cse_id': os.environ.get('GOOGLE_CSE_ID'),
        'bing_api_key': os.environ.get('BING_API_KEY'),
        'dehashed_email': os.environ.get('DEHASHED_EMAIL'),
        'dehashed_api_key': os.environ.get('DEHASHED_API_KEY')
    }
    
    # Try to load from config file if env vars not set
    config_file = os.path.join(os.path.dirname(__file__) or '.', '.telespot_config')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key.lower()] = value.strip()
    
    return config


def generate_phone_formats(phone_number, keywords='', site_search=None):
    """Generate various phone number formats for searching (10 total formats)"""
    digits = re.sub(r'\D', '', phone_number)
    
    if len(digits) == 11 and digits.startswith('1'):
        area = digits[1:4]
        prefix = digits[4:7]
        line = digits[7:11]
        country = '1'
    elif len(digits) == 10:
        area = digits[0:3]
        prefix = digits[3:6]
        line = digits[6:10]
        country = '1'
    else:
        print(f"{Colors.RED}Error: Phone number must be 10 or 11 digits{Colors.END}")
        return []
    
    # Prepare keyword string
    keyword_str = ''
    if keywords:
        keyword_str = ' ' + '+'.join(keywords.split())
    
    # Prepare site search string
    site_str = ''
    if site_search:
        site_str = f' site:{site_search}'
    
    # Basic 4 formats (without quotes)
    basic_formats = [
        f'{area}-{prefix}-{line}',
        f'{area}{prefix}{line}',
        f'({area}) {prefix}-{line}',
        f'+{country}{area}-{prefix}-{line}',
    ]
    
    # Quoted versions of basic 4
    quoted_formats = [f'"{fmt}"' for fmt in basic_formats]
    
    # Additional 2 special formats
    special_formats = [
        f'({area}-{prefix}-{line})',
        f'"({area}) {prefix}-{line}"',
    ]
    
    # Combine all formats
    all_formats = basic_formats + quoted_formats + special_formats
    
    # Add keywords and site search if provided
    if keyword_str or site_str:
        all_formats = [fmt + keyword_str + site_str for fmt in all_formats]
    
    return all_formats


def search_google_api(query, api_key, cse_id, num_results=10):
    """Search using Google Custom Search API"""
    if not api_key or not cse_id:
        return []
    
    results = []
    try:
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': query,
            'num': min(num_results, 10)
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'source': 'Google'
                })
        elif response.status_code == 429:
            print(f"  {Colors.RED}✗ Google API quota exceeded{Colors.END}")
        else:
            print(f"  {Colors.YELLOW}⚠ Google API error: {response.status_code}{Colors.END}")
        
        return results
    except Exception as e:
        print(f"  {Colors.YELLOW}Google API error: {str(e)[:50]}{Colors.END}")
        return []


def search_bing_api(query, api_key, num_results=10):
    """Search using Bing Search API"""
    if not api_key:
        return []
    
    results = []
    try:
        url = 'https://api.bing.microsoft.com/v7.0/search'
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        params = {
            'q': query,
            'count': num_results,
            'textDecorations': False,
            'textFormat': 'Raw'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get('webPages', {}).get('value', []):
                results.append({
                    'title': item.get('name', ''),
                    'snippet': item.get('snippet', ''),
                    'url': item.get('url', ''),
                    'source': 'Bing'
                })
        elif response.status_code == 429:
            print(f"  {Colors.RED}✗ Bing API quota exceeded{Colors.END}")
        else:
            print(f"  {Colors.YELLOW}⚠ Bing API error: {response.status_code}{Colors.END}")
        
        return results
    except Exception as e:
        print(f"  {Colors.YELLOW}Bing API error: {str(e)[:50]}{Colors.END}")
        return []


def search_duckduckgo(query):
    """Search DuckDuckGo using Instant Answer API"""
    results = []
    try:
        url = 'https://api.duckduckgo.com/'
        params = {
            'q': query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Result'),
                    'snippet': data.get('Abstract', ''),
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo'
                })
            
            for topic in data.get('RelatedTopics', [])[:5]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo'
                    })
        
        return results
    except Exception as e:
        print(f"  {Colors.YELLOW}DuckDuckGo error: {str(e)[:50]}{Colors.END}")
        return []


def search_dehashed(phone_number, email, api_key):
    """Search Dehashed API for phone number"""
    if not email or not api_key:
        return []
    
    results = []
    try:
        # Remove non-digits from phone number
        digits = re.sub(r'\D', '', phone_number)
        
        url = 'https://api.dehashed.com/search'
        headers = {
            'Accept': 'application/json'
        }
        params = {
            'query': f'phone:{digits}',
            'size': 10000  # Max results
        }
        
        response = requests.get(url, params=params, headers=headers, 
                              auth=(email, api_key), timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get('entries', [])
            
            for entry in entries[:50]:  # Limit to first 50
                result = {
                    'title': f"Dehashed: {entry.get('email', 'Unknown')}",
                    'snippet': f"Username: {entry.get('username', 'N/A')}, Email: {entry.get('email', 'N/A')}, Database: {entry.get('database_name', 'N/A')}",
                    'url': f"https://dehashed.com/search?query={digits}",
                    'source': 'Dehashed',
                    'username': entry.get('username', ''),
                    'email': entry.get('email', ''),
                    'database': entry.get('database_name', '')
                }
                results.append(result)
            
            if entries:
                print(f"  {Colors.GREEN}✓ Found {len(entries)} Dehashed entries{Colors.END}")
            
        elif response.status_code == 401:
            print(f"  {Colors.RED}✗ Dehashed authentication failed{Colors.END}")
        else:
            print(f"  {Colors.YELLOW}⚠ Dehashed API error: {response.status_code}{Colors.END}")
        
        return results
    except Exception as e:
        print(f"  {Colors.YELLOW}Dehashed error: {str(e)[:50]}{Colors.END}")
        return []


def extract_usernames(text, url=''):
    """Extract potential usernames from text and URLs"""
    usernames = []
    
    # Common social media URL patterns
    social_patterns = [
        r'facebook\.com/([a-zA-Z0-9\.]+)',
        r'twitter\.com/([a-zA-Z0-9_]+)',
        r'instagram\.com/([a-zA-Z0-9_\.]+)',
        r'linkedin\.com/in/([a-zA-Z0-9-]+)',
        r'tiktok\.com/@([a-zA-Z0-9_\.]+)',
        r'reddit\.com/user/([a-zA-Z0-9_-]+)',
        r'github\.com/([a-zA-Z0-9-]+)',
        r'youtube\.com/@([a-zA-Z0-9_]+)',
    ]
    
    # Extract from URL
    for pattern in social_patterns:
        matches = re.findall(pattern, url, re.IGNORECASE)
        for match in matches:
            if match and len(match) > 2 and match.lower() not in ['profile', 'pages', 'public']:
                platform = re.search(r'(facebook|twitter|instagram|linkedin|tiktok|reddit|github|youtube)', pattern).group(1)
                usernames.append({
                    'username': match,
                    'platform': platform.capitalize(),
                    'url': url
                })
    
    # Extract @mentions from text
    mention_pattern = r'@([a-zA-Z0-9_]{3,15})'
    mentions = re.findall(mention_pattern, text)
    for mention in mentions:
        usernames.append({
            'username': mention,
            'platform': 'Unknown',
            'url': url
        })
    
    return usernames


def find_username_correlations(all_results):
    """Find usernames that appear in 2+ results"""
    username_occurrences = defaultdict(list)
    
    for format_str, results in all_results.items():
        for result in results:
            # Extract usernames from URL and text
            combined_text = f"{result.get('title', '')} {result.get('snippet', '')}"
            usernames = extract_usernames(combined_text, result.get('url', ''))
            
            for user_info in usernames:
                username = user_info['username'].lower()
                username_occurrences[username].append({
                    'platform': user_info['platform'],
                    'url': user_info['url'],
                    'title': result.get('title', ''),
                    'source': result.get('source', 'Unknown')
                })
    
    # Filter to only usernames appearing 2+ times
    correlated_usernames = {
        username: occurrences 
        for username, occurrences in username_occurrences.items() 
        if len(occurrences) >= 2
    }
    
    return correlated_usernames


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
        'White Pages', 'Yellow Pages', 'True Caller', 'Caller Id'
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


def calculate_confidence_score(all_results, patterns):
    """Calculate confidence score based on result consistency"""
    if patterns['total_results'] == 0:
        return 0
    
    score = 0
    
    # Results found (0-30 points)
    if patterns['total_results'] > 0:
        score += min(30, patterns['total_results'] * 3)
    
    # Name consistency (0-35 points)
    if patterns['common_names']:
        top_name_count = patterns['common_names'][0][1]
        name_consistency = (top_name_count / patterns['total_results']) * 35
        score += name_consistency
    
    # Location consistency (0-20 points)
    if patterns['common_locations']:
        top_location_count = patterns['common_locations'][0][1]
        location_consistency = (top_location_count / patterns['total_results']) * 20
        score += location_consistency
    
    # Multiple source verification (0-10 points)
    if len(patterns['results_by_source']) >= 2:
        score += 10
    
    # Username correlation bonus (0-5 points)
    if patterns.get('username_correlations'):
        score += 5
    
    return min(int(score), 100)


def analyze_patterns(all_results):
    """Analyze results for name and location patterns"""
    all_text = []
    source_counts = Counter()
    url_list = []
    
    for format_str, search_results in all_results.items():
        for result in search_results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}"
            all_text.append(text)
            source_counts[result.get('source', 'Unknown')] += 1
            if result.get('url'):
                url_list.append(result.get('url'))
    
    combined_text = ' '.join(all_text)
    
    names = extract_names(combined_text)
    name_counter = Counter(names)
    
    locations = extract_locations(combined_text)
    location_counter = Counter(locations)
    
    # Find username correlations
    username_correlations = find_username_correlations(all_results)
    
    patterns = {
        'total_results': len(all_text),
        'results_by_source': dict(source_counts),
        'common_names': name_counter.most_common(10),
        'common_locations': location_counter.most_common(10),
        'unique_urls': len(set(url_list)),
        'username_correlations': username_correlations
    }
    
    patterns['confidence_score'] = calculate_confidence_score(all_results, patterns)
    
    return patterns


def print_verbose_results(all_results, colorful=False):
    """Print verbose listing of all search results"""
    color_title = Colors.BRIGHT_CYAN if colorful else Colors.CYAN
    color_url = Colors.BRIGHT_BLUE if colorful else Colors.BLUE
    color_snippet = Colors.GREEN if colorful else Colors.END
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}VERBOSE RESULTS - ALL LISTINGS{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")
    
    for format_str, results in all_results.items():
        if results:
            print(f"{Colors.BOLD}{Colors.YELLOW}Format: {format_str}{Colors.END}")
            print(f"{Colors.YELLOW}{'─' * 80}{Colors.END}\n")
            
            for idx, result in enumerate(results, 1):
                print(f"{color_title}[{idx}] {result.get('title', 'No Title')}{Colors.END}")
                print(f"{color_url}🔗 URL: {result.get('url', 'N/A')}{Colors.END}")
                print(f"{color_snippet}📄 Description: {result.get('snippet', 'No description')}{Colors.END}")
                print(f"{Colors.MAGENTA}🔍 Source: {result.get('source', 'Unknown')}{Colors.END}")
                print()
            
            print()


def print_pattern_summary(patterns, colorful=False, dossier_mode=None):
    """Print a formatted summary of pattern analysis"""
    header_color = Colors.BG_BLUE + Colors.BOLD if colorful else Colors.BOLD + Colors.HEADER
    
    print(f"\n{header_color}{'='*80}{Colors.END}")
    print(f"{header_color}PATTERN ANALYSIS SUMMARY{Colors.END}")
    print(f"{header_color}{'='*80}{Colors.END}\n")
    
    # Confidence Score
    confidence = patterns['confidence_score']
    if confidence >= 75:
        conf_color = Colors.BRIGHT_GREEN if colorful else Colors.GREEN
        conf_label = "HIGH"
    elif confidence >= 50:
        conf_color = Colors.YELLOW
        conf_label = "MEDIUM"
    else:
        conf_color = Colors.RED
        conf_label = "LOW"
    
    print(f"{Colors.BOLD}🎯 Confidence Score: {conf_color}{confidence}% ({conf_label}){Colors.END}\n")
    
    print(f"{Colors.CYAN}Total Results Found:{Colors.END} {patterns['total_results']}")
    print(f"{Colors.CYAN}Unique URLs:{Colors.END} {patterns['unique_urls']}\n")
    
    # Dossier header
    if dossier_mode:
        dossier_color = Colors.MAGENTA if colorful else Colors.HEADER
        print(f"{Colors.BOLD}{dossier_color}📋 DOSSIER TYPE: {dossier_mode.upper()}{Colors.END}\n")
    
    # Source breakdown
    if patterns['results_by_source']:
        print(f"{Colors.BOLD}{Colors.BLUE}Results by Source:{Colors.END}")
        for source, count in patterns['results_by_source'].items():
            print(f"  • {Colors.GREEN}{source}{Colors.END}: {count} results")
        print()
    
    # Username correlations
    if patterns.get('username_correlations'):
        corr_color = Colors.BRIGHT_CYAN if colorful else Colors.MAGENTA
        print(f"{Colors.BOLD}{corr_color}🔗 Username Correlations (appearing in 2+ results):{Colors.END}")
        for username, occurrences in list(patterns['username_correlations'].items())[:10]:
            platforms = ', '.join(set([occ['platform'] for occ in occurrences]))
            count = len(occurrences)
            print(f"  • {Colors.GREEN}@{username}{Colors.END} ({platforms}): {count} occurrence(s)")
            for occ in occurrences[:2]:  # Show first 2 URLs
                print(f"    - {Colors.BLUE}{occ['url'][:70]}...{Colors.END}")
        print()
    
    # Name patterns
    if patterns['common_names']:
        name_color = Colors.BRIGHT_GREEN if colorful else Colors.BLUE
        print(f"{Colors.BOLD}{name_color}📛 Names Found:{Colors.END}")
        for name, count in patterns['common_names']:
            print(f"  • {Colors.GREEN}{name}{Colors.END}: mentioned {count} time(s)")
        print()
    else:
        print(f"{Colors.YELLOW}No names detected in search results{Colors.END}\n")
    
    # Location patterns
    if patterns['common_locations']:
        loc_color = Colors.BRIGHT_CYAN if colorful else Colors.BLUE
        print(f"{Colors.BOLD}{loc_color}📍 Locations Mentioned:{Colors.END}")
        for location, count in patterns['common_locations']:
            print(f"  • {Colors.GREEN}{location}{Colors.END}: {count} occurrence(s)")
        print()
    else:
        print(f"{Colors.YELLOW}No locations detected in search results{Colors.END}\n")
    
    # Key insights
    insight_color = Colors.MAGENTA if colorful else Colors.BLUE
    print(f"{Colors.BOLD}{insight_color}🔍 Key Insights:{Colors.END}")
    
    if patterns['total_results'] == 0:
        print(f"  • {Colors.YELLOW}No results found for this phone number{Colors.END}")
    else:
        if patterns.get('username_correlations'):
            print(f"  • {Colors.GREEN}Found correlated usernames across multiple sources{Colors.END}")
        
        if len(patterns['common_names']) > 0:
            primary_name = patterns['common_names'][0][0]
            print(f"  • {Colors.GREEN}Most associated name: {primary_name}{Colors.END}")
        
        if len(patterns['common_locations']) > 0:
            primary_location = patterns['common_locations'][0][0]
            print(f"  • {Colors.GREEN}Most associated location: {primary_location}{Colors.END}")
        
        if len(patterns['common_names']) == 0 and len(patterns['common_locations']) == 0:
            print(f"  • {Colors.YELLOW}Found results but no clear name or location patterns{Colors.END}")
    
    print(f"\n{header_color}{'='*80}{Colors.END}\n")


def save_results_txt(phone_number, formats, all_results, patterns, filename=None):
    """Save results to a text file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"telespot_{re.sub(r'\\D', '', phone_number)}_{timestamp}.txt"
    
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    with open(filename, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("TELESPOT SEARCH RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Phone Number: {phone_number}\n")
        f.write(f"Search Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Confidence Score: {patterns['confidence_score']}%\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total Results: {patterns['total_results']}\n")
        f.write(f"Unique URLs: {patterns['unique_urls']}\n\n")
        
        if patterns['results_by_source']:
            f.write("Results by Source:\n")
            for source, count in patterns['results_by_source'].items():
                f.write(f"  - {source}: {count} results\n")
            f.write("\n")
        
        if patterns.get('username_correlations'):
            f.write("Username Correlations (2+ occurrences):\n")
            for username, occurrences in patterns['username_correlations'].items():
                platforms = ', '.join(set([occ['platform'] for occ in occurrences]))
                f.write(f"  - @{username} ({platforms}): {len(occurrences)} occurrence(s)\n")
                for occ in occurrences:
                    f.write(f"    URL: {occ['url']}\n")
            f.write("\n")
        
        if patterns['common_names']:
            f.write("Names Found:\n")
            for name, count in patterns['common_names']:
                f.write(f"  - {name}: {count} mention(s)\n")
            f.write("\n")
        
        if patterns['common_locations']:
            f.write("Locations Mentioned:\n")
            for location, count in patterns['common_locations']:
                f.write(f"  - {location}: {count} occurrence(s)\n")
            f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        for format_str, results in all_results.items():
            if results:
                f.write(f"Format: {format_str}\n")
                f.write("-" * 80 + "\n\n")
                
                for idx, result in enumerate(results, 1):
                    f.write(f"[{idx}] {result.get('title', 'No Title')}\n")
                    f.write(f"URL: {result.get('url', 'N/A')}\n")
                    f.write(f"Source: {result.get('source', 'Unknown')}\n")
                    f.write(f"Description: {result.get('snippet', 'No description')}\n\n")
                
                f.write("\n")
    
    return filename


def setup_wizard():
    """Interactive setup wizard for API keys"""
    print(f"{Colors.BOLD}{Colors.CYAN}TeleSpot API Setup Wizard{Colors.END}\n")
    print("Configure search engine APIs and optional services:\n")
    
    print(f"{Colors.YELLOW}1. Google Custom Search API{Colors.END} (Free: 100 searches/day)")
    print("   Get keys at: https://developers.google.com/custom-search/v1/overview")
    print(f"{Colors.YELLOW}2. Bing Search API{Colors.END} (Free tier: 1000 searches/month)")
    print("   Get key at: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api")
    print(f"{Colors.YELLOW}3. Dehashed API{Colors.END} (Paid service)")
    print("   Get credentials at: https://dehashed.com/")
    print(f"{Colors.YELLOW}4. DuckDuckGo{Colors.END} (Always included, no API needed)\n")
    
    config_lines = []
    
    choice = input("Configure APIs? (y/n): ").strip().lower()
    if choice == 'y':
        print("\n" + "="*60)
        print("Google Custom Search Setup:")
        print("="*60)
        google_key = input("Google API Key (or press Enter to skip): ").strip()
        google_cse = input("Google CSE ID (or press Enter to skip): ").strip()
        
        if google_key:
            config_lines.append(f"google_api_key={google_key}")
        if google_cse:
            config_lines.append(f"google_cse_id={google_cse}")
        
        print("\n" + "="*60)
        print("Bing Search API Setup:")
        print("="*60)
        bing_key = input("Bing API Key (or press Enter to skip): ").strip()
        
        if bing_key:
            config_lines.append(f"bing_api_key={bing_key}")
        
        print("\n" + "="*60)
        print("Dehashed API Setup (Optional):")
        print("="*60)
        dehashed_email = input("Dehashed Email (or press Enter to skip): ").strip()
        dehashed_key = input("Dehashed API Key (or press Enter to skip): ").strip()
        
        if dehashed_email:
            config_lines.append(f"dehashed_email={dehashed_email}")
        if dehashed_key:
            config_lines.append(f"dehashed_api_key={dehashed_key}")
        
        if config_lines:
            config_file = os.path.join(os.path.dirname(__file__) or '.', '.telespot_config')
            with open(config_file, 'w') as f:
                f.write("# TeleSpot API Configuration\n")
                f.write("# Keep this file secure - do not share your API keys\n\n")
                f.write('\n'.join(config_lines))
            
            print(f"\n{Colors.GREEN}✓ Configuration saved to .telespot_config{Colors.END}")
            print(f"{Colors.YELLOW}Note: Add .telespot_config to your .gitignore!{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}Skipping API setup. Will use free DuckDuckGo only.{Colors.END}\n")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='TeleSpot - Phone Number OSINT Search Tool')
    parser.add_argument('phone_number', nargs='?', help='Phone number to search')
    parser.add_argument('--setup', action='store_true', help='Run API setup wizard')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose results with full listings')
    parser.add_argument('--colorful', '-c', action='store_true', help='Enable colorful mode')
    parser.add_argument('--keywords', '-k', help='Additional search keywords (e.g., "John Smith")')
    parser.add_argument('--delay', type=int, default=2, help='Delay between searches in seconds (default: 2)')
    parser.add_argument('--dossier', choices=['person', 'business'], help='Generate a dossier (person or business)')
    parser.add_argument('--site', choices=PEOPLE_SEARCH_SITES, help='Limit search to specific site')
    parser.add_argument('--dehashed', action='store_true', help='Include Dehashed API search')
    parser.add_argument('--dtmf', action='store_true', help='Play DTMF tones while searching (fun mode)')
    parser.add_argument('--usernames', action='store_true', help='Focus on username correlation analysis')
    
    args = parser.parse_args()
    
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print(ASCII_LOGO)
    print(f"{Colors.END}")
    
    # Check for setup flag
    if args.setup:
        setup_wizard()
        return
    
    # Load API configuration
    config = load_api_keys()
    
    # Check if any APIs are configured
    has_google = config.get('google_api_key') and config.get('google_cse_id')
    has_bing = config.get('bing_api_key')
    has_dehashed = config.get('dehashed_email') and config.get('dehashed_api_key')
    
    if not (has_google or has_bing):
        print(f"{Colors.YELLOW}⚠ No API keys configured. Using DuckDuckGo only (limited results).{Colors.END}")
        print(f"{Colors.CYAN}Run './telespot.py --setup' to configure APIs for better results.{Colors.END}\n")
    
    # Get phone number
    if not args.phone_number:
        args.phone_number = input(f"{Colors.CYAN}Enter phone number (digits only or formatted): {Colors.END}")
    
    # Play DTMF tones if requested
    if args.dtmf:
        play_phone_number_tones(args.phone_number)
    
    if args.debug:
        print(f"{Colors.YELLOW}🐛 Debug mode enabled{Colors.END}")
    
    if args.colorful:
        print(f"{Colors.MAGENTA}🎨 Colorful mode enabled{Colors.END}")
    
    if args.dossier:
        print(f"{Colors.MAGENTA}📋 Dossier mode: {args.dossier}{Colors.END}")
    
    if args.site:
        print(f"{Colors.CYAN}🔍 Site-specific search: {args.site}{Colors.END}")
    
    if args.dehashed and has_dehashed:
        print(f"{Colors.MAGENTA}🔓 Dehashed search enabled{Colors.END}")
    elif args.dehashed and not has_dehashed:
        print(f"{Colors.YELLOW}⚠ Dehashed requested but not configured. Run --setup.{Colors.END}")
    
    if args.usernames:
        print(f"{Colors.CYAN}👤 Username correlation analysis enabled{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Generating search formats...{Colors.END}")
    formats = generate_phone_formats(args.phone_number, args.keywords or '', args.site)
    
    if not formats:
        return
    
    print(f"{Colors.GREEN}Generated {len(formats)} search format variations{Colors.END}")
    if args.keywords:
        print(f"{Colors.CYAN}Keywords: {args.keywords}{Colors.END}")
    if args.site:
        print(f"{Colors.CYAN}Site restriction: {args.site}{Colors.END}")
    print()
    
    all_results = {}
    
    # Search Dehashed first if enabled
    if args.dehashed and has_dehashed:
        print(f"{Colors.BRIGHT_CYAN}Searching Dehashed...{Colors.END}")
        dehashed_results = search_dehashed(args.phone_number, config['dehashed_email'], config['dehashed_api_key'])
        if dehashed_results:
            all_results['Dehashed'] = dehashed_results
        print()
    
    # Search each format across available engines
    for i, fmt in enumerate(formats, 1):
        print(f"{Colors.BLUE}[{i}/{len(formats)}] Searching: {Colors.END}{fmt}")
        
        format_results = []
        
        # Always search DuckDuckGo (free)
        print(f"  {Colors.CYAN}→ Searching DuckDuckGo...{Colors.END}", end=' ')
        ddg_results = search_duckduckgo(fmt)
        format_results.extend(ddg_results)
        print(f"{Colors.GREEN}({len(ddg_results)} results){Colors.END}")
        time.sleep(0.5)
        
        # Search Google API if configured
        if has_google:
            print(f"  {Colors.CYAN}→ Searching Google...{Colors.END}", end=' ')
            google_results = search_google_api(fmt, config['google_api_key'], config['google_cse_id'], num_results=10)
            format_results.extend(google_results)
            print(f"{Colors.GREEN}({len(google_results)} results){Colors.END}")
            time.sleep(0.5)
        
        # Search Bing API if configured
        if has_bing:
            print(f"  {Colors.CYAN}→ Searching Bing...{Colors.END}", end=' ')
            bing_results = search_bing_api(fmt, config['bing_api_key'], num_results=10)
            format_results.extend(bing_results)
            print(f"{Colors.GREEN}({len(bing_results)} results){Colors.END}")
            time.sleep(0.5)
        
        all_results[fmt] = format_results
        
        print(f"  {Colors.GREEN}✓ Total: {len(format_results)} results for this format{Colors.END}")
        
        if args.debug and format_results:
            print(f"  {Colors.YELLOW}Debug: Sample - {format_results[0].get('title', 'N/A')[:60]}...{Colors.END}")
        
        # Rate limiting between formats
        if i < len(formats):
            print(f"  {Colors.YELLOW}⏳ Waiting {args.delay} seconds...{Colors.END}\n")
            time.sleep(args.delay)
        else:
            print()
    
    # Analyze patterns
    print(f"{Colors.YELLOW}Analyzing patterns across all results...{Colors.END}")
    patterns = analyze_patterns(all_results)
    
    # Print verbose results if requested
    if args.verbose:
        print_verbose_results(all_results, args.colorful)
    
    # Print summary
    print_pattern_summary(patterns, args.colorful, args.dossier)
    
    # Save results
    save_choice = input(f"{Colors.CYAN}Save results to file? (y/n): {Colors.END}").strip().lower()
    if save_choice == 'y':
        custom_name = input(f"{Colors.CYAN}Enter filename (or press Enter for default): {Colors.END}").strip()
        filename = custom_name if custom_name else None
        
        saved_file = save_results_txt(args.phone_number, formats, all_results, patterns, filename)
        print(f"{Colors.GREEN}✓ Results saved to: {saved_file}{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Search interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
