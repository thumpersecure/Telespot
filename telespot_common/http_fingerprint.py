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


# Phrases that only appear on real bot-challenge / captcha pages.
#
# Earlier versions also matched generic words such as "blocked", "forbidden",
# "access denied", "security check" and "please verify". Those words show up
# in ordinary search results for phone numbers all the time ("Blocked 12
# times", "Access denied to this listing", ...), which made the tool treat
# perfectly good result pages as captchas, back off for many seconds and then
# drop the results entirely. Keep this list specific.
CAPTCHA_INDICATORS = [
    "captcha",
    "recaptcha",
    "hcaptcha",
    "challenge-platform",
    "cf-challenge",
    "cf-browser-verification",
    "are you a robot",
    "verify you are human",
    "unusual traffic from your computer",
    "automated queries",
    # DuckDuckGo "anomaly" page (served with HTTP 202 to suspected bots)
    "bots use duckduckgo too",
    "complete the following challenge",
    "anomaly-modal",
    "anomaly_modal",
]

# Only the first part of a page is scanned. Challenge pages are small and put
# their message at the top; large result pages carry user-generated snippets
# further down that we must not match against.
_BODY_SCAN_LIMIT = 24_000


def _brotli_available():
    """True if a brotli decoder is importable (requests/httpx need one)."""
    for mod in ("brotli", "brotlicffi"):
        try:
            __import__(mod)
            return True
        except ImportError:
            continue
    return False


_BROTLI_OK = _brotli_available()


def accept_encoding():
    """Return an Accept-Encoding value the installed HTTP stack can decode.

    Advertising ``br`` without a brotli decoder installed makes servers such
    as DuckDuckGo send brotli bodies that requests/httpx then hand back as raw
    compressed bytes. Every regex in the scrapers then matches nothing and
    the tool silently reports zero results.
    """
    return "gzip, deflate, br" if _BROTLI_OK else "gzip, deflate"


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
        "Accept-Encoding": accept_encoding(),
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


def merge_headers(fresh, caller_headers):
    """Merge a fresh fingerprint under caller-supplied headers.

    Caller headers win, so authentication headers (Brave subscription token,
    Dehashed API key, ...) survive a retry that regenerates the fingerprint.
    """
    merged = dict(fresh)
    merged.update(caller_headers or {})
    return merged


def is_bot_challenge_page(text):
    """Return True if ``text`` looks like a captcha / bot-challenge page."""
    try:
        body = text[:_BODY_SCAN_LIMIT].lower()
    except Exception:
        return False
    return any(indicator in body for indicator in CAPTCHA_INDICATORS)


def detect_captcha(response, api_mode=False):
    """Return True if the response appears to be a captcha/block page.

    ``api_mode`` should be True for JSON API endpoints (Google CSE, Brave,
    Dehashed, DuckDuckGo Instant Answers). For those, a 403 is an
    authentication / quota error that the caller must report, not a captcha
    to retry, and the body is never scanned for challenge phrases because it
    is data, not a page.
    """

    status = getattr(response, "status_code", None)

    if status in (429, 503):
        return True

    if status == 403 and not api_mode:
        return True

    if api_mode:
        return False

    try:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type or "javascript" in content_type:
            return False
    except Exception:
        # If headers aren't accessible, fall back to body scan.
        pass

    try:
        return is_bot_challenge_page(response.text)
    except Exception:
        return False
