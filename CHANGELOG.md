# Changelog

All notable changes to **Domain Vestor** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.0.0] - 2026-03-22

### Release — Domain Vestor v1.0

First public release of Domain Vestor — a multi-TLD domain availability checker built for domain investors and startup founders.

### Features

- **Multi-TLD Matrix View** — Check a single base name across up to 15 TLDs simultaneously (.ai, .com, .io, .dev, .app, .co, .tech, .xyz, .net, .org, .in, .co.in, .info, .online, .store)
- **4-Signal Verification Engine** — RDAP, WHOIS, DNS, and HTTP checks combined with weighted confidence scoring (RDAP 3x, WHOIS 2x, DNS 2x, HTTP 1x)
- **6 TLD Presets** — `--all`, `--popular`, `--cheap`, `--premium`, `--india`, or default 4-TLD set
- **Custom TLD Selection** — `--tlds ai com io in` to pick exactly which extensions to check
- **TLD-Specific RDAP Endpoints** — Uses correct authoritative RDAP server per TLD (Verisign for .com/.net, Google for .dev/.app, Identity Digital for .ai/.io, etc.)
- **"Best Pick" Column** — Matrix auto-highlights the best available TLD per domain (prioritizes .ai > .com > .io > .dev)
- **Available Domains Summary** — Flat list of all free domain+TLD combos with GoDaddy buy links
- **TLD Pricing Reference** — INR/yr cost, minimum registration period, and tier category for each TLD
- **Smart TLD Stripping** — Input files accept `promptcraft.ai` or just `promptcraft` — handles both
- **CSV Export** — `--csv` exports matrix with all TLDs, best available, and GoDaddy links
- **JSON Export** — `--json` exports full structured data with all check details
- **Browser Integration** — `--open` opens GoDaddy registration page for each available domain
- **Verbose Mode** — `--verbose` shows per-check breakdown (RDAP/WHOIS/DNS/HTTP status for each domain)
- **Batch Input** — `--file` loads domain names from text file (one per line, # comments)
- **Interactive Mode** — Run without arguments to enter domains manually
- **Dependency Checker** — Auto-detects missing pip packages and shows install command
- **Rate Limiting** — 0.25s delay between checks to respect WHOIS servers
- **Robust Error Handling** — Each check runs in isolated try-except; one failure doesn't crash the run
- **Windows Compatible** — UTF-8 file reading with fallback, handles all `python-whois` exception variants
- **Rich Terminal Dashboard** — Color-coded matrix tables, progress bar, panels via `rich` library
- **Minimal Output Mode** — `--no-dashboard` for scripting and piping

### Technical Details

- Single Python file, no complex project structure
- Queries RDAP (modern WHOIS), traditional WHOIS, Google/Cloudflare DNS (8.8.8.8, 1.1.1.1), and HTTP/HTTPS
- Supports 15 TLDs with TLD-specific RDAP bootstrap endpoints
- Weighted verdict algorithm: taken signals vs available signals with configurable weights
- Confidence scoring: 0-99% based on agreement across checks

---

### Legend

- **Features** — New capabilities
- **Fixed** — Bug fixes
- **Changed** — Behavior changes
- **Removed** — Removed features
