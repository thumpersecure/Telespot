"""
Shared pattern-extraction logic for `telespot.py` and `telespotx.py`.

Ported from telespot.py's (correct) extractors, plus the email regex that
previously only existed in telespotx.py. Both entrypoints import from here so
name/location/username/email extraction stays consistent and correct.
"""

from __future__ import annotations

import re
from typing import Dict, List

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

_NAME_EXCLUDED = {
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

_NAME_PATTERN = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b')
_USERNAME_AT_PATTERN = re.compile(r'@([A-Za-z0-9_]{3,20})')
_USERNAME_URL_PATTERN = re.compile(
    r'(?:facebook|twitter|instagram|linkedin)\.com/([A-Za-z0-9_.-]{3,30})',
    re.IGNORECASE,
)
_EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
_ZIP_PATTERN = re.compile(r'\b\d{5}(?:-\d{4})?\b')
_STATE_ABBR_PATTERN = re.compile(r'\b(' + '|'.join(US_STATES.keys()) + r')\b')
_CITY_STATE_PATTERN = re.compile(
    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+(' + '|'.join(US_STATES.keys()) + r')\b'
)
_USERNAME_EXCLUDED = {'search', 'profile', 'user', 'pages', 'groups', 'photos', 'videos'}


def extract_names(text: str) -> List[str]:
    """Extract potential full names (2-3 capitalized words) from text."""
    names = _NAME_PATTERN.findall(text)
    return [n for n in names if n not in _NAME_EXCLUDED and len(n.split()) >= 2]


def extract_locations(text: str) -> List[str]:
    """Extract potential US locations (states, City/State, full names, zips)."""
    locations: List[str] = []

    # State abbreviations
    locations.extend(_STATE_ABBR_PATTERN.findall(text))

    # City, State combinations
    for city, state in _CITY_STATE_PATTERN.findall(text):
        locations.append(f"{city}, {state}")

    # Full state names
    for full_name in US_STATES.values():
        if full_name in text:
            locations.append(full_name)

    # Zip codes
    locations.extend(_ZIP_PATTERN.findall(text))

    # Every occurrence is returned (no de-duplication): callers count them
    # with Counter to rank locations and compute confidence. An earlier
    # version returned list(set(...)), which capped every count at 1 and
    # made the "mentioned N times" / consistency scoring meaningless.
    return locations


def extract_usernames(text: str) -> List[str]:
    """Extract potential usernames from text and social URLs (every occurrence)."""
    usernames: List[str] = []
    usernames.extend(_USERNAME_AT_PATTERN.findall(text))
    usernames.extend(_USERNAME_URL_PATTERN.findall(text))
    return [u for u in usernames if u.lower() not in _USERNAME_EXCLUDED]


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text (every occurrence)."""
    return _EMAIL_PATTERN.findall(text)
