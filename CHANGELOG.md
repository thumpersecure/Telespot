# Changelog

## V6.0.0 — one tool, three speeds

`telespot.py` (sequential, requests) and `telespotx.py` (parallel, httpx) are merged into a
single async engine. `telespotx.py` remains as a shim that runs `telespot.py --mode fast`.
`requests` is no longer used; `httpx` and `brotli` are the dependencies.

### Parallel engine with per-engine rate gates
- Every configured engine (Google, Brave, DuckDuckGo, Dehashed) is queried concurrently for each
  format, and several formats are searched at once.
- Each engine sits behind its own rate gate. Brave is paced at 1 query/second (its free-tier
  limit) in every mode; Google and Dehashed are lightly spaced; DuckDuckGo's web search, the only
  engine that challenges bursts, is the one throttled by mode. A gate widens automatically when
  its engine rate-limits or challenges and relaxes on success, so one engine's trouble never slows
  the others.

### Speed modes
- `--fast`: all 10 formats at once, DuckDuckGo web search 3-wide.
- `--mode balanced` (default): 4 formats at once, DuckDuckGo 2-wide with 1-2.5s jitter.
- `--safe`: one format at a time with the classic adaptive delay between formats.
- `--workers N` overrides the number of concurrent formats; `default_mode=` in the config file
  (set by `--setup`) picks the default.

### Everything works in every mode
- Fast mode used to be US-only with 6 formats; all 10 formats and `-c` country codes now work in
  every mode.
- Email extraction (previously telespotx-only) is part of the main analysis, summary chart and
  JSON/TXT export.
- Run metadata (mode, elapsed time, rate-limit events, DuckDuckGo challenges) is printed and
  saved with the results.
- Per-format progress lines show each engine's count and the elapsed time.

### Carried forward from 5.2.0
- DuckDuckGo HTTP 202 handling and challenge detection, brotli-aware `Accept-Encoding`, accurate
  captcha detection, provider error messages, credential-preserving retries, real occurrence
  counts, international formats.

## V5.2.0 — telespot 5.2.0 / telespotx 0.4.0

A bug-fix release for everything that made searches come back empty or misleading.
Install with `pip install -r requirements.txt` (adds `brotli`).

### DuckDuckGo works again
- The Instant Answer API now answers with **HTTP 202** and a full JSON body. The tool only
  accepted 200, so instant answers were always thrown away. Any 2xx is accepted.
- DuckDuckGo's lite web search serves an **HTTP 202 "bots use DuckDuckGo too" challenge** to
  clients it does not trust. It was never detected, so it produced a silent 0. It is now detected
  and reported once; each format is retried once (the challenge is intermittent), and after three
  challenged formats in a row the web fallback is skipped for the rest of the run.
- DuckDuckGo's own "no results" page is no longer reported as stale selectors.

### Compressed replies are decoded
- Requests advertised `Accept-Encoding: … br` while no brotli decoder was installed, so servers
  sent bodies `requests`/`httpx` handed back as raw compressed bytes and every scraper regex
  matched nothing. `br` is now advertised only when `brotli` is importable, and `brotli` is in
  `requirements.txt`.

### No more false captcha hits
- Generic words such as *blocked*, *forbidden*, *access denied*, *please verify* and
  *security check* appear in ordinary spam-call listings and used to trigger the captcha
  detector, which backed off for seconds and then discarded the real results. Detection now keys
  on real challenge markers only and scans just the first 24 KB of a page.

### API errors are shown instead of hidden
- A 403 from Google (invalid key, API not enabled, quota) was treated as a captcha and retried
  with 15+ seconds of backoff per format under a misleading "blocked/rate limited" notice. JSON
  API 403s are now reported, not retried, and Google, Brave and Dehashed print the provider's
  message (e.g. `Google API error 403: API key not valid`).

### Retries keep credentials
- Retries regenerated headers and dropped the Brave subscription token and Dehashed API key in
  both scripts, turning every retry into a 401. Fingerprint headers are now merged under the
  caller's headers on every attempt, and API-mode headers persist across retries.

### Counts and confidence are real
- Locations, usernames and emails were de-duplicated before counting, so every count was 1 and
  the ⭐ indicators and location consistency in the confidence score never fired.

### International numbers
- Non-US numbers were searched as `+1…`. The `-c` country code is now used, and a country code
  typed into the number itself is not doubled.

### Docs
- README: 5.2.0, "What's New" table, DuckDuckGo challenge troubleshooting.
- GUIDE_APIS: Google 403 messages, DuckDuckGo fallback notes.

**Full Changelog**: https://github.com/thumpersecure/Telespot/compare/V5.1...V5.2.0

## V5.1

- Brave Search replaces the retired Bing Search API.
- Dehashed migrated to the v2 API.
- Captcha detection, retry logic, adaptive rate limiting, DuckDuckGo HTML fallback.
- Shared `telespot_common` package for both entrypoints.
