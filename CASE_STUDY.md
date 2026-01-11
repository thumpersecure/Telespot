# Building the Telespot Ecosystem

<div align="center">

*A case study on building open-source phone number intelligence tools*

| Repository | Stars | Language |
|:-----------|:-----:|:--------:|
| [Telespot](https://github.com/thumpersecure/Telespot) | [![](https://img.shields.io/github/stars/thumpersecure/Telespot?style=social)](https://github.com/thumpersecure/Telespot/stargazers) | Python |
| [Telespotter](https://github.com/thumpersecure/Telespotter) | [![](https://img.shields.io/github/stars/thumpersecure/Telespotter?style=social)](https://github.com/thumpersecure/Telespotter/stargazers) | Rust |
| [TelespotXX](https://github.com/thumpersecure/TelespotXX) | [![](https://img.shields.io/github/stars/thumpersecure/TelespotXX?style=social)](https://github.com/thumpersecure/TelespotXX/stargazers) | Python/Flask |

</div>

---

## The Problem

Phone numbers are ubiquitous identifiers in modern society. They're linked to social media accounts, business listings, public records, and countless online services. Yet investigating a phone number manually requires:

- Searching multiple engines with different query formats
- Querying people search databases individually
- Correlating results across dozens of pages
- Identifying patterns in unstructured data
- Avoiding detection by anti-bot systems

This process is time-consuming and error-prone. Security researchers, fraud investigators, and OSINT practitioners needed a better approach.

---

## The Solution: Three Tools, One Ecosystem

The Telespot ecosystem provides three complementary tools, each optimized for different use cases:

```
┌─────────────────────────────────────────────────────────────────┐
│                     TELESPOT ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │  Telespot   │   │ Telespotter │   │ TelespotXX  │          │
│   │   Python    │   │    Rust     │   │   Web UI    │          │
│   │    CLI      │   │    CLI      │   │   Flask     │          │
│   │  Original   │   │    Fast     │   │  Unified    │          │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          │
│          │                 │                 │                  │
│          └────────────┬────┴─────────────────┘                  │
│                       ▼                                         │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   DATA SOURCES                           │  │
│   │  ┌──────────────────────┐  ┌──────────────────────────┐ │  │
│   │  │   Search Engines     │  │   People Databases       │ │  │
│   │  │  Google │ Bing │ DDG │  │  Whitepages │ TruePeople │ │  │
│   │  └──────────────────────┘  │  FastPeople │ ThatsThem  │ │  │
│   │                            └──────────────────────────┘ │  │
│   └─────────────────────────────────────────────────────────┘  │
│                       │                                         │
│                       ▼                                         │
│          ┌────────────────────────┐                             │
│          │   Pattern Analysis     │                             │
│          │  Names │ Locations     │                             │
│          │  Emails │ Usernames    │                             │
│          │  Social │ Confidence   │                             │
│          └────────────────────────┘                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tool #1: Telespot (Python CLI)

**The original.** Built for accessibility and comprehensive coverage.

### Key Features

| Feature | Description |
|---------|-------------|
| **4 Search APIs** | Google, Bing, DuckDuckGo, Dehashed |
| **10 Phone Formats** | Dashes, digits, parentheses, international, quoted variants |
| **Pattern Analysis** | Names, locations, usernames with confidence scoring |
| **Anti-Detection** | 11 user-agent profiles, 3-5s random delays |
| **Output Options** | Console, JSON, TXT, summary charts |

### Design Philosophy

Telespot prioritizes **accessibility over speed**. It works without API keys (DuckDuckGo fallback), runs on any system with Python 3.6+, and includes comprehensive rate limiting to avoid blocks.

```bash
# Zero-config usage
./telespot.py 8885551212

# Full power with APIs
./telespot.py 8885551212 --verbose --output results.json
```

### Technical Stats

- **Lines of code**: ~1,250
- **Dependencies**: Just `requests`
- **Execution time**: ~60 seconds (rate-limited)
- **International support**: Yes (any country code)

---

## Tool #2: Telespotter (Rust CLI)

**The fast one.** A ground-up rewrite optimized for performance.

### Performance Gains

| Metric | Telespot (Python) | Telespotter (Rust) | Improvement |
|--------|-------------------|-------------------|-------------|
| Execution time | ~60s | ~17s | **3.6x faster** |
| Memory usage | ~50MB | ~8MB | **6x less** |
| Startup time | 800ms | 2ms | **400x faster** |

### Additional Capabilities

Telespotter goes beyond the original with:

- **People search databases**: Whitepages, TruePeopleSearch, FastPeopleSearch, ThatsThem, USPhoneBook
- **OSINT tool chaining**: Automatically runs Sherlock (usernames), Blackbird (emails), email2phonenumber on discovered data
- **15 user-agent profiles** with exponential backoff
- **Parallel request execution**

### When to Use

Choose Telespotter when:
- Speed is critical (bulk operations, time-sensitive investigations)
- Memory is constrained (embedded systems, containers)
- You need people database integration
- You want automatic OSINT tool chaining

```bash
# Fast parallel execution
./telespotter 8885551212

# Chain with external tools
./telespotter 8885551212 --chain-osint
```

---

## Tool #3: TelespotXX (Web UI)

**The unified interface.** All tools, one browser tab.

### Features

- **Real-time streaming**: WebSocket-powered live results
- **Multi-source aggregation**: Search engines + people databases simultaneously
- **Pattern analysis dashboard**: Visual confidence scoring
- **Export formats**: JSON, CSV, TXT
- **Dark theme**: Easy on the eyes during long investigations
- **Responsive design**: Works on desktop and mobile

### Technical Stack

```
Frontend:  Tailwind CSS, Socket.IO client
Backend:   Python 3.11+, Flask 3.0, Socket.IO
Deploy:    Docker containerization support
```

### When to Use

Choose TelespotXX when:
- You prefer a graphical interface
- You're collaborating with non-technical team members
- You want to see results stream in real-time
- You need quick export to multiple formats

---

## Choosing the Right Tool

| Use Case | Recommended Tool |
|----------|------------------|
| Quick single lookup | Telespot |
| Bulk investigations | Telespotter |
| Maximum speed | Telespotter |
| International numbers | Telespot |
| Team collaboration | TelespotXX |
| Non-technical users | TelespotXX |
| Automated pipelines | Telespotter |
| Low memory environments | Telespotter |

---

## Architecture Decisions

### Why Three Tools?

Each tool serves a distinct audience:

1. **Telespot**: Security researchers who want something that "just works" with minimal setup
2. **Telespotter**: Power users who need speed and don't mind compiling Rust
3. **TelespotXX**: Teams and non-CLI users who prefer visual interfaces

### Single-File Distribution (Telespot)

The original Telespot is distributed as a standalone script rather than a pip package:

- **Portability**: Clone and run immediately
- **Transparency**: All code visible in one file
- **Modification**: Easy to fork and customize
- **No dependency hell**: Just `requests`

### Rust Rewrite (Telespotter)

Rewriting in Rust wasn't about hype—it solved real problems:

- **Memory safety**: No runtime panics from null pointers
- **Concurrency**: Fearless parallelism for simultaneous requests
- **Startup time**: 2ms cold start vs 800ms Python interpreter
- **Binary distribution**: Single executable, no runtime needed

### Web Interface (TelespotXX)

Adding a web UI expanded the user base:

- **Accessibility**: No command line knowledge required
- **Visualization**: Pattern analysis is easier to understand visually
- **Sharing**: Results can be viewed collaboratively
- **Deployment**: Docker makes it easy to host internally

---

## Pattern Recognition

All three tools share a common pattern recognition engine that extracts:

### Names
- 2-3 word capitalized phrases
- Filtered for common false positives
- Frequency-weighted confidence scoring

### Locations
- All 50 US states + territories
- City/state combinations
- International when country code provided

### Contact Information
- Email addresses (validated format)
- Social media profile URLs
- Associated phone numbers

### Confidence Scoring

```
🎯 Confidence Score: HIGH (78%)

👤 Names Found:
   • John Smith: 12x ⭐ (high confidence)
   • Jane Doe: 3x

📍 Locations:
   • Philadelphia, PA: 15x ⭐
   • PA: 10x

🔗 Usernames:
   • @johnsmith: 3x ⭐
```

Results are weighted by:
- Occurrence frequency across sources
- Source reliability (search engines vs. people databases)
- Context (exact match vs. partial)

---

## Security & Privacy

### Privacy-Conscious Defaults

- Config files stored with `600` permissions
- No telemetry or usage tracking
- No cloud dependencies
- All processing happens locally (CLI tools)

### Rate Limiting

Aggressive rate limiting protects both users and targets:

- **Telespot**: 3-5s random delays between requests
- **Telespotter**: Configurable with exponential backoff
- **TelespotXX**: Server-side throttling

### Responsible Use

These tools are designed for legitimate OSINT:
- Security research
- Fraud investigation
- Identity verification
- Skip tracing (with proper authorization)

---

## Community & Contribution

The ecosystem is actively maintained with:

- Regular updates addressing API changes
- Community-contributed improvements
- Responsive issue tracking
- MIT license for maximum flexibility

### Contributing

Areas of interest:
- Additional search engine integrations
- Improved pattern recognition algorithms
- International format support expansion
- Performance optimizations
- New export formats

---

## Getting Started

### Telespot (Python)
```bash
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot && pip install -r requirements.txt
./telespot.py --setup
./telespot.py 8885551212
```

### Telespotter (Rust)
```bash
git clone https://github.com/thumpersecure/Telespotter.git
cd Telespotter && cargo build --release
./target/release/telespotter 8885551212
```

### TelespotXX (Web)
```bash
git clone https://github.com/thumpersecure/TelespotXX.git
cd TelespotXX && docker-compose up
# Open http://localhost:5000
```

---

<div align="center">

**Built for the OSINT community by [@thumpersecure](https://github.com/thumpersecure)**

[Telespot](https://github.com/thumpersecure/Telespot) | [Telespotter](https://github.com/thumpersecure/Telespotter) | [TelespotXX](https://github.com/thumpersecure/TelespotXX)

</div>
