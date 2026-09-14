#!/usr/bin/env python3
"""Make ICP Fishing links (and optionally pages) for every row of a CSV.

  python3 batch.py prospects.csv                 # writes prospects-links.csv with a `link` column (query links)
  python3 batch.py prospects.csv --pages         # also writes docs/<slug>/index.html for clean links
  python3 batch.py prospects.csv --pages --publish   # ...and commits + pushes so they go live

CSV columns (case-insensitive, any order; extra columns are kept):
  first name  : first_name | first | name | to | prospect
  company     : company | organisation | organization | account
  icp         : icp | title | titles | sells_to | persona | target_title
  cta (opt)   : cta | link | booking
Rows with no first name or no icp are skipped and reported.
"""
import csv, json, os, re, subprocess, sys, unicodedata
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "index.html")
SITE = os.path.join(HERE, "docs")
BASE = os.environ.get("ICPFISH_URL", "https://kieran-hooper-warren.github.io/icp-fishing").rstrip("/")
MARK = re.compile(r'<script type="application/json" id="cfg">.*?</script>', re.S)
ALIASES = {
    "to": ["first_name", "firstname", "first name", "first", "name", "to", "prospect", "contact"],
    "company": ["company", "company name", "organisation", "organization", "account", "employer"],
    "icp": ["icp", "title", "titles", "sells_to", "sells to", "persona", "target_title", "target title", "buyer", "buyer title"],
    "cta": ["cta", "link", "booking", "calendly"],
}

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "prospect"

def pick(headers, names):
    low = {h.lower().strip(): h for h in headers}
    for n in names:
        if n in low:
            return low[n]
    for h in headers:  # fuzzy: alias appears inside the header, e.g. "Title they sell to"
        hl = h.lower()
        if any(n in hl for n in names if len(n) > 2):
            return h
    return None

def qlink(cfg):
    q = "&".join(k + "=" + quote(v, safe=",") for k, v in cfg.items())
    return BASE + "/?" + q

def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        sys.exit(__doc__)
    src_csv = sys.argv[1]; pages = "--pages" in sys.argv; publish = "--publish" in sys.argv
    with open(src_csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("CSV is empty")
    headers = list(rows[0].keys())
    col = {k: pick(headers, v) for k, v in ALIASES.items()}
    if not col["to"] or not col["icp"]:
        sys.exit("Need a first-name column and an icp/title column. Found headers: " + ", ".join(headers))
    print("using columns:", {k: v for k, v in col.items() if v})

    template = open(TEMPLATE, encoding="utf-8").read() if pages else None
    if pages:
        os.makedirs(SITE, exist_ok=True)
        open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(template)

    out_rows, skipped, seen = [], 0, {}
    for r in rows:
        to = (r.get(col["to"]) or "").strip().split()[0:1]
        to = to[0] if to else ""
        icp = (r.get(col["icp"]) or "").strip()
        company = (r.get(col["company"]) or "").strip() if col["company"] else ""
        cta = (r.get(col["cta"]) or "").strip() if col["cta"] else ""
        if not to or not icp:
            skipped += 1; r["link"] = ""; r["page"] = ""; out_rows.append(r); continue
        cfg = {"to": to}
        if company: cfg["company"] = company
        cfg["icp"] = icp
        if cta: cfg["cta"] = cta
        r["link"] = qlink(cfg)
        r["page"] = ""
        if pages:
            slug = slugify(to + ("-" + company if company else ""))
            n = seen.get(slug, 0) + 1; seen[slug] = n
            if n > 1: slug = slug + "-" + str(n)
            payload = json.dumps(cfg, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            html = MARK.sub(lambda m: '<script type="application/json" id="cfg">' + payload + "</script>", template, count=1)
            os.makedirs(os.path.join(SITE, slug), exist_ok=True)
            open(os.path.join(SITE, slug, "index.html"), "w", encoding="utf-8").write(html)
            r["page"] = BASE + "/" + slug + "/"
        out_rows.append(r)

    out_csv = re.sub(r"\.csv$", "", src_csv, flags=re.I) + "-links.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers + ["link", "page"]); w.writeheader(); w.writerows(out_rows)
    made = len(out_rows) - skipped
    print("wrote", out_csv, "with", made, "links", ("and pages" if pages else ""), ("(" + str(skipped) + " rows skipped: missing name or icp)" if skipped else ""))
    if pages and publish:
        subprocess.run(["git", "add", "-A"], cwd=HERE, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "Add " + str(made) + " prospect pages from " + os.path.basename(src_csv)], cwd=HERE, check=True)
        subprocess.run(["git", "push", "-q"], cwd=HERE, check=True)
        print("published. Pages go live within a minute or two.")
    elif pages:
        print("pages written to docs/. Re-run with --publish (or commit and push) to make them live.")

if __name__ == "__main__":
    main()
