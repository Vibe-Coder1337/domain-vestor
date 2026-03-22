#!/usr/bin/env python3
"""
+==============================================================+
|            Domain Vestor v1.0 - Multi-TLD                    |
|   Check domains across .ai .com .io .dev .app .co & more     |
|       WHOIS/RDAP + DNS + HTTP multi-signal checks            |
+==============================================================+

Usage:
    python domain_vestor.py --file domains.txt                    # Default: .ai .com .io .dev
    python domain_vestor.py --file domains.txt --tlds ai com io   # Specific TLDs
    python domain_vestor.py --file domains.txt --all              # ALL 15 TLDs
    python domain_vestor.py --file domains.txt --cheap            # Budget TLDs only
    python domain_vestor.py promptcraft nexiq --tlds ai com io    # Inline domains
    python domain_vestor.py --file domains.txt --csv --open       # Export + open in browser

Requirements:
    pip install rich requests python-whois dnspython
"""

import sys, os, json, time, argparse, webbrowser
import csv as csv_module
from datetime import datetime

def check_deps():
    missing = []
    for pkg, pip_name in [("rich","rich"),("requests","requests"),("whois","python-whois"),("dns.resolver","dnspython")]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print(f"\n  Missing: {', '.join(missing)}")
        print(f"  Run: pip install {' '.join(missing)}\n")
        sys.exit(1)
check_deps()

import requests, whois, dns.resolver
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt
from rich import box

console = Console()

# ======================================================================
#  TLD CONFIG
# ======================================================================

TLD_CONFIG = {
    "ai":     {"price": "~6,000-8,000", "min_yr": 2, "cat": "premium",  "color": "bright_magenta"},
    "com":    {"price": "~800-1,200",   "min_yr": 1, "cat": "standard", "color": "bright_green"},
    "io":     {"price": "~2,500-4,000", "min_yr": 1, "cat": "premium",  "color": "bright_cyan"},
    "dev":    {"price": "~1,000-1,500", "min_yr": 1, "cat": "mid",      "color": "bright_yellow"},
    "app":    {"price": "~1,200-1,800", "min_yr": 1, "cat": "mid",      "color": "yellow"},
    "co":     {"price": "~800-2,500",   "min_yr": 1, "cat": "mid",      "color": "cyan"},
    "tech":   {"price": "~800-3,000",   "min_yr": 1, "cat": "mid",      "color": "blue"},
    "xyz":    {"price": "~200-800",     "min_yr": 1, "cat": "budget",   "color": "white"},
    "net":    {"price": "~800-1,200",   "min_yr": 1, "cat": "standard", "color": "green"},
    "org":    {"price": "~800-1,200",   "min_yr": 1, "cat": "standard", "color": "green"},
    "in":     {"price": "~500-800",     "min_yr": 1, "cat": "budget",   "color": "bright_yellow"},
    "co.in":  {"price": "~300-600",     "min_yr": 1, "cat": "budget",   "color": "yellow"},
    "info":   {"price": "~300-900",     "min_yr": 1, "cat": "budget",   "color": "dim"},
    "online": {"price": "~200-1,500",   "min_yr": 1, "cat": "budget",   "color": "dim"},
    "store":  {"price": "~200-4,000",   "min_yr": 1, "cat": "budget",   "color": "dim"},
}

TLD_PRESETS = {
    "default": ["ai", "com", "io", "dev"],
    "popular": ["ai", "com", "io", "dev", "app", "co", "tech"],
    "all":     list(TLD_CONFIG.keys()),
    "cheap":   ["com", "xyz", "in", "co.in", "net", "info", "online"],
    "premium": ["ai", "io", "dev", "app", "co"],
    "india":   ["com", "in", "co.in", "ai", "io"],
}

REGISTRAR_URLS = {
    "GoDaddy":    "https://www.godaddy.com/en-in/domainsearch/find?domainToCheck={domain}",
    "Namecheap":  "https://www.namecheap.com/domains/registration/results/?domain={domain}",
    "BigRock":    "https://www.bigrock.in/domain-registration/search?domain={domain}",
    "Cloudflare": "https://dash.cloudflare.com/?to=/:account/domains/register/{domain}",
}

