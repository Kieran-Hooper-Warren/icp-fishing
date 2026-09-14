#!/usr/bin/env python3
"""Spin up a personal ICP Fishing page for one prospect.

Example:
  python3 make.py --to Dave --company Shell --icp "COO, Chief Operating Officer, VP Operations" \
      --cta "https://calendly.com/kieran/15min"

Writes docs/<slug>/index.html and refreshes docs/index.html from the template.
Add --publish to commit, push to GitHub and print the live link.
"""
import argparse, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "index.html")
SITE = os.path.join(HERE, "docs")
PAGES_URL = os.environ.get("ICPFISH_URL", "https://kieran-hooper-warren.github.io/icp-fishing").rstrip("/")
MARK = re.compile(r'<script type="application/json" id="cfg">.*?</script>', re.S)

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "prospect"

def main():
    p = argparse.ArgumentParser(description="Generate a personal ICP Fishing page.")
    p.add_argument("--to", required=True, help="Prospect first name, e.g. Dave")
    p.add_argument("--company", default="", help="Prospect's company, e.g. Shell")
    p.add_argument("--icp", required=True, help="Comma-separated titles they sell to, first one is named on screen")
    p.add_argument("--junk", default="", help="Optional comma-separated wrong-fit titles (blank = built-in list)")
    p.add_argument("--from", dest="sender", default="Kieran", help="Your name")
    p.add_argument("--cta", default="", help="Button link, e.g. https://... or mailto:...")
    p.add_argument("--slug", default="", help="URL path (default: from --to, plus company if given)")
    p.add_argument("--publish", action="store_true", help="git commit + push so the link goes live")
    a = p.parse_args()

    if not os.path.exists(TEMPLATE):
        sys.exit("index.html template not found next to make.py")
    src = open(TEMPLATE, encoding="utf-8").read()
    if not MARK.search(src):
        sys.exit("template is missing the cfg marker")

    cfg = {"to": a.to.strip(), "icp": a.icp.strip(), "from": a.sender.strip()}
    for k, v in (("company", a.company), ("junk", a.junk), ("cta", a.cta)):
        if v.strip():
            cfg[k] = v.strip()
    payload = json.dumps(cfg, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = MARK.sub(lambda m: '<script type="application/json" id="cfg">' + payload + "</script>", src, count=1)

    slug = slugify(a.slug or (a.to + ("-" + a.company if a.company else "")))
    os.makedirs(SITE, exist_ok=True)
    os.makedirs(os.path.join(SITE, slug), exist_ok=True)
    out = os.path.join(SITE, slug, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(src)
    print("wrote", os.path.relpath(out, HERE))
    link = (PAGES_URL or "https://<your-pages-url>") + "/" + slug + "/"
    if a.publish:
        import subprocess
        try:
            subprocess.run(["git", "add", "-A"], cwd=HERE, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "Add game for " + a.to.strip() + (" at " + a.company.strip() if a.company.strip() else "")], cwd=HERE, check=True)
            subprocess.run(["git", "push", "-q"], cwd=HERE, check=True)
            print("published. GitHub Pages usually updates within a minute.")
        except subprocess.CalledProcessError as e:
            sys.exit("publish failed: " + str(e))
    else:
        print("not published yet. Re-run with --publish, or commit and push the docs folder.")
    print("send Dave this link:  " + link if a.to.strip().lower() == "dave" else "send this link:  " + link)

if __name__ == "__main__":
    main()
