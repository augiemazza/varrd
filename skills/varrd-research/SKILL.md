---
name: varrd-research
description: The core VARRD research tool — talk to a state-of-the-art quant AI to research, chart, test, optimize, and trade any market idea. Use when the user wants to test a trading hypothesis, find edges, or validate a strategy with real market data.
version: 1.0.0
tools: ["Bash"]
homepage: https://varrd.com
metadata: {"openclaw": {"requires": {"bins": ["varrd"]}, "emoji": "📊"}}
---

# VARRD Research — The Main Event

This is the core of VARRD. Everything else — scanning, searching, checking balances — those are environmental functions that support what happens here. This tool is how you talk to VARRD's AI to do real quantitative research.

Through this single interface, VARRD's AI can load market data, build indicators, chart patterns, run rigorous statistical tests, optimize stop-loss and take-profit levels, compute the best way to trade an edge, generate ideas through its expert council, and deliver exact dollar trade setups. It has 15 internal tools and knows how to use them.

## Command

```bash
varrd research "<your trading idea>"
```

## The Typical Flow

A research session follows a natural progression:

**1. You bring an idea.** This can be a specific hypothesis ("When RSI drops below 25 on ES, is there a bounce?"), a broad question ("What happens to crude when weekly inventory draws exceed expectations?"), or a request for idea generation ("Use the ELROND council on NQ" — 8 specialist investigators each trained on different systematic trading frameworks).

**2. VARRD charts the pattern.** It loads real market data, builds the indicators, evaluates the formula, and shows you exactly where the pattern fired on a real price chart with signal count. You review it — does this look right? Are the signals where you'd expect them?

**3. You validate or tweak.** If the chart looks good, you approve it for testing. If something's off, you refine the formula — adjust thresholds, add filters, change the market or timeframe. Iterate until you're satisfied with what you're about to test.

**4. VARRD recommends and runs the test.** Based on your setup, VARRD recommends the best testing approach. There are several types:

| Test Type | What It Does | When It's Used |
|-----------|-------------|----------------|
| **Single Event Study** | Forward return analysis on one market at multiple time horizons | Default for one market — "does price go up or down after this signal?" |
| **Parallel Event Study** | Same pattern tested independently on 2-5 markets, per-market results | "Does this work on ES, NQ, and CL?" |
| **Batch Event Study** | Same pattern pooled across 6+ markets into one aggregate result | Broad screen — "does this work across all metals?" |
| **Backtest Strategy** | Full simulation with stop-loss, take-profit, equity curve, drawdown, in-sample and sacred one-shot out-of-sample validation | When you want to simulate actually trading it as a system |

There's also portfolio backtesting for combining multiple strategies into a book, but that follows the same mechanics as strategy backtesting.

**5. You see the results and decide what's next.**

- **Edge found** — ask for the trade setup to get exact entry, stop-loss, and take-profit prices computed against current market data
- **No edge but close** — tweak the formula, try different horizons, adjust entry timing, and test again
- **No edge, move on** — start a new hypothesis and keep exploring. This is the most common outcome and it's valuable — you ruled something out for 25 cents instead of $25,000 in live losses

The cycle continues: idea → chart → validate → test → interpret → next idea. Each round gets you closer to a real edge or confirms there isn't one.

## Statistical Integrity (Behind the Scenes)

While you research, VARRD enforces institutional-grade statistical guardrails automatically:

- **K-tracking** — every test you run is counted, and the significance threshold rises accordingly. No free looks.
- **Bonferroni correction** — automatic penalty for multiple comparisons. Testing 5 horizons costs more statistical power than testing 1.
- **Fingerprint deduplication** — you can't re-test the exact same formula/market/horizon combination twice. The system remembers.
- **Out-of-sample lock** — OOS validation is a sacred one-shot test. Once used, it's locked forever. No peeking, no re-running.
- **Lookahead detection** — catches formulas that accidentally use future data.
- **Chart-before-test** — you must see and approve the pattern before spending statistical power on it.

These are the same controls that institutional quant firms enforce internally. They run identically whether you're testing interactively or running autonomous overnight research. You don't configure them. You can't skip them. That's the point.

## Edge Verdicts

| Verdict | Meaning |
|---------|---------|
| **STRONG EDGE** | Significant vs both zero and market baseline — real returns that also beat what the market does on its own |
| **MARGINAL** | Significant vs zero only — there's a real signal, but it doesn't clearly beat the market's natural drift |
| **PINNED** | Significant vs market only — returns are flat but meaningfully different from market behavior (useful for hedging or relative value) |
| **NO EDGE** | Neither test passed — no tradeable signal found |

## Examples

```bash
varrd research "When RSI drops below 25 on ES, is there a bounce?"
varrd research "Use the ELROND council on NQ"
varrd research "When wheat drops 3 consecutive days after monthly highs, is there a snap-back?"
varrd research "Load TLT and CL. When bonds sell off for a week, does crude follow?"
varrd research "What happens to gold when the VIX spikes above 30?"
```

## Reading the Output

Each turn prints response text and any widgets (charts, test results, trade setups). Key context fields:

- `has_edge: True` — edge found, get the trade setup, done
- `has_edge: False` — no edge, valid complete result
- `has_edge: None` — still in progress, keep going
- `next_actions` — what to say next (the CLI follows these automatically)
- `edge_verdict` — STRONG EDGE, MARGINAL, PINNED, or NO EDGE

## Tips

- Be specific: "When wheat drops 3 consecutive days after new monthly highs, is there a snap-back?" beats "find patterns in wheat"
- Cross-market ideas work: "Load TLT and CL. When bonds sell off for a week, does crude follow?"
- Use the ELROND council for idea generation — 8 specialists (momentum, volatility, regime, chartist, flow, seasonality, quant, cross-market) each return calibrated formulas
- "No edge" is the most common outcome and it's valuable. Move on, test the next idea.
- Use `--max-turns 20` for complex research that needs more steps

## Cost

~20-30 cents per complete workflow (idea through validated trade setup). ELROND council calls cost ~40-60 cents. Multi-market (3+ markets) can reach ~$1.

## Python SDK Equivalent

```python
from varrd import VARRD
v = VARRD()
r = v.research("When RSI drops below 25 on ES, is there a bounce?")
r = v.research("test it", session_id=r.session_id)
r = v.research("show me the trade setup", session_id=r.session_id)
```

## MCP Alternative

For richer integration with streaming progress and automatic instructions, use the MCP server at `https://app.varrd.com/mcp`.
