# Telespot: Building an Effective Phone Number OSINT Tool

<div align="center">


*A case study on building open-source intelligence tools*

</div>

---

## The Problem

Phone numbers are ubiquitous identifiers in modern society. They're linked to social media accounts, business listings, public records, and countless online services. Yet investigating a phone number manually requires:

- Searching multiple engines with different query formats
- Correlating results across dozens of pages
- Identifying patterns in unstructured data
- Avoiding detection by anti-bot systems

This process is time-consuming and error-prone. Security researchers, fraud investigators, and OSINT practitioners needed a better approach.

---

## The Solution: Telespot

Telespot automates phone number reconnaissance by:

### 1. Multi-Format Search Generation

Phone numbers appear in many formats online. A single US number can be written as:
- `8885551212` (digits only)
- `888-555-1212` (dashed)
- `(888) 555-1212` (parentheses)
- `+1 888 555 1212` (international)
- `"888-555-1212"` (quoted for exact match)

Telespot generates **10 format variations** automatically, ensuring comprehensive coverage across how numbers actually appear in the wild.

### 2. Multi-Engine Aggregation

Different search engines index different content. Telespot queries:

| Engine | Strength | Coverage |
|--------|----------|----------|
| Google | Deepest index, exact phrase matching | Global |
| Bing | Different results than Google | Global |
| DuckDuckGo | Privacy-focused sites, no API key needed | Global |
| Dehashed | Breach databases (optional) | Historical |

### 3. Pattern Recognition & Confidence Scoring

Raw search results are noise. Telespot extracts signal by:

- **Name extraction**: Identifies potential owner names from result snippets
- **Location correlation**: Maps geographic patterns with frequency tracking
- **Username discovery**: Finds associated handles and usernames
- **Confidence scoring**: Weights findings by occurrence frequency

```
🎯 Confidence Score: HIGH (78%)

👤 Names Found:
   • John Smith: 12x ⭐
   • Jane Doe: 3x

📍 Locations:
   • Philadelphia, PA: 15x ⭐
```

### 4. Anti-Detection Measures

Web scraping without protection gets blocked. Telespot implements:

- **User-Agent rotation**: 11 browser profiles cycled randomly
- **Rate limiting**: 3-5 second random delays between requests
- **Request spacing**: Prevents API quota exhaustion

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INPUT                                │
│              Phone Number + Country Code                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  FORMAT GENERATOR                           │
│         Produces 10 search-optimized variations             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   SEARCH ENGINE LAYER                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Google  │ │   Bing   │ │   DDG    │ │ Dehashed │       │
│  │   API    │ │   API    │ │  Scrape  │ │   API    │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  PATTERN ANALYZER                           │
│     Name Extraction │ Location Mapping │ Username Match     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      OUTPUT                                 │
│         Console │ JSON │ TXT │ Summary Charts               │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance: Standard vs Fast Mode

Telespot offers two execution modes:

| Metric | telespot.py | telespotx.py |
|--------|-------------|--------------|
| **Execution time** | ~60 seconds | ~5 seconds |
| **Request pattern** | Sequential with delays | Parallel async |
| **Rate limit safe** | Yes | No |
| **Format variations** | 10 | 6 |
| **International** | Yes | US only |
| **Best for** | Stealth, comprehensive | Speed, bulk |

The fast mode (`telespotx.py`) uses `httpx` with async/await for 12x faster execution when stealth isn't required.

---

## Key Design Decisions

### Single-File Distribution

Telespot is distributed as standalone Python scripts rather than a pip package. This decision prioritizes:

- **Portability**: Clone and run immediately
- **Transparency**: All code visible in one file (~1,250 lines)
- **Modification**: Easy to fork and customize
- **No dependency hell**: Just `requests` (or `httpx` for fast mode)

### API-First with Fallback

The tool works best with API keys but remains functional without them:

```bash
# Full power (with APIs configured)
./telespot.py 8885551212  # Uses Google + Bing + DDG

# Zero config (DuckDuckGo only)
./telespot.py 8885551212  # Still works, fewer results
```

### Privacy-Conscious Defaults

- Config file stored with `600` permissions (owner-only)
- No telemetry or usage tracking
- No cloud dependencies
- All processing happens locally

---

## Use Cases

### Security Research
Investigate phone numbers associated with phishing campaigns or fraud operations.

### OSINT Investigations
Gather intelligence on subjects using phone numbers as pivot points.

### Identity Verification
Cross-reference provided phone numbers against public records.

### Competitive Intelligence
Research business phone numbers for market analysis.

---

## Community & Development

Telespot is actively maintained with:

- Regular updates addressing API changes
- Community-contributed improvements
- Responsive issue tracking
- MIT license for maximum flexibility

### Contributing

Contributions welcome! Areas of interest:
- Additional search engine integrations
- Improved pattern recognition algorithms
- International format support expansion
- Performance optimizations

---

## Getting Started

```bash
git clone https://github.com/thumpersecure/Telespot.git
cd Telespot
pip install -r requirements.txt
./telespot.py --setup
./telespot.py 8885551212
```

See the [main README](README.md) for complete documentation.

---

<div align="center">

**Built for the OSINT community by [@thumpersecure](https://github.com/thumpersecure)**

[View on GitHub](https://github.com/thumpersecure/Telespot) | [Report Issues](https://github.com/thumpersecure/Telespot/issues) | [MIT License](LICENSE)

</div>
