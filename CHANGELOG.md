# Changelog

All notable changes to the **Domain Availability Checker** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [3.0.0] - 2026-03-22

### Highlights

Complete rewrite. The tool now checks domain names across **multiple TLD extensions simultaneously** and displays results in a color-coded matrix dashboard.

### Added

- **Multi-TLD Matrix View** — Check a single base name across up to 15 TLDs (.ai, .com, .io, .dev, .app, .co, .tech, .xyz, .net, .org, .in, .co.in, .info, .online, .store)
- **6 TLD Presets** — Quick selection via `--all`, `--popular`, `--cheap`, `--premium`, `--india`, or the default 4-TLD set
- **Custom TLD selection** — `--tlds ai com io in` to pick exactly which extensions to check
- **TLD-specific RDAP endpoints** — Uses the correct authoritative RDAP server for each TLD (Verisign for .com/.net, Google for .dev/.app, Identity Digital for .ai/.io, etc.)
- **"Best Pick" column** — Matrix automatically highlights the best available TLD per domain name (prioritizes .ai > .com > .io > .dev)
- **Available domains summary table** — Flat list of all FREE domain+TLD combos with GoDaddy buy links
- **TLD pricing reference table** — Shows INR/yr cost, minimum registration period, and category for each TLD
- **Smart TLD stripping** — Input files can contain `promptcraft.ai` or just `promptcraft` — the tool handles both

### Changed

- **Architecture** — Fully rewritten from single-TLD checker to multi-TLD matrix engine
- **Input format** — Domain file now uses base names (no extension needed)
- **Output format** — Matrix table replaces the old single-column list
- **CSV export** — Now includes columns for every TLD checked, plus "Best Available" and "GoDaddy Link"
- **Progress bar** — Shows `(completed/total)` where total = names × TLDs

### Removed

- Old `.ai`-only hardcoded logic
- Single-TLD `PRICE_ESTIMATES` constant (replaced by `TLD_CONFIG` dictionary)

---

## [2.1.0] - 2026-03-22

### Fixed

- **Windows crash fix** — `WhoisDomainNotFoundError` was not caught because `python-whois` uses different exception class names across versions. Now catches all exceptions and inspects error message text for "not found" / "no match" patterns
- **Crash-proof check isolation** — Each of the 4 checks (RDAP, WHOIS, DNS, HTTP) now runs inside its own try-except block at the orchestrator level. If one check crashes, the others still run
- **Socket timeout handling** — WHOIS socket timeouts no longer kill the entire run

---

## [2.0.1] - 2026-03-22

### Fixed

- **Windows encoding crash** — `UnicodeDecodeError` on Windows when reading `domains.txt` containing Unicode box-drawing characters (═══). Fixed by adding `encoding="utf-8", errors="ignore"` to file reader
- **domains.txt** — Replaced Unicode decorative comments with plain ASCII

---

## [2.0.0] - 2026-03-22

### Highlights

First public release. Single-file CLI tool for checking `.ai` domain availability.

### Added

- **4-signal verification engine** — RDAP, WHOIS, DNS, and HTTP checks combined with weighted confidence scoring
- **RDAP support** — Uses the modern Registration Data Access Protocol (replacement for WHOIS) via Identity Digital's API
- **WHOIS support** — Traditional WHOIS queries via `python-whois` library
- **DNS checking** — Queries Google (8.8.8.8) and Cloudflare (1.1.1.1) DNS for A, AAAA, NS, MX records
- **HTTP probing** — Attempts HTTPS then HTTP connection to detect active websites
- **Rich terminal dashboard** — Color-coded tables with summary stats, available/taken sections
- **Registrar buy links** — Generates direct links to GoDaddy, Namecheap, BigRock, Cloudflare, Dynadot for each available domain
- **CSV export** — `--csv` flag exports results to `domain_results.csv`
- **JSON export** — `--json` flag exports full check data
- **Browser integration** — `--open` flag opens GoDaddy registration page for available domains
- **Verbose mode** — `--verbose` shows per-check breakdown for each domain
- **Batch input** — `--file` flag loads domain names from text file
- **Interactive mode** — Run without arguments to enter domains manually
- **Dependency checker** — Auto-detects missing pip packages and shows install command
- **Rate limiting** — 0.5s delay between checks to be respectful to WHOIS servers

---

## [1.0.0] - 2026-03-22 (Internal)

### Added

- Initial prototype — HTML domain suggestion list with investment scores
- Domain brainstorming with 25 AI-themed name suggestions
- TLD pricing guide
- Investment strategy recommendations

---

### Legend

- **Added** — New features
- **Changed** — Behavior changes in existing features
- **Fixed** — Bug fixes
- **Removed** — Removed features
- **Security** — Security-related changes
