#!/usr/bin/env python3
"""
TeleSpot - DuckDuckGo Multi-Format Phone Number Search
Searches for phone numbers in various formats and analyzes patterns in results
"""

import subprocess
import json
import time
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import urlparse

ASCII_LOGO = """
████████╗███████╗██╗     ███████╗███████╗██████╗  ██████╗ ████████╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
   ██║   █████╗  ██║     █████╗  ███████╗██████╔╝██║   ██║   ██║   
   ██║   ██╔══╝  ██║     ██╔══╝  ╚════██║██╔═══╝ ██║   ██║   ██║   
   ██║   ███████╗███████╗███████╗███████║██║     ╚██████╔╝   ██║   
   ╚═╝   ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝    ╚═╝   
                                                         version 1.0
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


def generate_phone_formats(phone_number):
    """
    Generate various phone number formats for searching
    Args:
        phone_number: string of digits (e.g., "5555551212" or "15555551212")
    Returns:
        list of formatted phone number strings
    """
    # Strip all non-digit characters
    digits = re.sub(r'\D', '', phone_number)
    
    # Handle 10-digit or 11-digit numbers
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
        f'"{area}-{prefix}-{line}"',           # "555-555-1212"
        f'"({area}) {prefix}-{line}"',         # "(555) 555-1212"
        f'"{area}{prefix}{line}"',             # "5555551212"
        f'"{country}{area}{prefix}{line}"',    # "15555551212"
        f'"{country} ({area}) {prefix}-{line}"', # "1 (555) 555-1212"
        f'"{country} {area}-{prefix}-{line}"', # "1 555-555-1212"
        f'({area}-{prefix}-{line})',           # (555-555-1212)
        f'{area}-{prefix}-{line}',             # 555-555-1212
    ]
    
    return formats


def search_ddgr(query, num_results=10):
    """
    Execute ddgr search and return results
    Args:
        query: search query string
        num_results: number of results to retrieve
    Returns:
        list of result dictionaries
    """
    try:
        # Use ddgr with JSON output
        cmd = ['ddgr', '--json', '-n', str(num_results), query]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"{Colors.YELLOW}Warning: ddgr returned non-zero exit code for query: {query}{Colors.END}")
            return []
        
        # Parse JSON output
        if result.stdout.strip():
            results = json.loads(result.stdout)
            return results
        else:
            return []
            
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}Error: Search timed out for query: {query}{Colors.END}")
        return []
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error: Failed to parse JSON output: {e}{Colors.END}")
        return []
    except FileNotFoundError:
        print(f"{Colors.RED}Error: ddgr not found. Please install ddgr first.{Colors.END}")
        print(f"Install with: pip install ddgr")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error during search: {e}{Colors.END}")
        return []


def extract_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Remove www. prefix
        domain = re.sub(r'^www\.', '', domain)
        return domain
    except:
        return url


def extract_names(text):
    """
    Extract potential names from text (capitalized words that might be names)
    Simple heuristic: sequences of 2-3 capitalized words
    """
    # Pattern for potential names (2-3 capitalized words in sequence)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    names = re.findall(name_pattern, text)
    
    # Filter out common non-name words
    excluded = {'Phone', 'Number', 'Call', 'Contact', 'Email', 'Address', 
                'Street', 'City', 'State', 'Country', 'The', 'This', 'That',
                'Search', 'Results', 'View', 'More', 'Less', 'Show', 'Hide'}
    
    filtered_names = []
    for name in names:
        words = name.split()
        if not any(word in excluded for word in words):
            filtered_names.append(name)
    
    return filtered_names


def extract_locations(text):
    """
    Extract potential locations from text
    """
    # Pattern for US states (abbreviations and full names)
    states = r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b'
    
    # Common city patterns (capitalized word followed by state)
    city_state_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+(' + states + r')\b'
    
    locations = []
    
    # Find state abbreviations
    state_matches = re.findall(states, text)
    locations.extend(state_matches)
    
    # Find city, state combinations
    city_state_matches = re.findall(city_state_pattern, text)
    locations.extend([f"{city}, {state}" for city, state in city_state_matches])
    
    return list(set(locations))


def analyze_patterns(all_results):
    """
    Analyze results for common patterns
    Args:
        all_results: dict mapping search format to list of results
    Returns:
        dict with pattern analysis
    """
    # Collect all data
    all_domains = []
    all_titles = []
    all_abstracts = []
    all_urls = []
    
    for format_str, results in all_results.items():
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '')
            abstract = result.get('abstract', '')
            
            all_urls.append(url)
            all_titles.append(title)
            all_abstracts.append(abstract)
            all_domains.append(extract_domain(url))
    
    # Count domains
    domain_counter = Counter(all_domains)
    
    # Extract and count names
    all_text = ' '.join(all_titles + all_abstracts)
    names = extract_names(all_text)
    name_counter = Counter(names)
    
    # Extract and count locations
    locations = extract_locations(all_text)
    location_counter = Counter(locations)
    
    # Identify common URL patterns
    url_patterns = defaultdict(list)
    for url in all_urls:
        domain = extract_domain(url)
        url_patterns[domain].append(url)
    
    # Check for business indicators
    business_keywords = ['business', 'company', 'corp', 'inc', 'llc', 'ltd', 
                         'service', 'services', 'professional', 'office']
    personal_keywords = ['person', 'individual', 'personal', 'private', 'residential']
    spam_keywords = ['spam', 'scam', 'robocall', 'telemarketer', 'fraud', 'complaint']
    
    business_count = sum(1 for text in all_titles + all_abstracts 
                        if any(kw in text.lower() for kw in business_keywords))
    personal_count = sum(1 for text in all_titles + all_abstracts 
                        if any(kw in text.lower() for kw in personal_keywords))
    spam_count = sum(1 for text in all_titles + all_abstracts 
                    if any(kw in text.lower() for kw in spam_keywords))
    
    return {
        'total_results': len(all_urls),
        'unique_domains': len(domain_counter),
        'domain_frequency': domain_counter.most_common(10),
        'common_names': name_counter.most_common(5),
        'common_locations': location_counter.most_common(5),
        'business_indicators': business_count,
        'personal_indicators': personal_count,
        'spam_indicators': spam_count,
        'url_patterns': dict(url_patterns)
    }


def print_pattern_summary(patterns):
    """
    Print a formatted summary of pattern analysis
    """
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}PATTERN ANALYSIS SUMMARY{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")
    
    print(f"{Colors.CYAN}Total Results Found:{Colors.END} {patterns['total_results']}")
    print(f"{Colors.CYAN}Unique Domains:{Colors.END} {patterns['unique_domains']}\n")
    
    # Domain patterns
    if patterns['domain_frequency']:
        print(f"{Colors.BOLD}{Colors.BLUE}Most Common Domains:{Colors.END}")
        for domain, count in patterns['domain_frequency']:
            percentage = (count / patterns['total_results']) * 100 if patterns['total_results'] > 0 else 0
            print(f"  • {Colors.GREEN}{domain}{Colors.END}: {count} occurrences ({percentage:.1f}%)")
        print()
    
    # Name patterns
    if patterns['common_names']:
        print(f"{Colors.BOLD}{Colors.BLUE}Potential Names Found:{Colors.END}")
        for name, count in patterns['common_names']:
            print(f"  • {Colors.GREEN}{name}{Colors.END}: mentioned {count} time(s)")
        print()
    
    # Location patterns
    if patterns['common_locations']:
        print(f"{Colors.BOLD}{Colors.BLUE}Locations Mentioned:{Colors.END}")
        for location, count in patterns['common_locations']:
            print(f"  • {Colors.GREEN}{location}{Colors.END}: {count} occurrence(s)")
        print()
    
    # Type indicators
    print(f"{Colors.BOLD}{Colors.BLUE}Content Type Indicators:{Colors.END}")
    if patterns['business_indicators'] > 0:
        print(f"  • {Colors.YELLOW}Business-related:{Colors.END} {patterns['business_indicators']} results")
    if patterns['personal_indicators'] > 0:
        print(f"  • {Colors.YELLOW}Personal-related:{Colors.END} {patterns['personal_indicators']} results")
    if patterns['spam_indicators'] > 0:
        print(f"  • {Colors.RED}Spam/Scam indicators:{Colors.END} {patterns['spam_indicators']} results")
    
    if patterns['business_indicators'] == 0 and patterns['personal_indicators'] == 0 and patterns['spam_indicators'] == 0:
        print(f"  • {Colors.YELLOW}No specific type indicators found{Colors.END}")
    
    print()
    
    # Pattern insights
    print(f"{Colors.BOLD}{Colors.BLUE}Key Insights:{Colors.END}")
    
    if patterns['total_results'] == 0:
        print(f"  • {Colors.YELLOW}No results found for this phone number{Colors.END}")
    else:
        # Determine primary domain type
        top_domains = [d for d, c in patterns['domain_frequency'][:3]]
        
        social_domains = ['facebook.com', 'linkedin.com', 'twitter.com', 'instagram.com', 'tiktok.com']
        directory_domains = ['whitepages.com', 'yellowpages.com', '411.com', 'spokeo.com', 'truecaller.com']
        
        social_count = sum(1 for d in top_domains if any(s in d for s in social_domains))
        directory_count = sum(1 for d in top_domains if any(s in d for s in directory_domains))
        
        if social_count > 0:
            print(f"  • {Colors.GREEN}Appears on social media platforms{Colors.END}")
        if directory_count > 0:
            print(f"  • {Colors.GREEN}Listed in online directories{Colors.END}")
        
        if patterns['spam_indicators'] > 2:
            print(f"  • {Colors.RED}Multiple spam/scam warnings found - exercise caution{Colors.END}")
        
        if len(patterns['common_names']) > 0:
            primary_name = patterns['common_names'][0][0]
            print(f"  • {Colors.GREEN}Most associated name: {primary_name}{Colors.END}")
        
        if len(patterns['common_locations']) > 0:
            primary_location = patterns['common_locations'][0][0]
            print(f"  • {Colors.GREEN}Most associated location: {primary_location}{Colors.END}")
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")


def main():
    """Main execution function"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print(ASCII_LOGO)
    print(f"{Colors.END}")
    
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
    
    # Search each format with rate limiting
    for i, fmt in enumerate(formats, 1):
        print(f"{Colors.BLUE}[{i}/{len(formats)}] Searching: {Colors.END}{fmt}")
        
        results = search_ddgr(fmt, num_results=10)
        all_results[fmt] = results
        
        print(f"  {Colors.GREEN}→ Found {len(results)} results{Colors.END}")
        
        # Rate limiting: wait 2 seconds between searches (best practice to avoid throttling)
        if i < len(formats):
            print(f"  {Colors.YELLOW}⏳ Waiting 2 seconds...{Colors.END}")
            time.sleep(2)
    
    # Analyze patterns
    print(f"\n{Colors.YELLOW}Analyzing patterns across all results...{Colors.END}")
    patterns = analyze_patterns(all_results)
    
    # Print summary
    print_pattern_summary(patterns)
    
    # Optional: Save detailed results to file
    save_option = input(f"{Colors.CYAN}Save detailed results to JSON file? (y/n): {Colors.END}")
    if save_option.lower() == 'y':
        filename = f"phone_search_{re.sub(r'\\D', '', phone_number)}.json"
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
        sys.exit(1)
