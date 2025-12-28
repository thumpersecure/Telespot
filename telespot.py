#!/usr/bin/env python3
"""
TeleSpot - Multi-Engine Phone Number Search
Searches for phone numbers using Google Custom Search API and Bing Search API
Focuses on name and location pattern analysis
"""

import requests
import time
import re
import sys
import os
from collections import Counter

ASCII_LOGO = """
████████╗███████╗██╗     ███████╗███████╗██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     █████╗  ███████╗██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██╔═══╝ ██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗███████║██║     ╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝    ╚═╝   
                                                         version 3.0
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


def load_api_keys():
    """Load API keys from environment variables or config file"""
    config = {
        'google_api_key': os.environ.get('GOOGLE_API_KEY'),
        'google_cse_id': os.environ.get('GOOGLE_CSE_ID'),
        'bing_api_key': os.environ.get('BING_API_KEY')
    }
    
    # Try to load from config file if env vars not set
    if not all([config['google_api_key'], config['bing_api_key']]):
        config_file = os.path.join(os.path.dirname(__file__) or '.', '.telespot_config')
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key.lower()] = value.strip()
    
    return config


def generate_phone_formats(phone_number):
    """Generate various phone number formats for searching"""
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
    
    formats = [
        f'{area}-{prefix}-{line}',           # 555-555-1212
        f'({area}) {prefix}-{line}',         # (555) 555-1212
        f'{area}{prefix}{line}',             # 5555551212
        f'{country} {area}-{prefix}-{line}', # 1 555-555-1212
    ]
    
    return formats


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
            'num': min(num_results, 10)  # API max is 10 per request
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
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


def search_fallback(query):
    """
    Fallback search method that doesn't require API keys
    Uses DuckDuckGo Instant Answer API (limited but free)
    """
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
            
            # Abstract (main answer)
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo Result'),
                    'snippet': data.get('Abstract', ''),
                    'source': 'DuckDuckGo'
                })
            
            # Related topics
            for topic in data.get('RelatedTopics', [])[:5]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'snippet': topic.get('Text', ''),
                        'source': 'DuckDuckGo'
                    })
        
        return results
    except Exception as e:
        print(f"  {Colors.YELLOW}DuckDuckGo error: {str(e)[:50]}{Colors.END}")
        return []


def extract_names(text):
    """Extract potential names from text"""
    # Pattern for potential names (2-3 capitalized words in sequence)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    names = re.findall(name_pattern, text)
    
    # Filter out common non-name words
    excluded = {
        'Phone', 'Number', 'Call', 'Contact', 'Email', 'Address', 
        'Street', 'City', 'State', 'Country', 'The', 'This', 'That',
        'Search', 'Results', 'View', 'More', 'Less', 'Show', 'Hide',
        'United States', 'New York', 'Los Angeles', 'San Francisco',
        'Google', 'Bing', 'Yahoo', 'Facebook', 'Twitter', 'Instagram',
        'Best', 'Top', 'Free', 'Online', 'Reviews', 'About', 'Home',
        'Business', 'Service', 'Services', 'Company', 'Companies',
        'White Pages', 'Yellow Pages', 'True Caller'
    }
    
    filtered_names = []
    for name in names:
        # Skip single word names and excluded terms
        if name not in excluded and len(name.split()) >= 2:
            filtered_names.append(name)
    
    return filtered_names


def extract_locations(text):
    """Extract potential locations from text"""
    locations = []
    
    # Find state abbreviations
    state_pattern = r'\b(' + '|'.join(US_STATES.keys()) + r')\b'
    state_matches = re.findall(state_pattern, text)
    locations.extend(state_matches)
    
    # Find city, state combinations
    city_state_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+(' + '|'.join(US_STATES.keys()) + r')\b'
    city_state_matches = re.findall(city_state_pattern, text)
    for city, state in city_state_matches:
        locations.append(f"{city}, {state}")
    
    # Find full state names
    for abbr, full_name in US_STATES.items():
        if full_name in text:
            locations.append(full_name)
    
    # Find zip codes
    zip_pattern = r'\b\d{5}(?:-\d{4})?\b'
    zip_matches = re.findall(zip_pattern, text)
    locations.extend(zip_matches)
    
    return list(set(locations))


def analyze_patterns(all_results):
    """Analyze results for name and location patterns"""
    all_text = []
    source_counts = Counter()
    
    for format_str, search_results in all_results.items():
        for result in search_results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}"
            all_text.append(text)
            source_counts[result.get('source', 'Unknown')] += 1
    
    # Combine all text
    combined_text = ' '.join(all_text)
    
    # Extract names and locations
    names = extract_names(combined_text)
    name_counter = Counter(names)
    
    locations = extract_locations(combined_text)
    location_counter = Counter(locations)
    
    return {
        'total_results': len(all_text),
        'results_by_source': dict(source_counts),
        'common_names': name_counter.most_common(10),
        'common_locations': location_counter.most_common(10),
    }


def print_pattern_summary(patterns):
    """Print a formatted summary of pattern analysis"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}PATTERN ANALYSIS SUMMARY{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")
    
    print(f"{Colors.CYAN}Total Results Found:{Colors.END} {patterns['total_results']}\n")
    
    # Source breakdown
    if patterns['results_by_source']:
        print(f"{Colors.BOLD}{Colors.BLUE}Results by Source:{Colors.END}")
        for source, count in patterns['results_by_source'].items():
            print(f"  • {Colors.GREEN}{source}{Colors.END}: {count} results")
        print()
    
    # Name patterns
    if patterns['common_names']:
        print(f"{Colors.BOLD}{Colors.BLUE}📛 Names Found:{Colors.END}")
        for name, count in patterns['common_names']:
            print(f"  • {Colors.GREEN}{name}{Colors.END}: mentioned {count} time(s)")
        print()
    else:
        print(f"{Colors.YELLOW}No names detected in search results{Colors.END}\n")
    
    # Location patterns
    if patterns['common_locations']:
        print(f"{Colors.BOLD}{Colors.BLUE}📍 Locations Mentioned:{Colors.END}")
        for location, count in patterns['common_locations']:
            print(f"  • {Colors.GREEN}{location}{Colors.END}: {count} occurrence(s)")
        print()
    else:
        print(f"{Colors.YELLOW}No locations detected in search results{Colors.END}\n")
    
    # Key insights
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 Key Insights:{Colors.END}")
    
    if patterns['total_results'] == 0:
        print(f"  • {Colors.YELLOW}No results found for this phone number{Colors.END}")
    else:
        if len(patterns['common_names']) > 0:
            primary_name = patterns['common_names'][0][0]
            print(f"  • {Colors.GREEN}Most associated name: {primary_name}{Colors.END}")
        
        if len(patterns['common_locations']) > 0:
            primary_location = patterns['common_locations'][0][0]
            print(f"  • {Colors.GREEN}Most associated location: {primary_location}{Colors.END}")
        
        if len(patterns['common_names']) == 0 and len(patterns['common_locations']) == 0:
            print(f"  • {Colors.YELLOW}Found results but no clear name or location patterns{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")


