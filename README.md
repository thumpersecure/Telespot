<div align="center">

<!-- Social preview -->
<img src="og-preview.png" alt="TeleSpot — Phone Number OSINT in Python" width="100%" />

# 📞 telespot

```
  _       *      _                     _   *
 | |_ ___| | ___  ___ _ __   ___ | |_
 | __/ _ \ |/ _ \/ __| '_ \ / _ \| __|*
 | ||  __/ |  __/\__ \ |_) | (_) | |_
  \__\___|_|\___||___/ .__/ \___/ \__|
*                    |_|    *   v6.0.0
```

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=00D9FF&center=true&vCenter=true&width=435&lines=Phone+Number+OSINT+Tool;Search+Google%2C+Brave%2C+DuckDuckGo;Pattern+Analysis+%26+Confidence+Scoring;Find+Names%2C+Locations%2C+Usernames)](https://github.com/thumpersecure/Telespot)

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/thumpersecure/Telespot?style=for-the-badge&logo=github)](https://github.com/thumpersecure/Telespot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/thumpersecure/Telespot?style=for-the-badge&logo=github)](https://github.com/thumpersecure/Telespot/network)

**Telespot** is a Python OSINT tool that investigates phone numbers across multiple search engines. It searches each number in **10 format variations**, runs every engine **in parallel**, and correlates results to surface **names**, **locations**, **usernames** and **emails**.

[Getting Started](#-quick-start) •
[Features](#-features) •
[Speed Modes](#-speed-modes) •
[Usage](#-usage) •
[API Setup](#-api-setup) •
[Case Study](CASE_STUDY.md) •
[Changelog](CHANGELOG.md)

</div>

---

## 🚀 Quick Start

Get up and running in under 2 minutes:

```bash
# 1️⃣ Clone the repository
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot

# 2️⃣ Set up virtual environment (recommended)
python3 -m venv telvenv
source telvenv/bin/activate

# 3️⃣ Install dependencies (httpx, brotli)
pip install -r requirements.txt

# 4️⃣ Configure your API keys
./telespot.py --setup

# 5️⃣ Run your first search!
./telespot.py 8885551212
```

> 💡 **Tip:** No API keys? No problem! DuckDuckGo works without any setup.
> DuckDuckGo does, however, sometimes answer scripted clients with a bot challenge. A free Google or Brave key gives reliable results.

---

## 🆕 What's New in 6.0.0

**One tool.** The sequential `telespot.py` and the parallel `telespotx.py` are merged into a single async engine built on httpx. Every search engine is queried concurrently for each format, several formats are searched at once, and each engine sits behind its own **rate gate** so parallelism never exceeds what that engine tolerates. `telespotx.py` remains as a shim that runs `telespot.py --mode fast`.

| Change | Detail |
|--------|--------|
| ⚡ **Three speed modes** | `--fast`, `--mode balanced` (default) and `--safe`. See [Speed Modes](#-speed-modes). |
| 🚦 **Per-engine rate gates** | Brave's free tier allows 1 query/second, so Brave is paced at that rate even in fast mode. DuckDuckGo's web search is the only engine that challenges bursts, so only it is throttled by mode. Gates widen automatically when an engine rate-limits or challenges, and relax on success. |
| 🌍 **International in every mode** | Fast mode used to be US-only. All 10 formats and `-c` country codes work in every mode. |
| 📧 **Emails** | Email extraction from telespotx is now in the main analysis, summary chart and JSON/TXT export. |
| 🧾 **Run metadata** | Mode, elapsed time, rate-limit events and DuckDuckGo challenges are printed and saved with the results. |
| ⚙️ **Default mode in config** | `--setup` asks for a default mode (`default_mode=` in `~/.telespot_config`). |

The 5.2.0 fixes (DuckDuckGo HTTP 202 handling, brotli, false captcha hits, API error reporting, credential-preserving retries, real counts) are all carried forward. See [CHANGELOG.md](CHANGELOG.md).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **4 Search APIs** | Google, Brave, DuckDuckGo, and Dehashed (optional) |
| 📱 **10 Phone Formats** | Dashes, digits, parentheses, international, quoted variants |
| ⚡ **Parallel Engine** | All engines per format at once; formats in parallel by mode; per-engine rate gates |
| 🧠 **Pattern Analysis** | Extracts names, locations, usernames and emails with confidence scoring |
| 🛡️ **Anti-Detection** | User-agent rotation (13 profiles), adaptive spacing, accurate bot-challenge detection |
| 🎨 **Output Options** | Verbose, colorful rainbow mode, JSON/TXT export, summary charts |
| 🌍 **International** | Support for country codes worldwide, in every mode |

---

## ⚡ Speed Modes

Every mode calls all configured engines concurrently for each format. The modes differ in how many formats are in flight and how DuckDuckGo's web search is paced.

| Mode | Formats at once | DuckDuckGo web search | Typical time | Use when |
|------|:---:|---|:---:|---|
| `--fast` | 10 | 3-wide, light jitter | ~5-15s | You have Google/Brave keys or want a quick first look |
| `--mode balanced` (default) | 4 | 2-wide, 1-2.5s jitter | ~15-30s | Everyday use, keys or not |
| `--safe` | 1 | 1-wide, 2.5-4.5s jitter, adaptive delay between formats | ~60s | DuckDuckGo is challenging you, or you are on a shared IP |

```bash
./telespot.py 8885551212 --fast       # everything at once
./telespot.py 8885551212              # balanced (default)
./telespot.py 8885551212 --safe       # classic one-at-a-time behaviour
./telespot.py 8885551212 --workers 2  # override how many formats run concurrently
```

Brave is always paced at one query per second (its free-tier limit), Google and Dehashed are lightly spaced, and any engine that rate-limits or challenges gets its own spacing widened without slowing the others. If DuckDuckGo challenges three formats in a row, its web search is skipped for the rest of the run and you are told so.

---

## 📖 Usage

### Basic Commands

```bash
./telespot.py 8885551212              # 🔍 Basic search (balanced mode)
./telespot.py 8885551212 --fast       # ⚡ Fast mode
./telespot.py 8885551212 -v           # 📝 Verbose output with URLs
./telespot.py 8885551212 --colorful   # 🌈 Rainbow color mode
./telespot.py 8885551212 -k "name"    # 🔑 Add keyword filter
./telespot.py 8885551212 -s site.com  # 🌐 Search specific site
./telespot.py 8885551212 --dehashed   # 🔓 Include breach database
./telespot.py 8885551212 -o out.json  # 💾 Save to JSON
./telespot.py +442071234567 -c +44    # 🇬🇧 International number
```

### Configuration Commands

```bash
./telespot.py --setup                 # ⚙️ Configure API keys and default mode
./telespot.py --api-status            # 📊 Check API configuration
./telespot.py --update                # 🔄 Update from GitHub
./telespot.py --help                  # ❓ Show help
```

---

## 🎛️ Options Reference

```
🔍 SEARCH OPTIONS
   -k, --keyword    Add search keyword (e.g., "owner", "business")
   -s, --site       Limit to specific site (e.g., whitepages.com)
   -c, --country    Country code (default: +1)
   --dehashed       Include Dehashed breach database

⚡ SPEED OPTIONS
   --mode MODE      fast, balanced or safe (default: balanced)
   --fast           Shortcut for --mode fast
   --safe           Shortcut for --mode safe
   --workers N      Formats searched concurrently (overrides the mode)

📤 OUTPUT OPTIONS
   -v, --verbose    Show detailed results with URLs
   -o, --output     Save to file (.json or .txt)
   --summary        Show pattern comparison chart
   --dtmf           Show DTMF tone representation

🎨 DISPLAY OPTIONS
   --colorful       Enable rainbow color mode
   --no-color       Disable all colors

⚙️ CONFIGURATION
   --setup          Interactive API key setup wizard
   --api-status     Show current API configuration
   --update         Update Telespot from GitHub
   -d, --debug      Enable debug output
```

---

## 🔑 API Setup

### Quick Setup

Run the interactive setup wizard:

```bash
./telespot.py --setup
```

### API Free Tiers

| API | Free Tier | Signup |
|-----|-----------|--------|
| 🔵 **Google Custom Search** | 100 searches/day | [Get Key](https://developers.google.com/custom-search/v1/introduction) |
| 🟢 **Brave Search** | ~2,000 searches/month, 1 query/second | [Get Key](https://api.search.brave.com/) |
| 🟠 **DuckDuckGo** | ♾️ Unlimited | No key needed! |
| 🔴 **Dehashed** | Paid | [Sign Up](https://dehashed.com/) |

> 📘 **Need detailed instructions?** See [GUIDE_APIS.md](GUIDE_APIS.md) for step-by-step API setup.

---

## 📁 Config File

Your API keys are securely stored in `~/.telespot_config`:

```ini
# 🔵 Google Custom Search API
google_api_key=YOUR_GOOGLE_API_KEY
google_cse_id=YOUR_CUSTOM_SEARCH_ENGINE_ID

# 🟢 Brave Search API
brave_api_key=YOUR_BRAVE_API_KEY

# 🔴 Dehashed API (optional)
dehashed_api_key=YOUR_DEHASHED_V2_API_KEY

# ⚙️ Settings
default_country_code=+1
delay_seconds=2          # base delay between formats in safe mode
default_mode=balanced    # fast, balanced or safe
```

> 🔒 **Security:** Config file permissions are set to `600` (owner read/write only).

---

## 🎯 Example Output

```
📞 Searching for: 8885551212
🌍 Country code: +1
📊 Using 10 format variations
Mode: balanced - 4 formats at once; DuckDuckGo web search 2-wide, jittered (default)

[2/10] 8885551212           Google 8 · Brave 10 · DuckDuckGo 10  → 28 results (2.3s)
[1/10] 888-555-1212         Google 9 · Brave 10 · DuckDuckGo 10  → 29 results (3.1s)
[3/10] (888) 555-1212       Google 7 · Brave 10 · DuckDuckGo 0   → 17 results (3.4s)
...

Total Results: 96 (41 duplicates removed)  in 17.8s, mode=balanced

══════════════════════════════════════════
📊 PATTERN ANALYSIS SUMMARY
══════════════════════════════════════════

🎯 Confidence Score: HIGH (78%)

👤 Names Found:
   • John Smith: 12x ⭐
   • Jane Doe: 3x

📍 Locations:
   • Philadelphia, PA: 15x ⭐
   • PA: 10x

🔗 Usernames:
   • @johnsmith: 3x ⭐

📧 Emails:
   • john@example.com: 2x ⭐
══════════════════════════════════════════
```

---

## 🛠️ Troubleshooting

<details>
<summary>❌ No results found</summary>

1. Check API status: `./telespot.py --api-status`
2. Verify API keys are valid (a bad Google key prints Google's own error message)
3. Try with `--debug` to see API responses
4. DuckDuckGo Instant Answers only works for well-known topics
5. Make sure `brotli` is installed (`pip install -r requirements.txt`)

</details>

<details>
<summary>🦆 "DuckDuckGo answered with a bot challenge"</summary>

DuckDuckGo serves a picture challenge (HTTP 202) to clients it does not trust, especially from
cloud, VPN or shared IP addresses. The challenge is intermittent, so Telespot retries each format
once, reports the challenge once, and after three challenged formats in a row skips DuckDuckGo's
web search for the rest of the run.

- Re-run with `--safe`, which spaces DuckDuckGo requests out much more
- Wait a while or switch networks and try again
- Configure a free Google or Brave key, which are not affected

</details>

<details>
<summary>⚠️ API quota exceeded</summary>

- **Google:** 100/day, resets at midnight UTC
- **Brave:** ~2,000/month, resets monthly; 1 query/second (telespot paces this automatically)
- **DuckDuckGo:** No limits (but limited result types)

</details>

<details>
<summary>🔌 Connection errors</summary>

- Check your internet connection
- Use `--debug` to see detailed error messages
- Some APIs may be temporarily unavailable
- `telespot requires httpx`: run `pip install -r requirements.txt`

</details>

<details>
<summary>🐢 I liked telespotx.py</summary>

It is still there. `./telespotx.py 8885551212` runs `telespot.py --mode fast` with the same
arguments, now with international numbers, all 10 formats and per-engine pacing.

</details>

---

## 👏 Credits

Created with ❤️ by:

- **Spin** ([@thumpersecure](https://github.com/thumpersecure))
- User-Agent rotation concept from [@kaifcodec](https://github.com/kaifcodec)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

⚠️ **Disclaimer:** This tool is intended for **legitimate OSINT purposes only**. Users are responsible for ensuring their use complies with all applicable laws and regulations.

**Made with 🔍 for the OSINT community**

</div>
