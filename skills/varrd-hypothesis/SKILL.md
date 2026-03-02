---
name: varrd-hypothesis
description: Get full details on a specific saved strategy — formula, metrics, version history
tools: ["Bash"]
---

# VARRD Hypothesis — Strategy Details

Use this skill when a user wants to see full details on a specific strategy from their library.

## Command

```bash
varrd hypothesis <hypothesis_id>
```

## How It Works

Returns complete details for a saved strategy: formula, setup code, statistical metrics, version history, and horizon results.

## Example

```bash
varrd hypothesis hyp_abc123
```

## Reading the Output

| Field | Description |
|-------|-------------|
| **Name** | Strategy name (e.g. "RSI Oversold ES Daily") |
| **Formula** | The boolean pattern expression |
| **Market** | Primary market tested on |
| **Direction** | LONG or SHORT |
| **Edge verdict** | STRONG EDGE, MARGINAL, or NO EDGE |
| **Win rate** | Historical win percentage |
| **Sharpe ratio** | Risk-adjusted return metric |
| **Profit factor** | Gross profits / gross losses |
| **Total trades** | Number of historical signals |
| **Horizon results** | Per-horizon stats (1, 3, 5, 10, 20 bars) |
| **Versions** | Formula revision history |

## Important: Trade Levels May Be Stale

Trade levels from `varrd hypothesis` are from when the strategy was last tested. They may be outdated. For fresh current prices:

- Use `varrd scan` — if the strategy is firing, you get fresh levels
- Use `varrd research "Load hypothesis <id>"` then "show me the trade setup" — forces fresh calculation

## Tips

- Get hypothesis IDs from `varrd scan` or `varrd search` results
- This command is **free** — no credits consumed
- Use this to understand a strategy before acting on scan signals

## Cost

Free. No credits consumed.

## Python SDK Equivalent

```python
from varrd import VARRD
v = VARRD()
hyp = v.get_hypothesis("hyp_abc123")
print(f"{hyp.name}: {hyp.win_rate:.0%} WR, {hyp.sharpe:.2f} Sharpe")
```