RDAP_BOOTSTRAP = {
    "default": ["https://rdap.org/domain/{domain}"],
    "ai":  ["https://rdap.identitydigital.services/rdap/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "com": ["https://rdap.verisign.com/com/v1/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "net": ["https://rdap.verisign.com/net/v1/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "io":  ["https://rdap.identitydigital.services/rdap/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "dev": ["https://rdap.nic.google/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "app": ["https://rdap.nic.google/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "org": ["https://rdap.org/domain/{domain}"],
    "xyz": ["https://rdap.nic.xyz/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "co":  ["https://rdap.nic.co/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "tech":["https://rdap.nic.tech/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "in":  ["https://rdap.registry.in/domain/{domain}", "https://rdap.org/domain/{domain}"],
    "info":["https://rdap.afilias.net/rdap/info/domain/{domain}", "https://rdap.org/domain/{domain}"],
}


# ======================================================================
#  CHECKER ENGINE
# ======================================================================

class DomainChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DomainVestor/1.0 (research-tool)",
            "Accept": "application/rdap+json, application/json",
        })

    def check_rdap(self, fqdn):
        result = {"method": "RDAP", "status": "unknown", "details": {}}
        tld = fqdn.split(".")[-1]
        endpoints = RDAP_BOOTSTRAP.get(tld, RDAP_BOOTSTRAP["default"])
        for ep in endpoints:
            url = ep.format(domain=fqdn)
            try:
                r = self.session.get(url, timeout=8)
                if r.status_code == 200:
                    data = r.json()
                    result["status"] = "taken"
                    result["details"]["registrar"] = self._rdap_reg(data)
                    result["details"]["expires"] = self._rdap_date(data, "expiration")
                    return result
                elif r.status_code == 404:
                    result["status"] = "available"
                    return result
            except Exception:
                continue
        return result

    def check_whois(self, fqdn):
        result = {"method": "WHOIS", "status": "unknown", "details": {}}
        try:
            w = whois.whois(fqdn)
            if w and w.domain_name:
                result["status"] = "taken"
                result["details"]["registrar"] = (w.registrar or "")[:30]
                exp = w.expiration_date
                if isinstance(exp, list):
                    exp = exp[0]
                result["details"]["expires"] = str(exp)[:10] if exp else ""
            else:
                result["status"] = "available"
        except Exception as e:
            err = (str(e) + type(e).__name__).lower()
            if any(k in err for k in ["not found","no match","no entries","notfound","no data","no whois"]):
                result["status"] = "available"
            else:
                result["details"]["error"] = type(e).__name__
        return result

    def check_dns(self, fqdn):
        result = {"method": "DNS", "status": "unknown", "details": {}}
        res = dns.resolver.Resolver()
        res.nameservers = ["8.8.8.8", "1.1.1.1"]
        res.timeout = 4
        res.lifetime = 4
        for rt in ["A", "NS"]:
            try:
                res.resolve(fqdn, rt)
                result["status"] = "taken"
                result["details"]["record"] = rt
                return result
            except Exception:
                pass
        result["status"] = "no_dns"
        return result

    def check_http(self, fqdn):
        result = {"method": "HTTP", "status": "unknown", "details": {}}
        for scheme in ["https", "http"]:
            try:
                r = self.session.get(f"{scheme}://{fqdn}", timeout=5, allow_redirects=True)
                result["status"] = "taken"
                result["details"]["code"] = r.status_code
                try:
                    s = r.text.lower().find("<title>")
                    e = r.text.lower().find("</title>")
                    if s > -1 and e > s:
                        result["details"]["title"] = r.text[s+7:e].strip()[:40]
                except Exception:
                    pass
                return result
            except Exception:
                continue
        result["status"] = "no_http"
        return result

    def check_single(self, fqdn):
        checks = {}
        for name, method in [("rdap", self.check_rdap), ("whois", self.check_whois),
                              ("dns", self.check_dns), ("http", self.check_http)]:
            try:
                checks[name] = method(fqdn)
            except Exception as e:
                checks[name] = {"method": name.upper(), "status": "unknown", "details": {"error": type(e).__name__}}

        verdict, conf = self._verdict(checks)
        reg = ""
        for src in ["rdap", "whois"]:
            if checks.get(src, {}).get("status") == "taken":
                reg = checks[src].get("details", {}).get("registrar", "")
                if reg: break

        return {"fqdn": fqdn, "verdict": verdict, "confidence": conf, "registrar": reg, "checks": checks}

    @staticmethod
    def _verdict(checks):
        taken, avail = 0, 0
        w = {"rdap": 3, "whois": 2, "dns": 2, "http": 1}
        for k, wt in w.items():
            st = checks.get(k, {}).get("status", "unknown")
            if st == "taken": taken += wt
            elif st in ("available", "no_dns", "no_http"): avail += wt
        total = taken + avail
        if total == 0: return "UNKNOWN", 0
        if taken > avail: return "TAKEN", min(99, int(taken/total*100))
        if avail > taken: return "AVAILABLE", min(95, int(avail/total*100))
        return "UNCERTAIN", 50

    @staticmethod
    def _rdap_reg(data):
        for ent in data.get("entities", []):
            if "registrar" in ent.get("roles", []):
                vc = ent.get("vcardArray", [])
                if len(vc) > 1:
                    for item in vc[1]:
                        if item[0] == "fn": return item[3]
                return ent.get("handle", "")
        return ""

    @staticmethod
    def _rdap_date(data, evt):
        for ev in data.get("events", []):
            if ev.get("eventAction") == evt:
                return ev.get("eventDate", "")[:10]
        return ""


