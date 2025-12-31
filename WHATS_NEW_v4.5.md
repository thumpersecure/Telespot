# 🎉 TeleSpot v4.5 - New Features

## What's New

### 1. 🎯 Site-Specific Search (`--site`)

Limit your searches to specific people-finder and social media sites for more targeted results.

**Available Sites:**
- `yellowpages.com` - Business and residential directory
- `whitepages.com` - People finder and reverse lookup
- `thatsthem.com` - Reverse phone lookup specialist
- `information.com` - Public records search
- `instantcheckmate.com` - Background check service
- `facebook.com` - Social media profiles
- `yahoo.com` - General search engine

**Usage:**
```bash
# Search only WhitePages
./telespot.py --site whitepages.com 5555551212

# Search only Facebook
./telespot.py --site facebook.com 5555551212

# Combine with keywords
./telespot.py --site yellowpages.com --keywords "Philadelphia" 2155551234
```

**How It Works:**
Adds `site:whitepages.com` to all 10 phone number format searches, forcing search engines to only return results from that specific domain.

**Why Use This:**
- ✅ More focused results
- ✅ Faster searches (fewer irrelevant results)
- ✅ Better for specific use cases (e.g., only social media, only directories)
- ✅ Reduces noise in results

---

### 2. 🔓 Dehashed Integration (`--dehashed`)

Search the Dehashed breach database for phone numbers that have appeared in data breaches.

**What is Dehashed:**
Dehashed is a paid service that aggregates data from security breaches, leaks, and public records. It's commonly used for:
- Security research
- Checking if your data has been compromised
- OSINT investigations
- Credential verification

**Setup:**
```bash
# Run setup and enter Dehashed credentials
./telespot.py --setup

# Enter when prompted:
# - Dehashed Email: your@email.com
# - Dehashed API Key: your_api_key_here
```

**Usage:**
```bash
# Include Dehashed in search
./telespot.py --dehashed 5555551212

# Combine with other options
./telespot.py --dehashed --verbose 5555551212
```

**What You Get:**
- Associated usernames from breaches
- Email addresses linked to the phone number
- Database names where the number appeared
- Timestamp information

**Example Output:**
```
Results by Source:
  • Dehashed: 12 results
  • Google: 8 results
  • Bing: 5 results

From Dehashed:
[1] Dehashed: john.smith@example.com
Description: Username: jsmith123, Email: john.smith@example.com, Database: Collection1
```

**Cost:**
- Dehashed is a paid service (~$20/week or custom pricing)
- Get API access at: https://dehashed.com/

---

### 3. 🎵 DTMF Tone Playback (`--dtmf`)

Play phone dialing tones (DTMF) while searching for a fun audio experience!

**What is DTMF:**
Dual-Tone Multi-Frequency signaling - the beep sounds you hear when dialing a phone number.

**Usage:**
```bash
# Play tones while searching
./telespot.py --dtmf 5555551212
```

**What Happens:**
```
🎵 Playing DTMF tones for: 5555551212
📞 Dialing: 5
📞 Dialing: 5
📞 Dialing: 5
... [beep sounds]
✓ Dial complete!

[Then normal search proceeds]
```

**Why Use This:**
- 🎉 Fun factor!
- 🔊 Audio feedback during long searches
- 👴 Nostalgia for rotary/touch-tone phones
- 🎭 Adds personality to the tool

**Technical Note:**
- On Unix/Linux/Mac: Uses system beep
- On Windows: Uses winsound library
- Fallback: Visual-only if audio unavailable

---

### 4. 👤 Username Correlation (`--usernames`)

Automatically find usernames and social media handles that appear in 2 or more search results - a strong indicator of legitimacy.

**The Problem:**
When searching for a phone number, you might find dozens of results with different usernames. Which ones are actually associated with the number?

**The Solution:**
Username correlation identifies handles that appear multiple times across different sources, indicating they're likely legitimate.

**Usage:**
```bash
# Focus on username analysis
./telespot.py --usernames 5555551212

# See full details with verbose
./telespot.py --usernames --verbose 5555551212
```

**What It Finds:**
- Facebook profiles
- Twitter/X handles  
- Instagram accounts
- LinkedIn profiles
- TikTok accounts
- Reddit usernames
- GitHub profiles
- YouTube channels
- Any @mentions in text

**Example Output:**
```
🔗 Username Correlations (appearing in 2+ results):
  • @johnsmith (Facebook, LinkedIn): 3 occurrence(s)
    - https://facebook.com/johnsmith
    - https://linkedin.com/in/johnsmith
  • @jsmith123 (Twitter, Instagram): 2 occurrence(s)
    - https://twitter.com/jsmith123
    - https://instagram.com/jsmith123
```

**Why This Matters:**
- ✅ **High confidence** - Multiple sources = more likely to be real
- ✅ **Cross-platform verification** - Same username on different platforms
- ✅ **Saves time** - Focuses on the most promising leads
- ✅ **Social media OSINT** - Direct links to investigate further

**How It Works:**
1. Extracts all usernames from URLs and text across all search results
2. Identifies which usernames appear in 2 or more different results
3. Groups them by platform (Facebook, Twitter, etc.)
4. Shows URLs where each username was found
5. Adds +5 points to confidence score if correlations found

