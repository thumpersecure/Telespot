# 🔑 TeleSpot API Setup Guide

TeleSpot v3.0 uses official search engine APIs to avoid being blocked by CAPTCHAs and rate limiting. This guide will help you get free API keys.

## Why Use APIs?

**The Problem with Web Scraping:**
- ❌ Search engines block automated scraping
- ❌ CAPTCHAs prevent access
- ❌ IP addresses get blacklisted
- ❌ Unreliable results

**The Solution - Official APIs:**
- ✅ No CAPTCHAs or blocks
- ✅ Reliable, consistent results  
- ✅ Higher rate limits
- ✅ Free tiers available

---

## 🔵 Google Custom Search API (Recommended)

**Free Tier:** 100 searches per day

### Step 1: Get API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Custom Search API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Custom Search API"
   - Click "Enable"
4. Create API credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key

### Step 2: Create Custom Search Engine (CSE)

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click "Add" to create new search engine
3. Configuration:
   - **Sites to search:** Leave empty (searches entire web)
   - **Search engine name:** TeleSpot
   - Check "Search the entire web"
4. Click "Create"
5. Go to "Setup" → "Basics"
6. Copy your **Search engine ID** (CSE ID)

### Step 3: Configure TeleSpot

```bash
./telespot.py --setup
```

When prompted, enter:
- **Google API Key:** (paste from Step 1)
- **Google CSE ID:** (paste from Step 2)

---

## 🟢 Bing Search API (Alternative)

**Free Tier:** 1,000 searches per month (more than Google!)

### Step 1: Get API Key

1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a Microsoft account if you don't have one
3. Create **Bing Search v7** resource:
   - Click "Create a resource"
   - Search for "Bing Search v7"
   - Select the **free tier** (F1)
4. After creation, go to "Keys and Endpoint"
5. Copy **Key 1**

### Step 2: Configure TeleSpot

```bash
./telespot.py --setup
```

When prompted, enter:
- **Bing API Key:** (paste from Step 1)

---

## 🦆 DuckDuckGo Fallback (No Setup)

If you don't configure any APIs, TeleSpot will use DuckDuckGo's Instant Answer API:
- ✅ No API key required
- ✅ Free
- ⚠️ Limited results (much less data than Google/Bing)
- ⚠️ Not suitable for phone number searches (rarely returns useful results)

**Recommendation:** Use at least one of the paid APIs for best results.

---

## 📁 Configuration File

After running `--setup`, your API keys are saved in `.telespot_config`:

```
# TeleSpot API Configuration
google_api_key=YOUR_GOOGLE_API_KEY_HERE
google_cse_id=YOUR_CSE_ID_HERE
bing_api_key=YOUR_BING_API_KEY_HERE
```

### Security Tips:
- 🔒 **Never commit `.telespot_config` to Git**
- 🔒 Add it to `.gitignore`
- 🔒 Don't share your API keys
- 🔒 Keep the file permissions secure: `chmod 600 .telespot_config`

---

## 🚀 Quick Start

1. **Run setup:**
```bash
./telespot.py --setup
```

2. **Test with a phone number:**
```bash
./telespot.py 5555551212
```

3. **If you see results, you're done!** 🎉

---

## 💰 Cost Comparison

| Service | Free Tier | Cost After Free |
|---------|-----------|-----------------|
| Google Custom Search | 100/day | $5 per 1,000 queries |
| Bing Search API | 1,000/month | $3-$7 per 1,000 transactions |
| DuckDuckGo | Unlimited | Always free (but limited results) |

**For occasional use:** Google's 100/day is plenty
**For heavy use:** Bing's 1,000/month is better
**For testing:** DuckDuckGo works without setup

---

## ❓ Troubleshooting

### "API key not configured" warning
Run `./telespot.py --setup` to configure API keys

### "API quota exceeded"
You've hit your daily/monthly limit. Either:
- Wait for the limit to reset
- Use a different API
- Upgrade to a paid tier

### "Invalid API key" error
- Double-check you copied the entire key
- Make sure you enabled the API in the cloud console
- Try regenerating the key

### Still getting 0 results with APIs configured
- Run in debug mode: `./telespot.py --debug 5555551212`
- Check if the APIs are actually being called
- The phone number might genuinely not be indexed online

---

## 🎯 Recommended Setup

**Best combination for reliability:**
1. Set up **both** Google and Bing APIs
2. This gives you redundancy if one fails
3. Total: 100 Google searches/day + 1,000 Bing searches/month
4. Should be plenty for OSINT investigations

**Minimal setup:**
1. Just Bing API (1,000/month is usually enough)
2. Easier to set up than Google
3. More generous free tier

---

## 📞 Support

If you're having trouble with API setup:
1. Check the official documentation links above
2. Run with `--debug` flag to see detailed error messages
3. Open an issue on GitHub: https://github.com/thumpersecure/Telespot

---

**Happy searching!** 🔍
