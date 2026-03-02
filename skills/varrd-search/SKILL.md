---
name: varrd-search
description: Find saved strategies by keyword or natural language query
tools: ["Bash"]
---

# VARRD Search — Find Saved Strategies

Use this skill when a user wants to find strategies in their library by topic, keyword, or market.

## Command

```bash
varrd search "<query>"
varrd search "RSI oversold" --market ES
varrd search "momentum strategies" --limit 5
```

## How It Works

Searches all saved strategies using keyword and semantic matching. Returns matches ranked by relevance with key stats (win rate, Sharpe, edge status).

## Options

| Flag | Description |
|------|-------------|
| `--market ES` | Filter results to a specific market |
| `--limit N` | Max results to return (default 10) |

## Examples

```bash
varrd search "momentum strategies"
varrd search "RSI oversold"
varrd search "corn seasonal"
varrd search "mean reversion" --market ES
varrd search "volatility" --limit 20
```

## Reading the Output

Each result includes:
- **Strategy name** and hypothesis ID
- **Formula** — the pattern expression
- **Market** and direction
- **Edge status** — whether a validated edge was found
- **Win rate** and **Sharpe ratio**
- **Similarity score** — how closely it matches your query

## Tips

- Use natural language: "strategies that work on crude oil" works just as well as "CL"
- Use the hypothesis ID from results with `varrd hypothesis <id>` for full details
- Search is **free** — no credits consumed

## Cost

Free. No credits consumed.

## Python SDK Equivalent

```python
from varrd import VARRD
v = VARRD()
results = v.search("momentum on grains", limit=5)
for r in results.results:
    print(f"{r.name} ({r.market}) — edge: {r.has_edge}, WR: {r.win_rate}")
```