**Best Practices:**
```bash
# Comprehensive social media search
./telespot.py --site facebook.com --usernames 5555551212

# Check multiple sites for username consistency
./telespot.py --usernames --verbose 5555551212

# Combine with keywords for better targeting
./telespot.py --usernames --keywords "Philadelphia" 5555551212
```

---

## Feature Combinations

### The Ultimate Search
```bash
./telespot.py \
  --verbose \
  --colorful \
  --dehashed \
  --usernames \
  --dtmf \
  --keywords "John Smith Philadelphia" \
  --dossier person \
  5555551212
```

This will:
1. 🎵 Play DTMF tones
2. 🔓 Search Dehashed
3. 🔍 Search all engines (Google, Bing, DuckDuckGo)
4. 👤 Find correlated usernames
5. 📋 Generate person dossier
6. 🎨 Display with colors
7. 📄 Show verbose results
8. 🔑 Include keywords in searches

### Social Media Focus
```bash
./telespot.py \
  --site facebook.com \
  --usernames \
  --verbose \
  5555551212
```

### People-Finder Focus
```bash
./telespot.py \
  --site whitepages.com \
  --keywords "Jane Doe" \
  --dossier person \
  5555551212
```

### Breach Database Focus
```bash
./telespot.py \
  --dehashed \
  --usernames \
  --verbose \
  5555551212
```

---

## Updated Confidence Score

The confidence score now includes username correlation:

| Component | Weight | Description |
|-----------|--------|-------------|
| Results found | 30% | More results = higher confidence |
| Name consistency | 35% | Same name appearing multiple times |
| Location consistency | 20% | Same location appearing multiple times |
| Multiple sources | 10% | Results from 2+ search engines |
| **Username correlation** | **5%** | **NEW: Usernames appearing 2+ times** |

**Example:**
```
🎯 Confidence Score: 87% (HIGH)

Breakdown:
  ✓ 45 results found: 30/30 points
  ✓ "John Smith" in 15 results: 32/35 points
  ✓ "Philadelphia, PA" in 12 results: 16/20 points
  ✓ 3 search engines: 10/10 points
  ✓ @johnsmith found 3 times: 5/5 points
  = 87% total
```

---

## API Configuration Updates

The `--setup` wizard now includes Dehashed:

```bash
./telespot.py --setup

TeleSpot API Setup Wizard

Configure search engine APIs and optional services:

1. Google Custom Search API (Free: 100 searches/day)
2. Bing Search API (Free tier: 1000 searches/month)
3. Dehashed API (Paid service)          <-- NEW!
4. DuckDuckGo (Always included, no API needed)

Configure APIs? (y/n): y

...

Dehashed API Setup (Optional):         <-- NEW SECTION!
Enter Dehashed Email: your@email.com
Enter Dehashed API Key: xxxxxx

✓ Configuration saved to .telespot_config
```

---

## Use Cases

### 1. Skip Tracing (People Finding)
```bash
# Start broad
./telespot.py --verbose 5555551212

# Narrow to people-finders
./telespot.py --site whitepages.com 5555551212

# Check social media
./telespot.py --site facebook.com --usernames 5555551212

# Check breaches
./telespot.py --dehashed --usernames 5555551212
```

### 2. Fraud Investigation
```bash
# Comprehensive search
./telespot.py --verbose --colorful --dehashed --usernames --dossier person 5555551212

# Focus on username patterns
./telespot.py --usernames --verbose 5555551212

# Check if number appears in known scam databases
./telespot.py --keywords "scam fraud complaint" 5555551212
```

### 3. Background Checks
```bash
# People-finder sites
./telespot.py --site whitepages.com --site thatsthem.com 5555551212

# Social media presence
./telespot.py --usernames --verbose 5555551212

# Breach history
./telespot.py --dehashed 5555551212
```

### 4. Social Media OSINT
```bash
# Facebook only
./telespot.py --site facebook.com --usernames 5555551212

# Username discovery
./telespot.py --usernames --verbose --colorful 5555551212

# Cross-platform analysis
./telespot.py --usernames --keywords "instagram twitter" 5555551212
```

---

## Tips & Best Practices

### Using Site-Specific Search
- Start with `whitepages.com` for general info
- Use `facebook.com` for social media leads
- Try `yellowpages.com` for business numbers
- Combine with `--keywords` for better targeting

### Using Dehashed Effectively
- Always combine with `--usernames` flag
- Great for finding email addresses
- Useful for credential verification
- Best with `--verbose` to see all details

### Using Username Correlation
- Always use with `--verbose` to see URLs
- Combine with `--site facebook.com` for social media
- Look for patterns (same username across platforms)
- Higher occurrence count = higher confidence

### Using DTMF Tones
- Fun for demos and presentations
- Good for audio feedback on long searches
- Can be combined with any other flags
- Purely cosmetic - doesn't affect results

---

**Upgrade from v4.0 to v4.5:**

Simply download the new version and run:
```bash
./telespot.py --setup  # Re-enter API keys if needed
```

Your existing `.telespot_config` file will work, but you can add Dehashed credentials with `--setup` if desired.

---

**Made with ❤️ for OSINT and security research**
