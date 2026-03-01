# VARRD — Trading Edge Discovery

**You can ask any AI to backtest a trading strategy. It will happily do it. The results will look great. And they will be wrong.**

Not wrong like "off by a little." Wrong like "the edge never existed and you'll find out with real money."

Quantitative testing is full of invisible landmines — dozens of statistical biases, penalties, and correctional procedures that determine whether a result is real or an artifact of how you tested it. Things like what must be penalized when you test multiple variations. What can and can't be tested on the same data. When a result that looks significant is actually meaningless. How to tell the difference between a strategy that works and a strategy that just happened to overlap with a bull market. Why looking at your out-of-sample results "just to check" permanently contaminates them.

Professional quants at top firms spend years learning these rules. Most of them still get it wrong sometimes. When you ask an AI to "backtest this strategy," it skips all of it. Not maliciously — it just doesn't know what it doesn't know. And neither do you. That's the problem.

**VARRD is a quant research system built on the statistical framework that institutional firms use internally.** Every bias accounted for. Every penalty applied. Every checkpoint enforced — not by documentation or best practices, but by the structure of the system itself. You literally cannot skip the steps that need to happen, because the workflow won't let you.

You bring a messy idea in plain English. VARRD does the math and gives you a verdict: **edge or no edge** — with exact entry, stop-loss, and take-profit prices. If the edge is real, you'll know. If it's not, you'll know that too — and you found out for 25 cents instead of $25,000 in live losses.

```
pip install varrd
```

---

## Why This Matters

There are things in quantitative testing that are near-invisible to the human eye. Not complex — invisible. The kind of stuff that a PhD statistician catches on instinct after 15 years, that a trader learns the hard way after blowing up twice, that a quant at Citadel takes for granted but never explains because it's just "how things are done."

Things like:
- Why testing 5 RSI thresholds and picking the best one isn't the same as testing 1
- Why a strategy that "beats the market" might actually be *behind* the market
- Why every formula tweak is a statistical test, whether you think of it that way or not
- Why your out-of-sample validation becomes worthless the moment you use it to make a decision
- Why the number of observations matters in ways that aren't obvious
- Why significance at one horizon says nothing about significance at another

These aren't advanced topics. They're table stakes. And if even one of them is handled wrong, the whole result is unreliable.

VARRD handles all of them. Automatically. Invisibly. You don't configure anything. You don't set penalty parameters. You don't choose which corrections to apply. The system knows what needs to happen at each stage of research and it does it — the same way a quant at a top firm would, except it never forgets a step and it never cuts corners because it's 4pm on a Friday.

**You don't need to know what any of this means. That's the point.**

---

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

## Quick Start — CLI

```bash
# Check what's actionable now
varrd scan --only-firing

# Research an idea (auto-follows the workflow)
varrd research "When wheat drops 3 days in a row, is there a snap-back?"

# Search your saved strategies
varrd search "momentum on grains"

# Let VARRD discover edges autonomously
varrd discover "mean reversion on futures"

# Check credits
varrd balance
```

## Quick Start — MCP (Claude Desktop / Claude Code / Cursor)

Add to your MCP config:

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

That's it. Your AI can now scan strategies, research ideas, and get trade setups — with all the statistical guardrails enforced automatically.

---

## Authentication & Your Passkey

The first time you use VARRD (via Python, CLI, or MCP), an account is automatically created for you. You'll receive a **passkey** — a unique key that looks like `VARRD-XXXXXXXXXXXXXXXX`. This is your identity.

```
  VARRD account created.
  Your passkey: VARRD-A3X9K2B7T4M8P1Q6
  Saved to: ~/.varrd/credentials

  Keep this passkey safe. To see your strategies in the
  browser, go to app.varrd.com and link your agent using
  this passkey with an email and password.
```

**How it works:**

1. **First use** — account auto-created, passkey saved to `~/.varrd/credentials`, free credits granted
2. **Ongoing use** — all your strategies, test results, and credits are tied to this passkey
3. **Link to browser** — go to [app.varrd.com](https://app.varrd.com), click "Link your AI agent", enter your passkey with an email and password. Your agent's strategies and credits merge into your account.
4. **After linking** — sign in with email/password to see everything your agent discovered, or keep using the CLI/API with the same passkey. Both work.

**Keep your passkey safe.** It's the key to your strategies. If you lose it before linking to an email, your work is gone. After linking, your email and password are your login — the passkey is just for the initial connection.

You can also pass a key explicitly:

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

This is a valid result. Knowing what doesn't work saves you money.
Most ideas don't have edges. That's normal and that's the whole point —
you found out for 25 cents instead of $25,000 in live losses.
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
    |
    v
  Edge verdict:  STRONG EDGE — beats zero AND beats market
                 MARGINAL    — beats zero, doesn't clearly beat market
                 NO EDGE     — no signal found
    |
    v
  Trade setup — exact dollar entry, stop-loss, take-profit
```

A typical session is 3-5 turns. Each response includes `context.next_actions` (what to say next) and `context.has_edge` (when you're done).

## Tools

| Tool | Cost | Description |
|------|------|-------------|
| `scan` | Free | Scan strategies against live data. What's firing right now? |
| `search` | Free | Find saved strategies by keyword or natural language. |
| `get_hypothesis` | Free | Full details on a specific strategy. |
| `balance` | Free | Check credit balance. |
| `reset` | Free | Kill a stuck research session. |
| `research` | ~20-30c | Multi-turn research with VARRD AI. You drive the conversation. |
| `discover` | ~20-30c | Autonomous edge discovery. VARRD drives. |

## Data Coverage

| Asset Class | Markets | Timeframes |
|------------|---------|------------|
| **Futures** (CME) | ES, NQ, CL, GC, SI, ZW, ZC, ZS, ZB, TY, HG, NG + more | 1h and above |
| **Stocks/ETFs** | Any US equity | Daily |
| **Crypto** (Binance) | BTC, ETH, SOL + more | 10min and above |

## Pricing

- **Free tools:** scan, search, get_hypothesis, balance, reset
- **Research:** ~20-30 cents per complete workflow (idea through trade setup)
- **ELROND council** (8 expert investigators): ~40-60 cents
- **Multi-market** (3+ markets): can reach ~$1
- New accounts get free credits to start

---

## Examples

See the [`examples/`](examples/) directory:

- [`quick_start.py`](examples/quick_start.py) — 5 lines to get started
- [`scan_portfolio.py`](examples/scan_portfolio.py) — Scan all strategies, show what's firing
- [`research_idea.py`](examples/research_idea.py) — Full multi-turn research workflow
- [`multi_idea_loop.py`](examples/multi_idea_loop.py) — Test many ideas in a loop
- [`mcp_config.json`](examples/mcp_config.json) — MCP config for Claude Desktop

## For AI Agents

See [`AGENTS.md`](AGENTS.md) for a structured guide with complete tool reference, response formats, and integration patterns. Designed to be read by LLMs.

---

## Links

- **Web app:** [app.varrd.com](https://app.varrd.com)
- **Landing page:** [varrd.com](https://varrd.com)
- **MCP endpoint:** `https://app.varrd.com/mcp`
