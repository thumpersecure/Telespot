#!/usr/bin/env python3
"""
TeleSpot - Multi-Engine Phone Number Search
Searches for phone numbers across Google, Bing, and DuckDuckGo
Focuses on name and location pattern analysis
"""

import requests
import time
import re
import sys
from collections import Counter
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

ASCII_LOGO = """
████████╗███████╗██╗     ███████╗███████╗██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     █████╗  ███████╗██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██╔═══╝ ██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗███████║██║     ╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝    ╚═╝   
                                                         version 2.0
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


def generate_phone_formats(phone_number):
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
    
    # All 10 formats as specified
    formats = [
        f'+{country}{area}{prefix}{line}',                    # 1. +12155551234
        f'"+{country}{area}{prefix}{line}"',                  # 2. "+12155551234"
        f'({area}) {prefix}-{line}',                          # 3. (215) 555-1234
        f'"{country} ({area}) {prefix}-{line}"',              # 4. "1 (215) 555-1234"
        f'("{area}-{prefix}-{line}")',                        # 5. ("215-555-1234")
        f'{area}-{prefix}-{line}',                            # 6. 215-555-1234
        f'"{area}-{prefix}-{line}"',                          # 7. "215-555-1234"
        f'({area}{prefix}{line})',                            # 8. (2155551234)
        f'"{area}{prefix}{line}"',                            # 9. "2155551234"
        f'("{area}{prefix}{line}")',                          # 10. ("2155551234")
    ]
    
    return formats


def search_google(query, num_results=10):
    """Search Google and extract results"""
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        url = f'https://www.google.com/search?q={quote_plus(query)}&num={num_results}'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search result divs
            for g in soup.find_all('div', class_='g'):
                # Extract title
                title_elem = g.find('h3')
                title = title_elem.get_text() if title_elem else ''
                
                # Extract snippet
                snippet_elem = g.find('div', class_=['VwiC3b', 'yXK7lf'])
                snippet = snippet_elem.get_text() if snippet_elem else ''
                
                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'source': 'Google'
                    })
        
        return results
    except Exception as e:
        print(f"  {Colors.YELLOW}Google search error: {str(e)[:50]}{Colors.END}")
        return []


def search_bing(query, num_results=10):
    """Search Bing and extract results"""
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        url = f'https://www.bing.com/search?q={quote_plus(query)}&count={num_results}'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search result items
            for item in soup.find_all('li', class_='b_algo'):
                # Extract title
                title_elem = item.find('h2')
                title = title_elem.get_text() if title_elem else ''
                
                # Extract snippet
                snippet_elem = item.find('p')
                snippet = snippet_elem.get_text() if snippet_elem else ''
                
                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'source': 'Bing'
                    })
        
        return results
    except Exception as e:
        print(f"  {Colors.YELLOW}Bing search error: {str(e)[:50]}{Colors.END}")
        return []


def search_duckduckgo(query, num_results=10):
    """Search DuckDuckGo and extract results"""
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        url = f'https://html.duckduckgo.com/html/?q={quote_plus(query)}'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search results
            for result in soup.find_all('div', class_='result'):
                # Extract title
                title_elem = result.find('a', class_='result__a')
                title = title_elem.get_text() if title_elem else ''
                
                # Extract snippet
                snippet_elem = result.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text() if snippet_elem else ''
                
                if title or snippet:
                    results.append({
                        'title': title,
                        'snippet': snippet,
                        'source': 'DuckDuckGo'
                    })
                
                if len(results) >= num_results:
                    break
        
        return results
    except Exception as e:
        print(f"  {Colors.YELLOW}DuckDuckGo search error: {str(e)[:50]}{Colors.END}")
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
        'Business', 'Service', 'Services', 'Company', 'Companies'
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


def main():
    """Main execution function"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print(ASCII_LOGO)
    print(f"{Colors.END}")
    
    # Check for debug flag
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    if debug_mode:
        sys.argv = [arg for arg in sys.argv if arg not in ['--debug', '-d']]
        print(f"{Colors.YELLOW}🐛 Debug mode enabled{Colors.END}\n")
    
    # Get phone number from user
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
    else:
        phone_number = input(f"{Colors.CYAN}Enter phone number (digits only or formatted): {Colors.END}")
    
    print(f"\n{Colors.YELLOW}Generating search formats...{Colors.END}")
    formats = generate_phone_formats(phone_number)
    
    if not formats:
        return
    
    print(f"{Colors.GREEN}Generated {len(formats)} search format variations{Colors.END}\n")
    
    all_results = {}
    
    # Search each format across multiple engines
    for i, fmt in enumerate(formats, 1):
        print(f"{Colors.BLUE}[{i}/{len(formats)}] Searching: {Colors.END}{fmt}")
        
        format_results = []
        
        # Search Google
        print(f"  {Colors.CYAN}→ Searching Google...{Colors.END}", end=' ')
        google_results = search_google(fmt, num_results=5)
        format_results.extend(google_results)
        print(f"{Colors.GREEN}({len(google_results)} results){Colors.END}")
        
        time.sleep(1)  # Rate limiting
        
        # Search Bing
        print(f"  {Colors.CYAN}→ Searching Bing...{Colors.END}", end=' ')
        bing_results = search_bing(fmt, num_results=5)
        format_results.extend(bing_results)
        print(f"{Colors.GREEN}({len(bing_results)} results){Colors.END}")
        
        time.sleep(1)  # Rate limiting
        
        # Search DuckDuckGo
        print(f"  {Colors.CYAN}→ Searching DuckDuckGo...{Colors.END}", end=' ')
        ddg_results = search_duckduckgo(fmt, num_results=5)
        format_results.extend(ddg_results)
        print(f"{Colors.GREEN}({len(ddg_results)} results){Colors.END}")
        
        all_results[fmt] = format_results
        
        print(f"  {Colors.GREEN}✓ Total: {len(format_results)} results for this format{Colors.END}")
        
        if debug_mode and format_results:
            print(f"  {Colors.YELLOW}Debug: Sample - {format_results[0].get('title', 'N/A')[:60]}...{Colors.END}")
        
        # Rate limiting between formats
        if i < len(formats):
            print(f"  {Colors.YELLOW}⏳ Waiting 3 seconds...{Colors.END}\n")
            time.sleep(3)
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