# ======================================================================
#  DASHBOARD
# ======================================================================

class Dashboard:
    @staticmethod
    def banner():
        console.print()
        console.print(Panel(
            "[bold white]Domain Vestor v1.0[/bold white]\n"
            "[dim]WHOIS/RDAP + DNS + HTTP | Multi-TLD Matrix[/dim]",
            title="[bold cyan]DOMAIN VESTOR[/bold cyan]", border_style="cyan", width=58))

    @staticmethod
    def show_tlds(tlds):
        parts = []
        for t in tlds:
            c = TLD_CONFIG.get(t, {})
            col = c.get("color", "white")
            parts.append(f"[{col}].{t}[/{col}]")
        console.print(f"\n  [bold]Checking TLDs:[/bold] {' '.join(parts)}\n")

    @staticmethod
    def show_matrix(results, tlds):
        # Summary
        tot_a, tot_t, tot_all = 0, 0, 0
        for r in results:
            for tld in tlds:
                res = r["tlds"].get(tld, {})
                tot_all += 1
                v = res.get("verdict", "")
                if v == "AVAILABLE": tot_a += 1
                elif v == "TAKEN": tot_t += 1

        console.print(Panel(
            f"[green bold]AVAILABLE: {tot_a}[/green bold]  |  "
            f"[red bold]TAKEN: {tot_t}[/red bold]  |  "
            f"[dim]Total: {tot_all} checks ({len(results)} names x {len(tlds)} TLDs)[/dim]",
            title="[bold]Summary[/bold]", border_style="cyan"))
        console.print()

        # Matrix table
        table = Table(title="[bold]Availability Matrix[/bold]", box=box.ROUNDED,
                      border_style="bright_blue", show_lines=True)
        table.add_column("Domain", style="bold white", min_width=14, no_wrap=True)

        for tld in tlds:
            col = TLD_CONFIG.get(tld, {}).get("color", "white")
            table.add_column(f".{tld}", justify="center", width=max(len(tld)+4, 8),
                             header_style=f"bold {col}")

        table.add_column("Best Pick", justify="center", min_width=12, header_style="bold green")

        for r in results:
            row = [r["base"]]
            best_tld = None
            best_pri = 999
            for tld in tlds:
                res = r["tlds"].get(tld, {})
                v = res.get("verdict", "?")
                c = res.get("confidence", 0)
                if v == "AVAILABLE":
                    row.append(f"[bold green]FREE[/bold green] [dim]{c}%[/dim]")
                    pri = list(TLD_CONFIG.keys()).index(tld) if tld in TLD_CONFIG else 99
                    # Prefer ai > com > io > dev by custom priority
                    custom_pri = {"ai":1,"com":2,"io":3,"dev":4,"app":5,"co":6}.get(tld, 10+pri)
                    if custom_pri < best_pri:
                        best_pri = custom_pri
                        best_tld = tld
                elif v == "TAKEN":
                    row.append(f"[red]TAKEN[/red]")
                elif v == "UNCERTAIN":
                    row.append(f"[yellow]???[/yellow]")
                else:
                    row.append(f"[dim]?[/dim]")

            if best_tld:
                col = TLD_CONFIG.get(best_tld, {}).get("color", "white")
                row.append(f"[bold {col}].{best_tld}[/bold {col}]")
            else:
                row.append("[dim]-[/dim]")
            table.add_row(*row)

        console.print(table)

    @staticmethod
    def show_available(results, tlds):
        avail = []
        for r in results:
            for tld in tlds:
                res = r["tlds"].get(tld, {})
                if res.get("verdict") == "AVAILABLE":
                    fqdn = f"{r['base']}.{tld}"
                    avail.append({"fqdn": fqdn, "tld": tld, "conf": res["confidence"],
                                  "price": TLD_CONFIG.get(tld,{}).get("price","?")})
        if not avail:
            console.print("\n[yellow]No available domains found.[/yellow]")
            return avail

        console.print()
        t = Table(title=f"[bold green]Available for Registration ({len(avail)})[/bold green]",
                  box=box.ROUNDED, border_style="green")
        t.add_column("#", style="dim", width=4)
        t.add_column("Domain", style="bold", min_width=22)
        t.add_column("TLD", justify="center", width=6)
        t.add_column("Conf", justify="center", width=5)
        t.add_column("Price/yr (INR)", justify="right", width=16)

        for i, a in enumerate(avail, 1):
            col = TLD_CONFIG.get(a["tld"],{}).get("color","white")
            t.add_row(str(i), a["fqdn"], f"[{col}].{a['tld']}[/{col}]",
                      f"{a['conf']}%", f"[yellow]{a['price']}[/yellow]")
        console.print(t)

        # Print full buy links BELOW the table (not truncated)
        console.print()
        console.print(Panel("[bold]Buy Links — Copy full URL to browser[/bold]", border_style="cyan"))
        for i, a in enumerate(avail, 1):
            fqdn = a["fqdn"]
            console.print(f"\n  [bold white]{i}. {fqdn}[/bold white]")
            console.print(f"     [cyan]GoDaddy  :[/cyan] https://www.godaddy.com/en-in/domainsearch/find?domainToCheck={fqdn}")
            console.print(f"     [cyan]Namecheap:[/cyan] https://www.namecheap.com/domains/registration/results/?domain={fqdn}")
            console.print(f"     [cyan]BigRock  :[/cyan] https://www.bigrock.in/domain-registration/search?domain={fqdn}")

        return avail

    @staticmethod
    def show_prices(tlds):
        console.print()
        best_for = {
            "ai":"AI/ML startups, highest flip value",  "com":"Universal, safest hold",
            "io":"Tech startups, dev tools",            "dev":"Developer products, OSS",
            "app":"Mobile/web apps",                     "co":"Startups, .com alternative",
            "tech":"Tech companies",                     "xyz":"Cheap experiments",
            "net":"Networking, infra",                   "org":"Non-profit, open source",
            "in":"Indian business (local SEO)",          "co.in":"India (cheapest)",
            "info":"Informational sites",                "online":"Budget web presence",
            "store":"E-commerce",
        }
        t = Table(title="[bold]TLD Pricing (INR/yr)[/bold]", box=box.SIMPLE_HEAVY, border_style="yellow")
        t.add_column("TLD", width=7, style="bold")
        t.add_column("Price/yr", justify="right", width=14)
        t.add_column("Min", justify="center", width=4)
        t.add_column("Tier", width=9)
        t.add_column("Best For", min_width=25)
        for tld in tlds:
            c = TLD_CONFIG.get(tld, {})
            col = c.get("color","white")
            cat = c.get("cat","")
            cc = {"premium":"magenta","standard":"green","mid":"yellow","budget":"dim"}.get(cat,"white")
            t.add_row(f"[{col}].{tld}[/{col}]", f"[yellow]{c.get('price','?')}[/yellow]",
                      str(c.get("min_yr",1)), f"[{cc}]{cat}[/{cc}]", best_for.get(tld,""))
        console.print(t)


