# telespot API Setup Guide

This guide covers setting up optional API integrations for enhanced phone number lookups.

## Overview

telespot works without any APIs by scraping search engines directly. However, APIs can provide:
- Validated carrier information
- Line type (mobile, landline, VoIP)
- Caller ID names (CNAM)
- More accurate location data
- Higher reliability

## Quick Setup

Run the interactive setup:
```bash
python3 telespot.py --setup
```

This will guide you through configuring each API.

---

## Available APIs

### 1. NumVerify (Recommended for Free)

**What it provides:**
- Phone number validation
- Carrier name
- Line type
- Location
- Country information

**Free tier:** 100 requests/month

**Setup:**
1. Go to https://numverify.com/
2. Click "Get Free API Key"
3. Create an account
4. Copy your API key
5. Add to config.txt:
   ```
   numverify_api_key=YOUR_KEY_HERE
   ```

---

### 2. AbstractAPI

**What it provides:**
- Phone validation
- Carrier details
- Line type
- Location data

**Free tier:** 250 requests/month

**Setup:**
1. Go to https://www.abstractapi.com/phone-validation-api
2. Click "Get Started Free"
3. Create an account
4. Go to Dashboard → Phone Validation
5. Copy your API key
6. Add to config.txt:
   ```
   abstract_api_key=YOUR_KEY_HERE
   ```

---

### 3. Twilio (Paid)

**What it provides:**
- Carrier lookup
- Caller ID name
- Line type
- Most accurate data

**Cost:** ~$0.005 per lookup

**Setup:**
1. Go to https://www.twilio.com/
2. Create an account
3. Go to Console → Account → API credentials
4. Copy Account SID and Auth Token
5. Add to config.txt:
   ```
   twilio_account_sid=YOUR_ACCOUNT_SID
   twilio_auth_token=YOUR_AUTH_TOKEN
   ```

---

### 4. OpenCNAM (Paid)

**What it provides:**
- Caller ID Name (CNAM)
- Real name lookups
- Business name lookups

**Cost:** ~$0.004 per lookup

**Setup:**
1. Go to https://www.opencnam.com/
2. Create an account
3. Go to Dashboard → API Credentials
4. Copy Account SID and Auth Token
5. Add to config.txt:
   ```
   opencnam_account_sid=YOUR_ACCOUNT_SID
   opencnam_auth_token=YOUR_AUTH_TOKEN
   ```

---

### 5. Telnyx (Paid)

**What it provides:**
- Phone number intelligence
- Carrier data
- Number portability info

**Setup:**
1. Go to https://portal.telnyx.com/
2. Create an account
3. Go to API Keys
4. Generate a new key
5. Add to config.txt:
   ```
   telnyx_api_key=YOUR_API_KEY
   ```

---

## Configuration File

All API keys are stored in `config.txt`:

```ini
# telespot Configuration File

# API Keys
numverify_api_key=abc123def456
abstract_api_key=xyz789uvw012
twilio_account_sid=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
twilio_auth_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
opencnam_account_sid=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
opencnam_auth_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
telnyx_api_key=KEY0123456789ABCDEF

# Settings
default_country_code=+1
rate_limit_min=3
rate_limit_max=5
```

---

## Check API Status

See which APIs are configured:

```bash
python3 telespot.py --api-status
```

Output:
```
API Configuration Status:
----------------------------------------
  [+] NumVerify: LOADED
  [+] AbstractAPI: LOADED
  [-] Twilio: NOT CONFIGURED
  [-] OpenCNAM: NOT CONFIGURED
  [-] Telnyx: NOT CONFIGURED
----------------------------------------
  2/5 APIs configured
```

---

## API Comparison

| API | Free Tier | Cost | Best For |
|-----|-----------|------|----------|
| NumVerify | 100/mo | Free | Basic validation |
| AbstractAPI | 250/mo | Free | More free lookups |
| Twilio | None | $0.005 | Professional use |
| OpenCNAM | None | $0.004 | Name lookups |
| Telnyx | None | Varies | Enterprise |

---

## Best Practices

### For Casual Use
- Set up NumVerify (free 100/month)
- Set up AbstractAPI (free 250/month)
- Total: 350 free lookups per month

### For Regular Use
- Add Twilio for accurate carrier info
- Add OpenCNAM for name lookups
- Budget: ~$5-20/month depending on usage

### For Professional Use
- Configure all APIs
- Set up multiple accounts for redundancy
- Consider enterprise plans

---

## Security Notes

1. **Never commit config.txt to public repositories**
   - Add `config.txt` to `.gitignore`

2. **Protect your API keys**
   - Don't share them
   - Rotate periodically
   - Monitor usage

3. **Set file permissions**
   ```bash
   chmod 600 config.txt
   ```

---

## Troubleshooting

### "API key not working"
- Check for typos
- Verify the key is active in your account
- Check if you've exceeded rate limits

### "API returning errors"
- Check account balance (for paid APIs)
- Verify phone number format
- Check API status pages

### "No API data in results"
- Run `--api-status` to verify configuration
- Use `-d` debug mode to see API responses
- Check your internet connection

---

## Rate Limits

| API | Rate Limit |
|-----|-----------|
| NumVerify Free | 100/month |
| AbstractAPI Free | 250/month |
| Twilio | 100/second |
| OpenCNAM | Varies |

---

## Need Help?

- NumVerify: https://numverify.com/documentation
- AbstractAPI: https://docs.abstractapi.com/phone-validation
- Twilio: https://www.twilio.com/docs/lookup/api
- OpenCNAM: https://docs.opencnam.com/
- Telnyx: https://developers.telnyx.com/docs/api/v2/number-lookup

Or open an issue: https://github.com/thumpersecure/Telespot/issues
