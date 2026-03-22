# 🔍 Domain Availability Checker v3.0

> **Multi-TLD domain availability checker** — Check domains across `.ai`, `.com`, `.io`, `.dev`, `.app` and 10+ more extensions simultaneously using WHOIS/RDAP + DNS + HTTP signals. Built for domain investors and startup founders.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Why This Tool?

Domain registrar websites like GoDaddy, Namecheap, and BigRock **block automated lookups** (CORS, robots.txt, CAPTCHAs). This tool bypasses that limitation entirely by querying the **same underlying protocols** these registrars use internally:

| Method | Web Scraping | This Tool |
|--------|-------------|-----------|
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
# Interactive mode — type domain names manually
python domain_checker.py

# Check specific domains (default TLDs: .ai .com .io .dev)
python domain_checker.py promptcraft synthiq vectrix

# Check from file
python domain_checker.py --file domains.txt

# Check ALL 15 TLDs
python domain_checker.py --file domains.txt --all

# Export results + open available domains in browser
python domain_checker.py --file domains.txt --popular --csv --open
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
| `--default` | ai, com, io, dev | Quick check (default if nothing specified) |
| `--popular` | ai, com, io, dev, app, co, tech | Comprehensive startup check |
| `--all` | All 15 TLDs | Maximum coverage |
| `--cheap` | com, xyz, in, co.in, net, info, online | Budget domain hunting |
| `--premium` | ai, io, dev, app, co | Premium/tech domains only |
| `--india` | com, in, co.in, ai, io | Indian market focus |

### Input File Format

Create a text file with one domain base name per line. Comments start with `#`:

```
# My domain watchlist
promptcraft
synthiq
vectrix
mindforge
# AI trending terms
ragpipe
llmguard
agentchain
```

The tool automatically strips any TLD you accidentally include — `promptcraft.ai` becomes `promptcraft` and gets checked across all selected TLDs.

## How It Works

The tool runs **4 independent verification checks** for each domain:

| Check | Protocol | What It Does | Weight |
|-------|----------|--------------|--------|
| **RDAP** | RDAP over HTTPS | Queries the authoritative domain registry | 3x (highest) |
| **WHOIS** | WHOIS (port 43) | Queries traditional WHOIS database | 2x |
| **DNS** | DNS (A + NS records) | Checks if domain resolves in DNS | 2x |
| **HTTP** | HTTP/HTTPS | Attempts to load the website | 1x |

Signals are combined into a **weighted verdict**:

- **AVAILABLE** (confidence 60-95%) — No registration found across checks
- **TAKEN** (confidence 60-99%) — Registration confirmed, shows registrar info
- **UNCERTAIN** (50%) — Mixed signals, verify manually on registrar
- **UNKNOWN** (0%) — All checks failed (timeout/network issue)

### Important Accuracy Note

> **WHOIS/RDAP can miss parked domains.** A domain might be registered but have no DNS records, no website, and delayed WHOIS propagation. The tool catches ~85-90% of taken domains. **Always verify "AVAILABLE" results on GoDaddy/Namecheap before purchasing.** The `--open` flag makes this easy.

## Output Examples

### Matrix View (Terminal)

```
+----------------------------------------------------------+
|                  Availability Matrix                      |
+--------------+------+------+------+------+---------------+
| Domain       | .ai  | .com | .io  | .dev | Best Pick     |
+--------------+------+------+------+------+---------------+
| synthiq      | FREE | FREE | FREE | FREE | .ai           |
| promptcraft  | TAKEN| TAKEN| FREE | FREE | .io           |
| vectrix      | FREE | TAKEN| TAKEN| FREE | .ai           |
| mindforge    | FREE | TAKEN| TAKEN| TAKEN| .ai           |
+--------------+------+------+------+------+---------------+
```

### CSV Export

Exports a spreadsheet with columns: `Base Name`, `.ai Status`, `.ai Conf%`, `.ai Registrar`, `.com Status`, ... `Best Available`, `GoDaddy Link`