def setup_wizard():
    """Interactive setup wizard for API keys"""
    print(f"{Colors.BOLD}{Colors.CYAN}TeleSpot API Setup Wizard{Colors.END}\n")
    print("TeleSpot can use search engine APIs for reliable, unblocked searches.")
    print("You can configure one or both APIs:\n")
    
    print(f"{Colors.YELLOW}1. Google Custom Search API{Colors.END} (Free: 100 searches/day)")
    print("   Get keys at: https://developers.google.com/custom-search/v1/overview")
    print(f"{Colors.YELLOW}2. Bing Search API{Colors.END} (Free tier: 1000 searches/month)")
    print("   Get key at: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api")
    print(f"{Colors.YELLOW}3. Skip (use limited DuckDuckGo fallback){Colors.END}\n")
    
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
        
        if config_lines:
            config_file = os.path.join(os.path.dirname(__file__) or '.', '.telespot_config')
            with open(config_file, 'w') as f:
                f.write("# TeleSpot API Configuration\n")
                f.write("# Keep this file secure - do not share your API keys\n\n")
                f.write('\n'.join(config_lines))
            
            print(f"\n{Colors.GREEN}✓ Configuration saved to .telespot_config{Colors.END}")
            print(f"{Colors.YELLOW}Note: Add .telespot_config to your .gitignore!{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}Skipping API setup. Will use limited DuckDuckGo fallback.{Colors.END}\n")


