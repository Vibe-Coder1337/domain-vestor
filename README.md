# Domain Vestor v1.0

> **Multi-TLD domain availability checker for investors & founders** — Check domains across `.ai`, `.com`, `.io`, `.dev`, `.app` and 10+ more extensions simultaneously using WHOIS/RDAP + DNS + HTTP signals. Matrix dashboard in your terminal.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Why Domain Vestor?

Domain registrar websites like GoDaddy, Namecheap, and BigRock **block automated lookups** (CORS, robots.txt, CAPTCHAs). Domain Vestor bypasses that by querying the **same underlying protocols** registrars use internally:

| Method | Web Scraping | Domain Vestor |
|--------|-------------|---------------|
| **Approach** | Scrape registrar HTML | Query WHOIS/RDAP/DNS directly |
| **CORS/robots.txt** | Blocked | Not applicable (CLI) |
| **Reliability** | Breaks when site changes | Stable protocol-level queries |
| **Speed** | Slow (renders full page) | Fast (data-only responses) |
| **Multi-TLD** | Check one at a time | Matrix view across 15 TLDs |

## Features

- **Multi-TLD Matrix** — Check a domain name across up to 15 extensions in one run
- **4-Signal Verification** — RDAP + WHOIS + DNS + HTTP checks combined with confidence scoring
- **6 TLD Presets** — `--popular`, `--all`, `--cheap`, `--premium`, `--india`, or pick your own with `--tlds`
- **15 TLDs Supported** — `.ai`, `.com`, `.io`, `.dev`, `.app`, `.co`, `.tech`, `.xyz`, `.net`, `.org`, `.in`, `.co.in`, `.info`, `.online`, `.store`
- **Rich Dashboard** — Color-coded matrix table in your terminal
- **Export** — CSV (for Excel/Google Sheets) and JSON output
- **Browser Integration** — `--open` flag opens available domains directly on GoDaddy for purchase
- **Batch Processing** — Load hundreds of domain names from a text file
- **Pricing Reference** — Built-in INR/USD price estimates per TLD

## Quick Start

### 1. Install Dependencies

```bash
pip install rich requests python-whois dnspython
```

### 2. Run It

```bash
# Interactive mode
python domain_vestor.py

# Check specific domains (default TLDs: .ai .com .io .dev)
python domain_vestor.py promptcraft synthiq vectrix

# Check from file
python domain_vestor.py --file domains_v3.txt

# Check ALL 15 TLDs
python domain_vestor.py --file domains_v3.txt --all

# Export + open in browser for purchase
python domain_vestor.py --file domains_v3.txt --popular --csv --open
```

## Usage

### Command Line Arguments

```
positional arguments:
  domains               Base domain names (without TLD)

options:
  -f, --file FILE       Load domain names from file (one per line)
  -t, --tlds TLD [...]  Specific TLDs to check (e.g., --tlds ai com io)
  --all                 Check all 15 supported TLDs
  --popular             Check popular 7 TLDs (ai, com, io, dev, app, co, tech)
  --cheap               Check budget TLDs (com, xyz, in, co.in, net, info, online)
  --premium             Check premium TLDs (ai, io, dev, app, co)
  --india               Check India-relevant TLDs (com, in, co.in, ai, io)
  --csv                 Export results to domain_results.csv
  --json                Export results to domain_results.json
  -o, --open            Open available domains on GoDaddy in browser
  -v, --verbose         Show detailed per-check breakdown
  --no-dashboard        Minimal output for scripting/piping
```

### TLD Presets

| Preset | TLDs | Best For |
|--------|------|----------|
| `(default)` | ai, com, io, dev | Quick check |
| `--popular` | ai, com, io, dev, app, co, tech | Comprehensive startup check |
| `--all` | All 15 TLDs | Maximum coverage |
| `--cheap` | com, xyz, in, co.in, net, info, online | Budget domain hunting |
| `--premium` | ai, io, dev, app, co | Premium/tech domains only |
| `--india` | com, in, co.in, ai, io | Indian market focus |

### Input File Format

```
# My domain watchlist
promptcraft
synthiq
vectrix
mindforge
ragpipe
llmguard
```

The tool auto-strips any TLD you include — `promptcraft.ai` becomes `promptcraft` and gets checked across all selected TLDs.

## How It Works

Domain Vestor runs **4 independent checks** for each domain:

