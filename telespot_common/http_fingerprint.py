import random


USER_AGENTS = [
    # Chrome on Windows (latest versions)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    # Firefox (latest)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Mobile
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
]


REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://search.yahoo.com/",
    "",  # Direct navigation (no referer)
]


CAPTCHA_INDICATORS = [
    "captcha",
    "recaptcha",
    "hcaptcha",
    "challenge-platform",
    "are you a robot",
    "are you human",
    "verify you are human",
    "unusual traffic",
    "automated requests",
    "bot detection",
    "access denied",
    "forbidden",
    "rate limit exceeded",
    "please verify",
    "security check",
    "blocked",
    "cf-challenge",
    "cf-browser-verification",
]


def get_random_headers():
    """Get request headers with random User-Agent and realistic browser fingerprint."""

    ua = random.choice(USER_AGENTS)
    is_firefox = "Firefox" in ua

    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
        "Accept-Language": random.choice(
            [
                "en-US,en;q=0.9",
                "en-US,en;q=0.9,es;q=0.8",
                "en-GB,en;q=0.9,en-US;q=0.8",
                "en-US,en;q=0.5",
            ]
        ),
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    if not is_firefox:
        headers.update(
            {
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "sec-ch-ua-platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
            }
        )

    ref = random.choice(REFERERS)
    if ref:
        headers["Referer"] = ref

    return headers


def get_api_headers():
    """Get headers specifically tuned for API requests (JSON-focused)."""

    headers = get_random_headers()
    headers["Accept"] = "application/json, text/html, */*"
    headers.pop("Upgrade-Insecure-Requests", None)
    headers.pop("Sec-Fetch-Dest", None)
    headers.pop("Sec-Fetch-Mode", None)
    headers.pop("Sec-Fetch-Site", None)
    headers.pop("Sec-Fetch-User", None)
    return headers


def detect_captcha(response):
    """Return True if the response appears to be a captcha/block page."""

    if getattr(response, "status_code", None) in (403, 429, 503):
        return True

    try:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return False
    except Exception:
        # If headers aren't accessible, fall back to body scan.
        pass

    try:
        body = response.text.lower()
        return any(indicator in body for indicator in CAPTCHA_INDICATORS)
    except Exception:
        return False

