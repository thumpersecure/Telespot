# telespot API Setup Guide

This guide covers setting up the APIs for telespot.

## Quick Setup

Run the interactive wizard:
```bash
./telespot.py --setup
```

## APIs Overview

| API | Required | Free Tier | Purpose |
|-----|----------|-----------|---------|
| Google Custom Search | Recommended | 100/day | Best results |
| Brave Search | Recommended | ~2,000/month | Good backup |
| DuckDuckGo | Built-in | Unlimited | Always works |
| Dehashed | Optional | Paid | Breach data |

---

## 1. Google Custom Search API

**Free tier:** 100 searches/day

### Step 1: Get API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services** → **Library**
4. Search for "Custom Search API" and **Enable** it
5. Go to **APIs & Services** → **Credentials**
6. Click **Create Credentials** → **API Key**
7. Copy the API key

### Step 2: Create Custom Search Engine
1. Go to [Programmable Search Engine](https://cse.google.com/cse/)
2. Click **Add** to create a new search engine
3. Under "Sites to search", enter `*.com` (or leave empty)
4. Name your search engine
5. Click **Create**
6. Go to **Control Panel** for your search engine
7. Enable **Search the entire web**
8. Copy the **Search engine ID** (cx parameter)

### Step 3: Add to telespot
```bash
./telespot.py --setup
# Enter your Google API Key
# Enter your CSE ID
```

---

## 2. Brave Search API

**Free tier:** ~2,000 queries/month, 1 query/second (telespot paces Brave at this rate
automatically, even in fast mode)

> Note: This replaced the Bing Search API, which Microsoft retired
> (api.bing.microsoft.com/v7.0/search) in August 2025.

### Step 1: Create a Brave Search API Account
1. Go to [Brave Search API](https://api.search.brave.com/)
2. Sign up and subscribe to the **Data for Search** plan (free tier available)

### Step 2: Get the Subscription Token
1. Open your API dashboard
2. Copy the **subscription token** (used as the `X-Subscription-Token` header)

### Step 3: Add to telespot
```bash
./telespot.py --setup
# Enter your Brave API Key
```

---

## 3. DuckDuckGo Instant Answer API

**No setup required!**

DuckDuckGo's Instant Answer API is free and doesn't require an API key. It's automatically included in every search.

Note: The Instant Answer API returns instant answers and related topics only. When it has
nothing for a phone number, telespot falls back to DuckDuckGo's lite web search page.
DuckDuckGo may answer that fallback with a bot challenge (HTTP 202) when the request comes
from a cloud, VPN or shared IP address. The challenge is intermittent, so each format is retried
once. Telespot reports it and, after three challenged formats in a row, skips the fallback for
the remainder of the run. Google and Brave are not affected.

---

## 4. Dehashed API (Optional)

**Paid service** - For breach database searches

### Step 1: Create Account
1. Go to [Dehashed](https://www.dehashed.com/)
2. Create an account and purchase credits

### Step 2: Get API Key
1. Log into Dehashed
2. Go to your account settings
3. Copy your **v2 API key** (raw key; a legacy `email:key` value is also accepted)

### Step 3: Add to telespot
```bash
./telespot.py --setup
# Enter your Dehashed v2 API key
```

### Usage
```bash
./telespot.py 5555551234 --dehashed
```

---

## Checking Configuration

View your API status:
```bash
./telespot.py --api-status
```

Output:
```
API Configuration Status:
----------------------------------------
  [+] Google: CONFIGURED
  [+] Brave: CONFIGURED
  [+] DuckDuckGo: CONFIGURED
  [-] Dehashed: NOT CONFIGURED
----------------------------------------
  3/4 APIs configured
```

---

## Configuration File

API keys are stored in `.telespot_config`:

```ini
# telespot Configuration

# Google Custom Search API
google_api_key=AIzaSy...
google_cse_id=017576...

# Brave Search API
brave_api_key=BSA...

# Dehashed API (optional)
dehashed_api_key=your_dehashed_v2_key

# Settings
default_country_code=+1
delay_seconds=2          # base delay between formats in safe mode
default_mode=balanced    # fast, balanced or safe
```

**Security:** This file has 600 permissions (owner read/write only).

---

## Troubleshooting

### "Google API quota exceeded"
- Free tier: 100 queries/day
- Resets at midnight UTC
- Use Brave as backup

### "Brave API key invalid"
- Verify the subscription token in the Brave API dashboard
- Check that your plan is still active

### "Google API error 403: ..."
- The message after the status code comes straight from Google
- "API key not valid": re-check the key in the Cloud Console
- "Custom Search API has not been used in project": enable the API (Step 1 above)
- Daily quota messages: wait for the midnight UTC reset or use Brave

### "No results from DuckDuckGo" / "DuckDuckGo answered with a bot challenge"
- DuckDuckGo's Instant Answer API returns instant answers only
- Its web search fallback may serve a bot challenge to scripted clients
- Wait, or try from another network
- Use Google/Brave for comprehensive results

### "Dehashed API error"
- Ensure you are using a Dehashed v2 API key
- Verify account has credits
- Check Dehashed service status

---

## Rate Limits

| API | Limit | Reset |
|-----|-------|-------|
| Google | 100/day | Midnight UTC |
| Brave | ~2,000/month | Monthly |
| DuckDuckGo | None | N/A |
| Dehashed | Based on plan | N/A |

---

## Best Practices

1. **Start with Google + Brave** - Best coverage
2. **Keep DuckDuckGo enabled** - Free backup
3. **Use Dehashed sparingly** - Save for important searches
4. **Monitor usage** - Check API dashboards regularly
5. **Rotate if needed** - Create multiple API keys if hitting limits
