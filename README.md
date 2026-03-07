# VARRD

[![PyPI](https://img.shields.io/pypi/v/varrd)](https://pypi.org/project/varrd/)
[![MCP](https://img.shields.io/badge/MCP-8_tools-blue)](https://app.varrd.com/mcp)
[![Transport](https://img.shields.io/badge/transport-Streamable_HTTP-green)](https://app.varrd.com/mcp)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**Turn any trading idea into a statistically validated edge — or find out it doesn't work for $0.25.**

```bash
pip install varrd
```

## Ask it anything

```bash
varrd research "Does buying SPY after a 3-day losing streak actually work?"

varrd research "When VIX spikes above 30, is there a bounce in ES?"

varrd research "Is there a seasonal pattern in wheat before harvest?"

varrd research "What happens to gold when the dollar drops 3 days straight?"

varrd research "Does Bitcoin rally after the halving?"

varrd research "When crude oil drops 5% in a week, what happens next?"
```

Every question gets real data, a chart with signals marked, a statistical test, and a definitive answer.

## What you get back

### Edge found
```
STRONG EDGE — Statistically significant vs both zero and market baseline.

  Direction:    LONG
  Win Rate:     62%
  Sharpe:       1.45
  Signals:      247

  Trade Setup:
    Entry:       $5,150.25
    Stop Loss:   $5,122.00
    Take Profit: $5,192.50
    Risk/Reward: 1:1.5
```

### No edge
```
NO EDGE — Neither test passed. No tradeable signal found.

You found out for 25 cents instead of $25,000 in live losses.
```

Both are valuable results.

---

## How it works

```
Your idea (plain English)
     ↓
  Load real market data — stocks, futures, crypto
     ↓
  Chart the pattern — see actual signals on price history
     ↓
  You approve — sanity check before spending statistical power
     ↓
  Statistical test — event study with proper controls
     ↓
  Verdict:  STRONG EDGE / MARGINAL / NO EDGE
     ↓
  Trade setup — exact entry, stop-loss, take-profit in dollars
```

A typical session is 3–5 turns and costs ~$0.25.

---

## Quick start — Python

```python
from varrd import VARRD

v = VARRD()  # auto-creates free account, $2 in credits

# Research a trading idea
r = v.research("When RSI drops below 25 on ES, is there a bounce?")
r = v.research("test it", session_id=r.session_id)

print(r.context.edge_verdict)  # "STRONG EDGE" / "NO EDGE"

# Get exact trade levels
r = v.research("show me the trade setup", session_id=r.session_id)
```

```python
# What's firing right now across all your strategies?
signals = v.scan(only_firing=True)
for s in signals.results:
    print(f"{s.name}: {s.direction} {s.market} @ ${s.entry_price}")
```

```python
# Let VARRD discover edges autonomously
result = v.discover("mean reversion on futures")
print(result.edge_verdict, result.market, result.win_rate)
```

## Quick start — CLI

```bash
# Full research workflow (auto-follows chart → test → trade setup)
varrd research "When wheat drops 3 days in a row, is there a snap-back?"

# What's firing right now?
varrd scan --only-firing

# Search saved strategies
varrd search "momentum on grains"

# Let VARRD discover edges on its own
varrd discover "mean reversion on futures"
```

---

## Use with AI agents

### Claude Desktop / Claude Code / Cursor

Add to your MCP config — no API key needed:

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

Then just ask: *"Is there a pattern when gold spikes after a Fed rate decision?"*

### CrewAI

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Trading Researcher",
    goal="Find statistically validated trading edges",
    backstory="You are a quantitative researcher who tests trading ideas rigorously.",
    mcps=[{"type": "streamable-http", "url": "https://app.varrd.com/mcp"}]
)

task = Task(
    description="Research whether RSI oversold conditions on ES lead to a bounce within 5 days.",
    agent=researcher,
    expected_output="Edge verdict with trade setup if edge is found."
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
```

### LangChain / LangGraph

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-20250514")

async with MultiServerMCPClient({
    "varrd": {"url": "https://app.varrd.com/mcp", "transport": "streamable_http"}
}) as client:
    agent = create_react_agent(model, client.get_tools())
    result = await agent.ainvoke({"messages": [
        {"role": "user", "content": "Does gold rally when the dollar drops 3 days in a row?"}
    ]})
```

### Raw MCP (any client)

```bash
# Any MCP-compatible client can connect to:
https://app.varrd.com/mcp
# Transport: Streamable HTTP | No auth required | $2 free credits
```

---

## 8 statistical guardrails (infrastructure-enforced)

Every test runs through these automatically. You can't skip them.

| Guardrail | What It Prevents |
|-----------|-----------------|
| **K-Tracking** | Tests 50 variations of the same idea? Significance bar goes up automatically. |
| **Bonferroni Correction** | Multiple comparison penalty. No p-hacking. |
| **OOS Lock** | Out-of-sample is one shot. Can't re-run after seeing results. |
| **Lookahead Detection** | Catches formulas that accidentally use future data. |
| **Tools Calculate, AI Interprets** | Every number comes from real data. AI never fabricates stats. |
| **Chart → Approve → Test** | You see and approve the pattern before spending statistical power. |
| **Fingerprint Dedup** | Can't retest the same formula/market/horizon twice. |
| **No Post-OOS Optimization** | Parameters lock after out-of-sample validates. |

---

## Data coverage

| Asset Class | Markets | Timeframes |
|------------|---------|------------|
| **Futures** (CME) | ES, NQ, CL, GC, SI, ZW, ZC, ZS, ZB, TY, HG, NG + 20 more | 1h and above |
| **Stocks / ETFs** | Any US equity | Daily |
| **Crypto** (Binance) | BTC, ETH, SOL + more | 10min and above |

15,000+ instruments total.

## MCP tools

| Tool | Cost | What It Does |
|------|------|--------------|
| `research` | ~$0.25 | Multi-turn quant research. Orchestrates 15 internal tools. |
| `autonomous_research` | ~$0.25 | AI discovers edges for you. Give it a topic, get validated results. |
| `scan` | Free | Scan strategies against live data. Fresh entry/stop/target prices. |
| `search` | Free | Find strategies by keyword or natural language. |
| `get_hypothesis` | Free | Full details on any strategy. |
| `check_balance` | Free | View credits and available packs. |
| `buy_credits` | Free | Buy credits with USDC on Base or Stripe. |
| `reset_session` | Free | Kill a broken session and start fresh. |

## Pricing

- **$2 free** on signup — enough for 6–8 research sessions
- **Research:** ~$0.20–0.30 per idea tested
- **Discovery** (autonomous): ~$0.20–0.30
- **ELROND council** (8 expert investigators): ~$0.40–0.60
- **Multi-market** (3+ markets): ~$1
- **Scan, search, balance:** Always free
- **Credit packs:** $5 / $20 / $50 via Stripe
- Credits never expire

---

## Examples

See [`examples/`](examples/) for runnable scripts:

- [`quick_start.py`](examples/quick_start.py) — 5 lines to scan all strategies
- [`research_idea.py`](examples/research_idea.py) — Full multi-turn research workflow
- [`multi_idea_loop.py`](examples/multi_idea_loop.py) — Test many ideas in a loop
- [`scan_portfolio.py`](examples/scan_portfolio.py) — Portfolio scan with trade levels
- [`mcp_config.json`](examples/mcp_config.json) — MCP config for Claude Desktop / Cursor

## For AI agent builders

See [`AGENTS.md`](AGENTS.md) for the complete integration guide — tool reference, response formats, authentication, and workflow patterns.

---

## Links

- **Web app:** [app.varrd.com](https://app.varrd.com)
- **Website:** [varrd.com](https://www.varrd.com)
- **MCP endpoint:** `https://app.varrd.com/mcp`
- **PyPI:** [pypi.org/project/varrd](https://pypi.org/project/varrd/)
