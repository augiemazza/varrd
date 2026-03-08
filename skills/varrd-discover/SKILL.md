---
name: varrd-discover
description: Autonomous edge discovery — VARRD generates, tests, and validates trading hypotheses hands-free. Use when the user wants the AI to find trading edges on its own given a topic or market.
version: 1.0.0
tools: ["Bash"]
homepage: https://varrd.com
metadata: {"openclaw": {"requires": {"bins": ["varrd"]}, "emoji": "🔍"}}
---

# VARRD Discover — Autonomous Edge Discovery

Use this skill when a user wants VARRD to autonomously discover trading edges without driving the conversation step-by-step.

## Command

```bash
varrd discover "<topic>"
```

## How It Works

Give it a topic and VARRD handles everything: generates a creative hypothesis from its market structure knowledge base, loads data, charts the pattern, runs statistical tests, and returns the trade setup if an edge is found. One command, one result.

Each call tests ONE hypothesis through the full pipeline. Call again for another — VARRD uses tangential idea propagation, so related concepts branch out from your seed idea.

## Examples

```bash
varrd discover "momentum on grains"
varrd discover "mean reversion on crypto" --mode explore
varrd discover "volatility clustering on ES" --markets ES NQ
varrd discover "seasonal patterns in energy" --test-type backtest
```

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--mode` | `focused`, `explore` | `focused` | focused = stay close to topic, explore = creative freedom |
| `--markets` | e.g. `ES NQ CL` | auto | Focus on specific markets |
| `--test-type` | `event_study`, `backtest`, `both` | `event_study` | Type of statistical test |

## When to Use discover vs research

| Scenario | Use |
|----------|-----|
| You have a specific idea to test | `varrd research "your idea"` |
| You want broad exploration of a space | `varrd discover "topic"` |
| You want control over each step | `varrd research` |
| You want hands-free, one command | `varrd discover` |
| Running many hypotheses at scale | `varrd discover` in a loop |

## Reading the Output

The result includes:
- **Edge verdict:** STRONG EDGE / MARGINAL / NO EDGE
- **Statistics:** Win rate, Sharpe ratio, signal count
- **Trade setup** (if edge found): exact entry, stop-loss, take-profit prices
- **Hypothesis ID:** saved to your library for later scanning

## Tips

- Use `--mode explore` for more creative, tangential ideas
- Each call takes 30-120 seconds — it's running the full pipeline
- Run in a loop to test many hypotheses: `for topic in "momentum" "mean reversion" "breakouts"; do varrd discover "$topic"; done`
- All validated hypotheses are saved — use `varrd scan` later to see what's firing

## Cost

~20-30 cents per discovery call.

## Python SDK Equivalent

```python
from varrd import VARRD
v = VARRD()
result = v.discover("mean reversion on crypto", search_mode="explore")
print(result.has_edge, result.edge_verdict)
```
