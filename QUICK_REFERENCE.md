# 🚀 TeleSpot v4.0 - Quick Reference Guide

## What's New in v4.0

### ✅ All Your Requested Features Implemented!

#### 1. ✨ 10 Search Formats (Previously 4)
- **Basic 4**: `555-555-1212`, `5555551212`, `(555) 555-1212`, `+1555-555-1212`
- **Quoted 4**: All basic formats wrapped in `"quotes"` for exact matching
- **Special 2**: `(555-555-1212)` and `"(555) 555-1212)"`

**Why this matters:** Quoted searches dramatically improve accuracy!

#### 2. 🦆 DuckDuckGo Always Included
- No API setup required
- Automatically runs with every search
- Free backup to Google/Bing APIs

#### 3. 🎯 Confidence Score (0-100%)
Shows how accurate/reliable the results are:
- **75-100%** 🟢 HIGH - Strong evidence
- **50-74%** 🟡 MEDIUM - Moderate evidence  
- **0-49%** 🔴 LOW - Weak evidence

#### 4. 📋 Verbose Mode (`--verbose` or `-v`)
See complete listings with:
- Full URLs
- Complete titles
- Full descriptions
- Source attribution

```bash
./telespot.py --verbose 5555551212
```

#### 5. 🎨 Colorful Mode (`--colorful` or `-c`)
Enhanced visual experience with:
- Bright colors
- Color-coded sections
- Better contrast

```bash
./telespot.py --colorful 5555551212
```

#### 6. 🔑 Keyword Search (`--keywords` or `-k`)
Add context to your searches:

```bash
# Search with name
./telespot.py --keywords "John Smith" 5555551212

# Search with business  
./telespot.py --keywords "Acme Industries" 5555551212

# Multiple keywords
./telespot.py --keywords "Philadelphia lawyer firm" 2155551234
```

**How it works:** Keywords are added to all 10 phone formats:
```
555-555-1212 + John+Smith
"5555551212" + John+Smith
(555) 555-1212 + John+Smith
...and so on
```

#### 7. ⏱️ Custom Delay (`--delay`)
Adjust rate limiting between searches:

```bash
# Slower (safer for API limits)
./telespot.py --delay 5 5555551212

# Faster (if you have high API quotas)
./telespot.py --delay 1 5555551212

# Default is 2 seconds
./telespot.py 5555551212
```

#### 8. 📋 Dossier Mode (`--dossier`)
Specialized investigation modes:

```bash
# Person investigation
./telespot.py --dossier person 5555551212

# Business investigation
./telespot.py --dossier business 8005551212
```

Adds specialized header to results indicating investigation type.

#### 9. 💾 TXT File Output (Default)
- Clean, readable text format
- Better for documentation
- Easier to share/print
- Includes all result details

**Custom naming:**
```
Save results to file? (y/n): y
Enter filename (or press Enter for default): investigation_smith
✓ Results saved to: investigation_smith.txt
```

**Default naming:**
```
telespot_5555551212_20241228_143022.txt
```

#### 10. 📊 Complete Result Details
Every search result now includes:
- Title
- URL  
- Description/Snippet
- Source (Google/Bing/DuckDuckGo)

---

## Quick Command Examples

### Basic Search
```bash
./telespot.py 5555551212
```

### Maximum Detail
```bash
./telespot.py --verbose --colorful 5555551212
```

### Investigative Search
```bash
./telespot.py --verbose --colorful --keywords "John Smith" --dossier person 5555551212
```

### Business Lookup
```bash
./telespot.py --keywords "Acme Corp Philadelphia" --dossier business 8005551212
```

### Slow & Careful (High API Quotas)
```bash
./telespot.py --delay 5 --verbose 5555551212
```

### The Works™
```bash
./telespot.py \
  --verbose \
  --colorful \
  --keywords "Philadelphia lawyer" \
  --dossier person \
  --delay 3 \
  2155551234
```

---

## Feature Comparison