# ======================================================================
#  FILE I/O
# ======================================================================

def load_names(path):
    names = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            d = line.strip().lower()
            if not d or d.startswith("#"):
                continue
            # Strip any known TLD
            for tld in sorted(TLD_CONFIG.keys(), key=len, reverse=True):
                if d.endswith(f".{tld}"):
                    d = d[:-(len(tld)+1)]
                    break
            if d:
                names.append(d)
    return list(dict.fromkeys(names))

def strip_tld(name):
    name = name.strip().lower()
    for tld in sorted(TLD_CONFIG.keys(), key=len, reverse=True):
        if name.endswith(f".{tld}"):
            return name[:-(len(tld)+1)]
    return name

def export_csv(results, tlds, fname="domain_results.csv"):
    with open(fname, "w", newline="", encoding="utf-8") as f:
        w = csv_module.writer(f)
        hdr = ["Base Name"]
        for tld in tlds:
            hdr += [f".{tld} Status", f".{tld} Conf%", f".{tld} Registrar"]
        hdr += ["Best Available", "GoDaddy Link"]
        w.writerow(hdr)
        for r in results:
            row = [r["base"]]
            best = None
            for tld in tlds:
                res = r["tlds"].get(tld, {})
                row += [res.get("verdict","?"), res.get("confidence",""), res.get("registrar","")]
                if res.get("verdict") == "AVAILABLE" and not best:
                    best = f"{r['base']}.{tld}"
            row += [best or "", REGISTRAR_URLS["GoDaddy"].format(domain=best) if best else ""]
            w.writerow(row)
    console.print(f"\n[green]CSV exported:[/green] [bold]{fname}[/bold]")

