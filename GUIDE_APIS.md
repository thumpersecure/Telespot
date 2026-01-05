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
| Bing Search | Recommended | 1,000/month | Good backup |
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

## 2. Bing Search API (Azure)

**Free tier:** 1,000 searches/month

### Step 1: Create Azure Account
1. Go to [Azure Portal](https://portal.azure.com/)
2. Sign up for a free account (if needed)

### Step 2: Create Bing Search Resource
1. Click **Create a resource**
2. Search for "Bing Search v7"
3. Click **Create**
4. Fill in:
   - Subscription: Your subscription
   - Resource group: Create new or select existing
   - Name: Any name (e.g., "telespot-bing")
   - Pricing tier: **F1** (Free - 1,000 calls/month)
5. Click **Review + Create** → **Create**

### Step 3: Get API Key
1. Go to your Bing Search resource
2. Click **Keys and Endpoint**
3. Copy **Key 1** or **Key 2**

### Step 4: Add to telespot
```bash
./telespot.py --setup
# Enter your Bing API Key
```

---

## 3. DuckDuckGo Instant Answer API

**No setup required!**

DuckDuckGo's Instant Answer API is free and doesn't require an API key. It's automatically included in every search.

Note: Results are limited to instant answers and related topics, not full web search results.

---

## 4. Dehashed API (Optional)

**Paid service** - For breach database searches

### Step 1: Create Account
1. Go to [Dehashed](https://www.dehashed.com/)
2. Create an account and purchase credits

### Step 2: Get API Key
1. Log into Dehashed
2. Go to your account settings
3. Find your API credentials
4. Format: `email:api_key`

### Step 3: Add to telespot
```bash
./telespot.py --setup
# Enter: your_email@example.com:your_api_key
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
  [+] Bing: CONFIGURED
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

# Bing Search API (Azure)
bing_api_key=a1b2c3...

# Dehashed API (optional)
dehashed_api_key=email@example.com:key123

# Settings
default_country_code=+1
delay_seconds=2
```

**Security:** This file has 600 permissions (owner read/write only).

---

## Troubleshooting

### "Google API quota exceeded"
- Free tier: 100 queries/day
- Resets at midnight UTC
- Use Bing as backup

### "Bing API key invalid"
- Verify key in Azure portal
- Check if resource is still active
- Ensure you're using Bing Search v7

### "No results from DuckDuckGo"
- DuckDuckGo returns instant answers only
- Works better for well-known topics
- Use Google/Bing for comprehensive results

### "Dehashed API error"
- Check your API key format (email:key)
- Verify account has credits
- Check Dehashed service status

---

## Rate Limits

| API | Limit | Reset |
|-----|-------|-------|
| Google | 100/day | Midnight UTC |
| Bing | 1,000/month | Monthly |
| DuckDuckGo | None | N/A |
| Dehashed | Based on plan | N/A |

---

## Best Practices

1. **Start with Google + Bing** - Best coverage
2. **Keep DuckDuckGo enabled** - Free backup
3. **Use Dehashed sparingly** - Save for important searches
4. **Monitor usage** - Check API dashboards regularly
5. **Rotate if needed** - Create multiple API keys if hitting limits