def main():
    """Main execution function"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print(ASCII_LOGO)
    print(f"{Colors.END}")
    
    # Check for setup flag
    if '--setup' in sys.argv:
        setup_wizard()
        return
    
    # Load API configuration
    config = load_api_keys()
    
    # Check if any APIs are configured
    has_google = config.get('google_api_key') and config.get('google_cse_id')
    has_bing = config.get('bing_api_key')
    has_apis = has_google or has_bing
    
    if not has_apis:
        print(f"{Colors.YELLOW}⚠ No API keys configured. Using limited DuckDuckGo fallback.{Colors.END}")
        print(f"{Colors.CYAN}Run './telespot.py --setup' to configure APIs for better results.{Colors.END}\n")
    
    # Check for debug flag
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    if debug_mode:
        sys.argv = [arg for arg in sys.argv if arg not in ['--debug', '-d']]
        print(f"{Colors.YELLOW}🐛 Debug mode enabled{Colors.END}\n")
    
    # Get phone number from user
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        phone_number = sys.argv[1]
    else:
        phone_number = input(f"{Colors.CYAN}Enter phone number (digits only or formatted): {Colors.END}")
    
    print(f"\n{Colors.YELLOW}Generating search formats...{Colors.END}")
    formats = generate_phone_formats(phone_number)
    
    if not formats:
        return
    
    print(f"{Colors.GREEN}Generated {len(formats)} search format variations{Colors.END}\n")
    
    all_results = {}
    
    # Search each format across available engines
    for i, fmt in enumerate(formats, 1):
        print(f"{Colors.BLUE}[{i}/{len(formats)}] Searching: {Colors.END}{fmt}")
        
        format_results = []
        
        # Search Google API
        if has_google:
            print(f"  {Colors.CYAN}→ Searching Google...{Colors.END}", end=' ')
            google_results = search_google_api(fmt, config['google_api_key'], config['google_cse_id'], num_results=10)
            format_results.extend(google_results)
            print(f"{Colors.GREEN}({len(google_results)} results){Colors.END}")
            time.sleep(0.5)
        
        # Search Bing API
        if has_bing:
            print(f"  {Colors.CYAN}→ Searching Bing...{Colors.END}", end=' ')
            bing_results = search_bing_api(fmt, config['bing_api_key'], num_results=10)
            format_results.extend(bing_results)
            print(f"{Colors.GREEN}({len(bing_results)} results){Colors.END}")
            time.sleep(0.5)
        
        # Fallback to DuckDuckGo if no APIs configured
        if not has_apis:
            print(f"  {Colors.CYAN}→ Searching DuckDuckGo...{Colors.END}", end=' ')
            ddg_results = search_fallback(fmt)
            format_results.extend(ddg_results)
            print(f"{Colors.GREEN}({len(ddg_results)} results){Colors.END}")
            time.sleep(1)
        
        all_results[fmt] = format_results
        
        print(f"  {Colors.GREEN}✓ Total: {len(format_results)} results for this format{Colors.END}")
        
        if debug_mode and format_results:
            print(f"  {Colors.YELLOW}Debug: Sample - {format_results[0].get('title', 'N/A')[:60]}...{Colors.END}")
        
        # Rate limiting between formats
        if i < len(formats):
            print(f"  {Colors.YELLOW}⏳ Waiting 2 seconds...{Colors.END}\n")
            time.sleep(2)
        else:
            print()
    
    # Analyze patterns
    print(f"{Colors.YELLOW}Analyzing patterns across all results...{Colors.END}")
    patterns = analyze_patterns(all_results)
    
    # Print summary
    print_pattern_summary(patterns)
    
    # Optional: Save detailed results to file
    save_option = input(f"{Colors.CYAN}Save detailed results to file? (y/n): {Colors.END}")
    if save_option.lower() == 'y':
        import json
        filename = f"telespot_results_{re.sub(r'\\D', '', phone_number)}.json"
        output_data = {
            'phone_number': phone_number,
            'search_formats': formats,
            'results': all_results,
            'pattern_analysis': patterns
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"{Colors.GREEN}Results saved to: {filename}{Colors.END}\n")


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
