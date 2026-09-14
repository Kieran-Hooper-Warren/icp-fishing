# ICP Fishing

Two 30-second rounds. Round 1: hook anything, ICP +1, junk −1. Round 2: only fish giving off a
signal can be hooked, and only ICP fish carry signals, so every catch is +1.

## One command per prospect
```bash
python3 make.py --to Dave --company Shell --icp "COO, Chief Operating Officer, VP Operations" --cta "https://calendly.com/you/15min" --ctaLabel "Book 15 min" --publish
```
It prints the link to send. `--publish` commits and pushes; GitHub Pages goes live within a minute.

Or, with no publishing at all, open `<live-url>/?build=1`, fill the form and copy the long link.

## Files
- `index.html` — the game and the template.
- `make.py` — makes one prospect's page under `docs/<slug>/`.
- `docs/` — what GitHub Pages serves. Do not edit by hand.

## Parameters (query string or baked in)
`to`, `company`, `icp`, `junk`, `from`, `cta`, `ctaLabel`. All optional.
