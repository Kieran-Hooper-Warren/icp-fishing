# ICP Fishing

Two 10-second rounds. Round 1: hook anything, ICP +1, junk −1. Round 2: only fish giving off a
signal can be hooked, and only ICP fish carry signals, so every catch is +1.

## One command per prospect
```bash
python3 make.py --to Dave --company Shell --icp "COO, Chief Operating Officer, VP Operations" --cta "https://calendly.com/you/15min" --publish
```
It prints the link to send. `--publish` commits and pushes; GitHub Pages goes live within a minute.

Or, with no publishing at all, open https://kieran-hooper-warren.github.io/icp-fishing/?build=1, fill the form and copy the long link.

## Boss battle
After Round 2 the player can fight a random boss (IT Director or Finance Director): tap to fire arrows,
4 timed hits win, 20-second timer. All objection/rebuttal copy is in the `BOSSES` object near the bottom of
`index.html`. The fight loads Three.js r128 from cdnjs on demand, so it needs an internet connection;
the fishing rounds still work offline.

## Files
- `index.html` — the game and the template.
- `make.py` — makes one prospect's page under `docs/<slug>/`.
- `docs/` — what GitHub Pages serves. Do not edit by hand.

## Parameters (query string or baked in)
`to`, `company`, `icp`, `junk`, `from`, `cta`. All optional. The button always reads "Say hi to the guy asking for your attention" and
goes to https://calendly.com/khw-r6mn unless `cta` is set. Known ICP titles (COO, CFO, Head of Facilities, ...)
automatically pull in their variations, e.g. `icp=COO` also fishes for Chief Operating Officer, Head of Operations,
Operations Director and VP Operations. Unknown titles are used exactly as typed.
