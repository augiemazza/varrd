---
name: varrd-scan
description: Scan saved strategies against live market data — see what's firing right now with exact trade levels
tools: ["Bash"]
---

# VARRD Scan — What's Firing Right Now

Use this skill when a user wants to check which of their saved strategies are producing signals right now, with exact entry/stop/target prices.

## Command

```bash
varrd scan
varrd scan --only-firing
varrd scan --market ES
varrd scan --market ES --only-firing
```

## How It Works

Scans all saved strategies against current market data. Returns which strategies are firing with exact dollar entry, stop-loss, and take-profit prices computed against live data. These trade levels are FRESH — computed right now, not stored from a past test.

## Options

| Flag | Description |
|------|-------------|
| `--only-firing` | Only show strategies producing signals right now |
| `--market ES` | Filter to a specific market symbol |

## Reading the Output

Each result includes:
- **Strategy name** and hypothesis ID
- **Market** and direction (LONG/SHORT)
- **Firing status** — is the pattern active right now?
- **Edge verdict** — STRONG EDGE, MARGINAL, or NO EDGE
- **Win rate** and **Sharpe ratio**
- **Entry price**, **stop-loss**, **take-profit** — exact dollar levels

## Fresh vs Stale Trade Levels

This is critical:
- `varrd scan` returns **FRESH** levels (computed against live data right now)
- `varrd hypothesis <id>` returns **STORED** stats (may be outdated)
- If you need fresh levels on a non-firing strategy, use `varrd research "Load hypothesis <id>"` then ask for the trade setup

## Tips

- Use `--only-firing` for actionable signals only — skip dormant strategies
- Scan is **free** — no credits consumed
- Run it daily or on a schedule to catch new signals
- Combine with `--market` to focus on one asset class

## Cost

Free. No credits consumed.

## Python SDK Equivalent

```python
from varrd import VARRD
v = VARRD()
signals = v.scan(only_firing=True)
for s in signals.results:
    if s.firing_now:
        print(f"{s.name}: {s.direction} {s.market} @ ${s.entry_price}")
        print(f"  Stop: ${s.stop_loss_price}  Target: ${s.take_profit_price}")
```
