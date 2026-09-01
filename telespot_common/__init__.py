"""
Shared utilities for `telespot.py` and `telespotx.py`.

This package is intentionally small and dependency-free so both entrypoint
scripts can import it without changing installation requirements.
"""

from .colors import Colors
from .config import read_simple_kv_config, resolve_config_path
from .dedupe import deduplicate_results_dict, deduplicate_results_list
from .http_fingerprint import (
    CAPTCHA_INDICATORS,
    REFERERS,
    USER_AGENTS,
    detect_captcha,
    get_api_headers,
    get_random_headers,
)
from .patterns import (
    US_STATES,
    extract_emails,
    extract_locations,
    extract_names,
    extract_usernames,
)

__all__ = [
    "Colors",
    "CAPTCHA_INDICATORS",
    "REFERERS",
    "USER_AGENTS",
    "US_STATES",
    "deduplicate_results_dict",
    "deduplicate_results_list",
    "detect_captcha",
    "extract_emails",
    "extract_locations",
    "extract_names",
    "extract_usernames",
    "get_api_headers",
    "get_random_headers",
    "read_simple_kv_config",
    "resolve_config_path",
]