| Check | Protocol | What It Does | Weight |
|-------|----------|--------------|--------|
| **RDAP** | RDAP over HTTPS | Queries the authoritative domain registry | 3x (highest) |
| **WHOIS** | WHOIS (port 43) | Queries traditional WHOIS database | 2x |
| **DNS** | DNS (A + NS records) | Checks if domain resolves in DNS | 2x |
| **HTTP** | HTTP/HTTPS | Attempts to load the website | 1x |

Signals are combined into a **weighted verdict**:

- **AVAILABLE** (60-95% confidence) — No registration found
- **TAKEN** (60-99% confidence) — Registration confirmed, shows registrar
- **UNCERTAIN** (50%) — Mixed signals, verify manually
- **UNKNOWN** (0%) — All checks failed (timeout/network)

### Accuracy Note

> WHOIS/RDAP can miss **parked domains** (registered but no DNS/website). Domain Vestor catches ~85-90% of taken domains. **Always verify "AVAILABLE" results on the registrar before purchasing.** The `--open` flag makes this one-click.

## Output Example

```
+----------------------------------------------------------+
|                  Availability Matrix                      |
+--------------+------+------+------+------+---------------+
| Domain       | .ai  | .com | .io  | .dev | Best Pick     |
+--------------+------+------+------+------+---------------+
| synthiq      | FREE | FREE | FREE | FREE | .ai           |
| promptcraft  | TAKEN| TAKEN| FREE | FREE | .io           |
| vectrix      | FREE | TAKEN| TAKEN| FREE | .ai           |
+--------------+------+------+------+------+---------------+
```

## Supported TLDs & Pricing

| TLD | Price (INR/yr) | Min Period | Category | Best For |
|-----|---------------|------------|----------|----------|
| `.ai` | ~6,000-8,000 | 2 years | Premium | AI/ML startups, highest flip value |
| `.com` | ~800-1,200 | 1 year | Standard | Universal, safest long-term hold |
| `.io` | ~2,500-4,000 | 1 year | Premium | Tech startups, developer tools |
| `.dev` | ~1,000-1,500 | 1 year | Mid | Developer products, open source |
| `.app` | ~1,200-1,800 | 1 year | Mid | Mobile/web applications |
| `.co` | ~800-2,500 | 1 year | Mid | Startups, .com alternative |
| `.tech` | ~800-3,000 | 1 year | Mid | Technology companies |
| `.xyz` | ~200-800 | 1 year | Budget | Cheap experiments |
| `.net` | ~800-1,200 | 1 year | Standard | Networks, infrastructure |
| `.org` | ~800-1,200 | 1 year | Standard | Non-profits, open source |
| `.in` | ~500-800 | 1 year | Budget | Indian businesses (local SEO) |
| `.co.in` | ~300-600 | 1 year | Budget | India (cheapest) |
| `.info` | ~300-900 | 1 year | Budget | Informational sites |
| `.online` | ~200-1,500 | 1 year | Budget | Budget web presence |
| `.store` | ~200-4,000 | 1 year | Budget | E-commerce |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | `pip install rich requests python-whois dnspython` |
| `UnicodeDecodeError` | Already handled — reads files as UTF-8 |
| All results UNKNOWN | Check internet connection |
| WHOIS timeouts | Normal. RDAP + DNS still provide verdict. |
| False "AVAILABLE" | Domain may be parked. **Verify on registrar.** |
| Slow on `--all` | Use `--popular` to reduce scope |

## Requirements

- **Python** 3.8+
- **OS:** Windows, macOS, Linux
- **Packages:** `rich`, `requests`, `python-whois`, `dnspython`

## Project Structure

```
domain-vestor/
├── domain_vestor.py       # Main CLI tool
├── domains_v3.txt         # Sample domain watchlist (95 names)
├── README.md              # This file
├── CHANGELOG.md           # Version history
├── LICENSE                # MIT License
└── .gitignore             # Git ignore rules
```

## Contributing

Ideas for future versions: parallel/async checking, web UI dashboard, price comparison across registrars, expiring domain alerts, registrar API integration, more TLDs.

## Disclaimer

This tool queries publicly available WHOIS/RDAP/DNS data using standard internet protocols. Results are estimates — always verify on a registrar before purchasing. Domain investing is speculative and carries risk.

## License

[MIT License](LICENSE)

---

**Built with Claude AI** | If this saved you time, give it a star!