def export_json(results, fname="domain_results.json"):
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    console.print(f"[green]JSON exported:[/green] [bold]{fname}[/bold]")


# ======================================================================
#  MAIN
# ======================================================================

def main():
    p = argparse.ArgumentParser(
        description="Domain Vestor v1.0 - Multi-TLD Matrix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
TLD Presets:
  --default    {', '.join(TLD_PRESETS['default'])}
  --popular    {', '.join(TLD_PRESETS['popular'])}
  --all        ALL {len(TLD_PRESETS['all'])} TLDs
  --cheap      {', '.join(TLD_PRESETS['cheap'])}
  --premium    {', '.join(TLD_PRESETS['premium'])}
  --india      {', '.join(TLD_PRESETS['india'])}

Examples:
  %(prog)s --file domains.txt                     Default 4 TLDs
  %(prog)s --file domains.txt --all               All 15 TLDs
  %(prog)s --file domains.txt --tlds ai com io    Pick specific
  %(prog)s --file domains.txt --cheap --csv       Budget + export
  %(prog)s promptcraft nexiq --popular --open     Inline + browser
        """)

    p.add_argument("domains", nargs="*", help="Base names (no TLD needed)")
    p.add_argument("--file", "-f", help="File with domain names")
    p.add_argument("--tlds", "-t", nargs="+", help="Specific TLDs to check")
    p.add_argument("--all", action="store_true", help="All 15 TLDs")
    p.add_argument("--popular", action="store_true", help="Popular 7 TLDs")
    p.add_argument("--cheap", action="store_true", help="Budget TLDs")
    p.add_argument("--premium", action="store_true", help="Premium TLDs")
    p.add_argument("--india", action="store_true", help="India-relevant TLDs")
    p.add_argument("--csv", action="store_true", help="Export CSV")
    p.add_argument("--json", action="store_true", help="Export JSON")
    p.add_argument("--open", "-o", action="store_true", help="Open available in browser")
    p.add_argument("--verbose", "-v", action="store_true", help="Detailed per-check output")
    p.add_argument("--no-dashboard", action="store_true", help="Minimal output")

    args = p.parse_args()
    dash = Dashboard()

    if not args.no_dashboard:
        dash.banner()

    # TLDs
    if args.tlds:
        tlds = [t.lower().lstrip(".") for t in args.tlds]
        bad = [t for t in tlds if t not in TLD_CONFIG]
        if bad:
            console.print(f"[red]Unknown TLDs: {', '.join(bad)}[/red]")
            console.print(f"[dim]Valid: {', '.join(TLD_CONFIG.keys())}[/dim]")
            sys.exit(1)
    elif args.all:     tlds = TLD_PRESETS["all"]
    elif args.popular: tlds = TLD_PRESETS["popular"]
    elif args.cheap:   tlds = TLD_PRESETS["cheap"]
    elif args.premium: tlds = TLD_PRESETS["premium"]
    elif args.india:   tlds = TLD_PRESETS["india"]
    else:              tlds = TLD_PRESETS["default"]

    if not args.no_dashboard:
        dash.show_tlds(tlds)

    # Names
    names = []
    if args.file:
        if not os.path.exists(args.file):
            console.print(f"[red]File not found: {args.file}[/red]"); sys.exit(1)
        names = load_names(args.file)
        console.print(f"  [dim]Loaded {len(names)} names from {args.file}[/dim]")

    if args.domains:
        for d in args.domains:
            n = strip_tld(d)
            if n: names.append(n)

    if not names:
        console.print("\n  [bold cyan]Enter base domain names[/bold cyan] (no TLD, empty to finish):")
        while True:
            line = Prompt.ask("  [cyan]Name[/cyan]", default="").strip()
            if not line:
                if names: break
                console.print("  [yellow]Enter at least one![/yellow]"); continue
            for part in line.replace(",", " ").split():
                n = strip_tld(part)
                if n:
                    names.append(n)
                    console.print(f"    [dim]+ {n}[/dim]")

    names = list(dict.fromkeys(names))
    if not names:
        console.print("[red]No domains.[/red]"); sys.exit(0)

    total = len(names) * len(tlds)
    console.print(f"\n  [bold]{len(names)} names x {len(tlds)} TLDs = {total} lookups[/bold]\n")

    # Run
    checker = DomainChecker()
    all_results = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(bar_width=30), TextColumn("{task.percentage:>3.0f}%"),
                  TextColumn("({task.completed}/{task.total})"), console=console) as prog:
        task = prog.add_task("Checking...", total=total)
        for name in names:
            tld_res = {}
            for tld in tlds:
                fqdn = f"{name}.{tld}"
                prog.update(task, description=f"[cyan]{fqdn}[/cyan]")
                try:
                    tld_res[tld] = checker.check_single(fqdn)
                except Exception:
                    tld_res[tld] = {"fqdn": fqdn, "verdict": "UNKNOWN", "confidence": 0, "registrar": "", "checks": {}}
                prog.advance(task)
                time.sleep(0.25)
            all_results.append({"base": name, "tlds": tld_res})

    console.print()

    # Display
    if args.no_dashboard:
        for r in all_results:
            for tld in tlds:
                res = r["tlds"].get(tld, {})
                v = res.get("verdict", "?")
                icon = {"AVAILABLE":"+","TAKEN":"X"}.get(v,"?")
                print(f"[{icon}] {r['base']+'.'+tld:30s} {v:12s} {res.get('confidence',0)}%")
    else:
        dash.show_matrix(all_results, tlds)
        avail = dash.show_available(all_results, tlds)
        dash.show_prices(tlds)

        if args.verbose:
            console.print()
            console.print(Panel("[bold]Detailed Checks[/bold]", border_style="cyan"))
            for r in all_results:
                for tld in tlds:
                    res = r["tlds"].get(tld)
                    if not res: continue
                    fqdn = f"{r['base']}.{tld}"
                    v = res["verdict"]
                    vc = {"AVAILABLE":"green","TAKEN":"red"}.get(v,"yellow")
                    console.print(f"\n  [{vc}]{v:10s}[/{vc}] [bold]{fqdn}[/bold] ({res['confidence']}%)")
                    for m, ck in res.get("checks",{}).items():
                        st = ck.get("status","?")
                        sc = "green" if st in ("available","no_dns","no_http") else "red" if st=="taken" else "yellow"
                        det = ""
                        d = ck.get("details",{})
                        if d.get("registrar"): det += f" reg={d['registrar'][:20]}"
                        if d.get("error"): det += f" err={d['error']}"
                        if d.get("title"): det += f' "{d["title"]}"'
                        console.print(f"      [{sc}]{st:10s}[/{sc}] {m.upper():6s}{det}")

    # Export
    if args.csv: export_csv(all_results, tlds)
    if args.json: export_json(all_results)

    # Open
    if args.open:
        opened = 0
        for r in all_results:
            for tld in tlds:
                res = r["tlds"].get(tld,{})
                if res.get("verdict") == "AVAILABLE":
                    webbrowser.open(REGISTRAR_URLS["GoDaddy"].format(domain=f"{r['base']}.{tld}"))
                    opened += 1; time.sleep(0.8)
        console.print(f"\n[bold]Opened {opened} domains in browser[/bold]" if opened else "\n[yellow]Nothing to open[/yellow]")

    console.print(f"\n[dim]Done {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Always verify on registrar before buying[/dim]\n")

if __name__ == "__main__":
    main()
