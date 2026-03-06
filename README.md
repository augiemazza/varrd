# VARRD — Trading Edge Discovery

[![PyPI](https://img.shields.io/pypi/v/varrd)](https://pypi.org/project/varrd/)
[![MCP](https://img.shields.io/badge/MCP-8_tools-blue)](https://app.varrd.com/mcp)
[![Transport](https://img.shields.io/badge/transport-Streamable_HTTP-green)](https://app.varrd.com/mcp)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**Institutional-grade quant research. Describe any trading idea in plain English, get statistically validated results with exact trade levels.**

Any AI can backtest a strategy. VARRD guarantees it was done right — with K-tracking, Bonferroni correction, OOS lock, lookahead detection, and 4 other integrity guardrails enforced at infrastructure level.

<a href="https://glama.ai/mcp/servers/@augiemazza/varrd">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@augiemazza/varrd/badge" alt="Varrd MCP server" />
</a>

---

## MCP Server — 8 Tools, 4 Prompts

**Endpoint:** `https://app.varrd.com/mcp`
**Transport:** Streamable HTTP (2025-03-26 spec)
**Auth:** Anonymous access with auto-provisioned credits. No API key required.

```json
{
  "mcpServers": {
    "varrd": {
      "transport": {
        "type": "streamable-http",
        "url": "https://app.varrd.com/mcp"
      }
    }
  }
}
```

Works with **Claude Desktop**, **Claude Code**, **Cursor**, and any MCP-compatible client.

### MCP Tools

| Tool | Cost | What It Does |
|------|------|--------------|
| `research` | ~$0.25 | Multi-turn quant research with VARRD AI. Orchestrates 15 internal tools (data loaders, charting, event studies, backtests, optimization). Follow `context.next_actions` each turn. |
| `autonomous_research` | ~$0.25 | AI discovers edges for you. Give it a topic, it generates hypotheses from its market knowledge base, runs the full pipeline, returns validated results. |
| `scan` | Free | Scan saved strategies against live market data. Returns exact dollar entry, stop-loss, and take-profit prices for every active signal. |
| `search` | Free | Find saved strategies by keyword or natural language. Returns matches ranked by relevance with win rate, Sharpe, edge status. |
| `get_hypothesis` | Free | Full details on any strategy: formula, entry/exit rules, win rate, Sharpe, profit factor, max drawdown, version history. |
| `check_balance` | Free | View credit balance and available credit packs. |
| `buy_credits` | Free | Buy credits with USDC on Base. Returns deposit address, then confirm after sending. |
| `reset_session` | Free | Kill a broken research session and start fresh. |

### MCP Prompts

| Prompt | Description |
|--------|-------------|
| `test-trading-idea` | Test any trading idea with real market data and statistical validation |
| `whats-firing-now` | Scan your validated strategies and show what's actively firing |
| `discover-edges` | Let VARRD's autonomous AI discover trading edges on a topic |
| `find-strategies` | Search your strategy library by keyword or concept |

---

## Quick Start — CLI

```bash
pip install varrd

# Research an idea (auto-follows the full workflow)
varrd research "When wheat drops 3 days in a row, is there a snap-back?"

# What's firing right now?
varrd scan --only-firing

# Search your saved strategies
varrd search "momentum on grains"

# Let VARRD discover edges autonomously
varrd discover "mean reversion on futures"

# Check credits
varrd balance
```

## Quick Start — Python

```python
from varrd import VARRD

v = VARRD()  # auto-creates free account

# What's firing right now?
signals = v.scan(only_firing=True)
for s in signals.results:
    print(f"{s.name}: {s.direction} {s.market} @ ${s.entry_price}")

# Research a trading idea
r = v.research("When RSI drops below 25 on ES, is there a bounce?")
r = v.research("test it", session_id=r.session_id)
print(r.context.has_edge)       # True / False
print(r.context.edge_verdict)   # "STRONG EDGE" / "NO EDGE" / etc.

# Get the trade setup
r = v.research("show me the trade setup", session_id=r.session_id)
```

---

## Authentication & Passkey

First use auto-creates an account. You'll receive a **passkey** (`VARRD-XXXXXXXXXXXXXXXX`) saved to `~/.varrd/credentials`.

```
  VARRD account created.
  Your passkey: VARRD-A3X9K2B7T4M8P1Q6
  Saved to: ~/.varrd/credentials
```

**Link to browser:** Go to [app.varrd.com](https://app.varrd.com), click "Link your AI agent", enter your passkey with an email and password. Your agent's strategies and credits merge into your account.

```python
v = VARRD(api_key="your-key")         # Python
```
```bash
varrd --key your-key scan              # CLI
export VARRD_API_KEY=your-key          # Environment variable
```

---

## What You Get Back

### Edge Found
```
STRONG EDGE: Statistically significant vs both zero and market baseline.
The pattern produces real returns that beat market drift.

  Direction: LONG
  Win Rate:  62%
  Sharpe:    1.45
  Trades:    247
  K:         3 (tests run on this hypothesis)

  Trade Setup:
    Entry:       $5,150.25
    Stop Loss:   $5,122.00
    Take Profit: $5,192.50
    Risk/Reward: 1.5:1
```

### No Edge
```
NO EDGE: Neither test passed — no tradeable signal found.

This is a valid result. You found out for 25 cents
instead of $25,000 in live losses.
```

---

## The Research Flow

```
Your idea (plain English)
    |
    v
  Chart pattern — see the actual signals on real price data
    |
    v
  You approve — sanity check before spending statistical power
    |
    v
  Statistical test — event study or backtest with proper controls
    |                 (K increments, fingerprints logged)
    v
  Edge verdict:  STRONG EDGE — beats zero AND beats market
                 MARGINAL    — beats zero, doesn't clearly beat market
                 NO EDGE     — no signal found
    |
    v
  Trade setup — exact dollar entry, stop-loss, take-profit
```

A typical session is 3-5 turns and costs ~$0.25.

## 8 Statistical Guardrails (Infrastructure-Enforced)

| Guardrail | What It Does |
|-----------|--------------|
| **K-Tracking** | Counts every test. 50 variations = higher significance bar. |
| **Bonferroni Correction** | Multiple comparison penalty, automatic. |
| **OOS Lock** | Out-of-sample is sacred. One shot. Locked forever. |
| **Lookahead Detection** | Catches formulas that accidentally use future data. |
| **Tools Calculate, AI Interprets** | AI never fabricates a number. Every stat from real data. |
| **Chart > Approve > Test** | Must see and approve pattern before testing. |
| **Fingerprint Deduplication** | Can't retest same formula/market/horizon twice. |
| **No Post-OOS Optimization** | Parameters locked after OOS validates. |

## Data Coverage

| Asset Class | Markets | Timeframes |
|------------|---------|------------|
| **Futures** (CME) | ES, NQ, CL, GC, SI, ZW, ZC, ZS, ZB, TY, HG, NG + 20 more | 1h and above |
| **Stocks/ETFs** | Any US equity | Daily |
| **Crypto** (Binance) | BTC, ETH, SOL + more | 10min and above |

15,000+ instruments total.

## Pricing

- **$2 free** on signup — enough for 6-8 full research sessions
- **Research:** ~$0.20-0.30 per complete workflow
- **ELROND council** (8 expert investigators): ~$0.40-0.60
- **Multi-market** (3+ markets): up to ~$1
- **Free tools:** scan, search, get_hypothesis, check_balance, buy_credits, reset_session
- **Credit packs:** $5 / $20 / $50 via Stripe
- Credits never expire

---

## Examples

See [`examples/`](examples/):

- [`quick_start.py`](examples/quick_start.py) — 5 lines to get started
- [`scan_portfolio.py`](examples/scan_portfolio.py) — Scan all strategies, show what's firing
- [`research_idea.py`](examples/research_idea.py) — Full multi-turn research workflow
- [`multi_idea_loop.py`](examples/multi_idea_loop.py) — Test many ideas in a loop
- [`mcp_config.json`](examples/mcp_config.json) — MCP config for Claude Desktop

## For AI Agents

See [`AGENTS.md`](AGENTS.md) for a structured guide with complete tool reference, response formats, and integration patterns.

---

## Links

- **Web app:** [app.varrd.com](https://app.varrd.com)
- **Website:** [varrd.com](https://www.varrd.com)
- **MCP endpoint:** `https://app.varrd.com/mcp`
- **MCP Registry:** [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io)