| Feature | v3.0 | v4.0 |
|---------|------|------|
| Search formats | 4 | **10** ✅ |
| DuckDuckGo | Optional | **Always included** ✅ |
| Confidence score | ❌ | **Yes (0-100%)** ✅ |
| Verbose mode | ❌ | **Yes** ✅ |
| Colorful mode | ❌ | **Yes** ✅ |
| Keywords | ❌ | **Yes** ✅ |
| Custom delay | Fixed 2s | **Adjustable** ✅ |
| Dossier mode | ❌ | **Yes** ✅ |
| File format | JSON | **TXT** ✅ |
| Custom filename | ❌ | **Yes** ✅ |

---

## Tips & Tricks

### 🎯 Getting Better Results

1. **Use keywords** when you know context:
   ```bash
   ./telespot.py --keywords "personal injury attorney" 2155551234
   ```

2. **Combine verbose and colorful** for best UX:
   ```bash
   ./telespot.py -v -c 5555551212
   ```

3. **Use dossier mode** for focused investigations:
   ```bash
   ./telespot.py --dossier person --keywords "Jane Doe" 5555551212
   ```

4. **Increase delay** if hitting API rate limits:
   ```bash
   ./telespot.py --delay 5 5555551212
   ```

### 📊 Understanding Confidence Scores

- **90-100%**: Nearly certain - multiple sources, consistent name/location
- **75-89%**: Very confident - good consistency across results
- **60-74%**: Fairly confident - some consistency  
- **40-59%**: Uncertain - mixed results
- **0-39%**: Very uncertain - little to no consistency

### 🔍 When to Use What

| Scenario | Recommended Flags |
|----------|-------------------|
| Quick lookup | None (basic) |
| Legal case building | `--verbose --dossier person` |
| Business investigation | `--keywords "business name" --dossier business` |
| Skip tracing | `--verbose --keywords "last known name"` |
| Comprehensive report | `--verbose --colorful --delay 3` |

---

## Command Line Reference

### All Flags

```
./telespot.py [OPTIONS] PHONE_NUMBER

Options:
  --setup              Run API configuration wizard
  -v, --verbose        Show complete result listings
  -c, --colorful       Enable colorful display
  -k, --keywords TEXT  Add search keywords
  --delay INT          Delay between searches (default: 2)
  --dossier TYPE       Generate dossier (person|business)
  -d, --debug          Enable debug output
```

### Examples

```bash
# Setup
./telespot.py --setup

# Basic
./telespot.py 5555551212

# Verbose + Colorful
./telespot.py -v -c 5555551212

# With keywords
./telespot.py -k "John Smith" 5555551212

# Full investigation
./telespot.py -v -c -k "Jane Doe" --dossier person 5555551212

# Business lookup with delay
./telespot.py --delay 4 --dossier business -k "Acme Corp" 8005551212
```

---

## Output Files

### Text File Format

```
================================================================================
TELESPOT SEARCH RESULTS
================================================================================

Phone Number: 5555551212
Search Date: 2024-12-28 14:30:22
Confidence Score: 78%

[Summary section]
[Detailed results section]
```

### Naming Convention

**Default:**
```
telespot_[DIGITS]_[YYYYMMDD]_[HHMMSS].txt

Example:
telespot_5555551212_20241228_143022.txt
```

**Custom:**
```
[YOUR_NAME].txt

Example:
john_smith_investigation.txt
```

---

## Troubleshooting

### "Only getting DuckDuckGo results"
- You haven't configured Google/Bing APIs
- Run `./telespot.py --setup` to add API keys
- See API_SETUP_GUIDE.md

### "Low confidence score"
- Phone number might not be well-indexed
- Try adding `--keywords` with known info
- Results exist but are inconsistent

### "No results at all"
- Number might be brand new/unlisted
- Try different keyword combinations
- Check if you can find it manually on Google

### "API quota exceeded"
- You've hit your daily/monthly limit
- DuckDuckGo will still work (free)
- Wait for reset or use other API

---

**Made with ❤️ for OSINT investigations**

For full documentation, see README.md
For API setup, see API_SETUP_GUIDE.md