### JSON Export

Full structured data with all check details for programmatic use.

## Supported TLDs & Pricing

| TLD | Price (INR/yr) | Min Period | Category | Best For |
|-----|---------------|------------|----------|----------|
| `.ai` | ~₹6,000-8,000 | 2 years | Premium | AI/ML startups, highest flip value |
| `.com` | ~₹800-1,200 | 1 year | Standard | Universal, safest long-term hold |
| `.io` | ~₹2,500-4,000 | 1 year | Premium | Tech startups, developer tools |
| `.dev` | ~₹1,000-1,500 | 1 year | Mid | Developer products, open source |
| `.app` | ~₹1,200-1,800 | 1 year | Mid | Mobile/web applications |
| `.co` | ~₹800-2,500 | 1 year | Mid | Startups, .com alternative |
| `.tech` | ~₹800-3,000 | 1 year | Mid | Technology companies |
| `.xyz` | ~₹200-800 | 1 year | Budget | Creative/cheap experiments |
| `.net` | ~₹800-1,200 | 1 year | Standard | Networks, infrastructure |
| `.org` | ~₹800-1,200 | 1 year | Standard | Non-profits, open source |
| `.in` | ~₹500-800 | 1 year | Budget | Indian businesses (local SEO) |
| `.co.in` | ~₹300-600 | 1 year | Budget | India (cheapest option) |
| `.info` | ~₹300-900 | 1 year | Budget | Informational sites |
| `.online` | ~₹200-1,500 | 1 year | Budget | Budget web presence |
| `.store` | ~₹200-4,000 | 1 year | Budget | E-commerce |

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError` | Missing dependency | `pip install rich requests python-whois dnspython` |
| `UnicodeDecodeError` | Windows encoding | Already handled — file reads use `utf-8` with `errors="ignore"` |
| `WhoisDomainNotFoundError` crash | Old `python-whois` exception handling | Already handled — catches all exception types |
| All results show UNKNOWN | No internet or firewall blocking | Check internet connection, try different network |
| WHOIS timeouts | WHOIS server rate limiting | Normal — RDAP + DNS checks still provide a verdict |
| False "AVAILABLE" | Domain parked without DNS/website | **Always verify on GoDaddy/Namecheap before buying** |
| Slow on `--all` with large file | 15 TLDs × many domains = many lookups | Use `--popular` or `--tlds` to reduce scope |

## Requirements

- **Python** 3.8 or higher
- **OS:** Windows, macOS, Linux
- **Internet connection** (queries external WHOIS/DNS servers)
- **Dependencies:**
  - `rich` — Terminal dashboard rendering
  - `requests` — HTTP/HTTPS and RDAP queries
  - `python-whois` — WHOIS protocol queries
  - `dnspython` — DNS record lookups

## Project Structure

```
domain-checker/
├── domain_checker.py      # Main CLI tool (single file, no dependencies beyond pip)
├── domains_v3.txt         # Sample domain watchlist (95 names)
├── README.md              # This file
├── CHANGELOG.md           # Version history
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
└── domain_results.csv     # Generated output (after running with --csv)
```

## Contributing

Contributions are welcome! Some ideas:

- Add more TLDs (`.agency`, `.cloud`, `.design`, etc.)
- Parallel/async checking for speed
- Web UI dashboard version
- Domain price comparison across registrars
- Expiring domain alerts
- Integration with registrar APIs for direct purchase

## Disclaimer

This tool queries publicly available WHOIS/RDAP/DNS data using standard internet protocols. It is designed for legitimate domain research purposes. Results are estimates — always verify availability on a registrar website before purchasing. Domain investing is speculative and carries risk. This tool is not affiliated with any domain registrar.

## License

[MIT License](LICENSE) — Use it however you want.

---

**Built with Claude AI** | If this tool saved you time, star the repo!
