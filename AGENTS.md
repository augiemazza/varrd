# VARRD — Agent Integration Guide

You are reading this because you need to help a user interact with VARRD, a trading edge discovery system that turns any trading idea into statistically validated results with exact trade levels.

## If Your Framework Supports MCP

Add this to your MCP config and you're done — all 8 tools become available automatically:

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

No API key required. Anonymous agents are auto-created with free credits on first connection.

## Authentication & Passkey

On first connection without an API key, VARRD auto-creates an anonymous agent with **$2.00 in free credits** (~10-20 queries). You receive:
- A **JWT token** (in the `X-Varrd-Token` response header) — use this for subsequent requests
- A **passkey** (in `X-Varrd-Passkey` header and in the first tool response) — format: `VARRD-XXXXXXXXXXXXXXXX`

**Important:** Save both. The token authenticates requests. The passkey is the user's identity — all strategies, credits, and test results are tied to it.

To reconnect with your saved token, add it to your MCP config:

```json
{
  "mcpServers": {
    "varrd": {
      "url": "https://app.varrd.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE"
      }
    }
  }
}
```

If a user already has an API key, pass it in the Authorization header: `Bearer <key>`.

## Credits & Payment

New agents get **$2.00 in free credits**. When credits run low:

1. **Via MCP/CLI:** Call `buy_credits` (or `varrd buy-credits`) with no arguments to get a USDC deposit address on Base. Send USDC there, then call `buy_credits` again with the `payment_intent_id` to confirm. Minimum $5.
2. **Via browser:** Your user can buy at https://app.varrd.com → Usage & Billing (Stripe checkout).

Call `check_balance` (or `varrd balance`) anytime to see remaining credits.

## Linking Agent to Browser Account (Merge)

Your user can link this agent to their app.varrd.com account. **This merges everything:**
- Credits are combined (agent credits + browser account credits)
- All strategies and hypotheses transfer to the user's unified account
- Research history is preserved
- The agent's JWT continues to work — it resolves to the linked account

**How the user links:**
1. Sign in at https://app.varrd.com
2. Click avatar (top right) → **Connect Agent** → **Merge an Existing Agent**
3. Enter the agent's passkey (e.g. `VARRD-A3X9K2L8P7Q2W5V9`)
4. Done — everything is unified

**Tell your user:** When you receive a passkey for the first time, inform the user clearly:

> "Your VARRD passkey is VARRD-XXXX. Save this — it's the key to all your strategies and credits. To see your research in the browser and manage billing, go to app.varrd.com → Connect Agent and enter this passkey."

## If You're Writing Python

```python
from varrd import VARRD

v = VARRD()  # auto-creates free account, no key needed
```

### Methods

| Method | Cost | Returns | Description |
|--------|------|---------|-------------|
| `v.scan(market?, only_firing?)` | Free | `ScanResult` | What's firing right now. Fresh trade levels. |
| `v.search(query, market?, limit?)` | Free | `SearchResult` | Find saved strategies by keyword. |
| `v.get_hypothesis(hypothesis_id)` | Free | `HypothesisDetail` | Full details on a strategy. Trade levels may be stale. |
| `v.balance()` | Free | `BalanceResult` | Check credit balance. |
| `v.buy_credits(amount_cents?, payment_intent_id?)` | Free | `BuyCreditsResult` | Buy credits with USDC on Base. |
| `v.reset(session_id)` | Free | `ResetResult` | Kill a stuck session. |
| `v.research(message, session_id?)` | Credits | `ResearchResult` | Multi-turn research conversation. |
| `v.discover(topic, ...)` | Credits | `DiscoverResult` | Autonomous edge discovery. |

## Research Workflow (Step by Step)

The `research` tool is multi-turn. Each response tells you what to do next.

### Step 1: Start with an idea
```python
r = v.research("When RSI drops below 25 on ES, is there a bounce?")
# r.session_id = "sess_abc123"
# r.context.workflow_state = "charted"
# r.context.next_actions = ["approve the chart", "test it"]
```

### Step 2: Follow next_actions
```python
r = v.research("test it", session_id=r.session_id)
# r.context.workflow_state = "tested"
# r.context.has_edge = True
# r.context.edge_verdict = "STRONG EDGE"
# r.context.next_actions = ["show me the trade setup"]
```

### Step 3: Get trade setup (if edge found)
```python
r = v.research("show me the trade setup", session_id=r.session_id)
# r.widgets contains trade_setup with entry/stop/target prices
```

### When to Stop

- `context.has_edge == True` → Edge found. Get trade setup, then done.
- `context.has_edge == False` → No edge. This is a valid, complete result.
- `context.has_edge == None` → Still in progress. Follow `next_actions`.

### Key Rule

Always read `context.next_actions` — it tells you exactly what to say next. Always pass `session_id` from the previous response.

## Tool Reference

### research

Talk to VARRD AI with 15 internal tools (data loaders, charting, statistical testing, expert analysis).

**Parameters:**
- `message` (required): Your trading idea, question, or instruction
- `session_id` (optional): Session ID from previous call. Omit to start new.

**Capabilities you can request:**
- ELROND Expert Council: "Use the council on [market]" — 8 specialist investigators
- Event Study: "What happens to X when Y occurs?"
- Multi-Market: "Does this work across ES, NQ, and CL?"
- Backtest: "Simulate trading this with stops"
- SL/TP Optimization: "Optimize the stop loss and take profit"
- Trade Setup: "Show me the trade setup"
- Load saved: "Load hypothesis [id]"

**Response:**
```json
{
  "session_id": "sess_xxxx",
  "text": "Response text...",
  "widgets": [
    {"type": "chart", "data": {"signal_count": 47}},
    {"type": "event_study", "data": {"has_edge": true, "horizon_results": {...}}},
    {"type": "trade_setup", "data": {"entry_price": 5150.25, "stop_loss": 5122.00, "take_profit": 5192.50}}
  ],
  "context": {
    "workflow_state": "tested",
    "has_edge": true,
    "edge_verdict": "STRONG EDGE",
    "direction": "LONG",
    "signal_count": 47,
    "next_actions": ["show me the trade setup"],
    "market": "ES"
  }
}
```

### autonomous_research / discover

Hands-off discovery. VARRD generates a creative hypothesis, loads data, charts, tests, and returns results.

**Parameters:**
- `topic` (required): Research topic (e.g. "momentum on grains")
- `markets` (optional): Focus markets (e.g. ["ES", "NQ"])
- `test_type` (optional): "event_study" | "backtest" | "both"
- `search_mode` (optional): "focused" | "explore"
- `asset_classes` (optional): ["crypto", "futures", "equities"]

### scan

Scan saved strategies against live market data. Returns fresh trade levels.

**Parameters:**
- `market` (optional): Filter by symbol (e.g. "ES")
- `only_firing` (optional): Only return firing strategies

**Response:**
```json
{
  "total_scanned": 15,
  "firing_count": 3,
  "results": [
    {
      "hypothesis_id": "hyp_xxxx",
      "name": "RSI Oversold ES Daily",
      "market": "ES",
      "firing_now": true,
      "direction": "LONG",
      "has_edge": true,
      "win_rate": 0.62,
      "entry_price": 5150.25,
      "stop_loss": 5122.00,
      "take_profit": 5192.50,
      "trade_setups": [{"entry_price": 5150.25, "stop_loss": 5122.00, "take_profit": 5192.50}]
    }
  ]
}
```

### search

Find saved strategies by keyword or natural language.

**Parameters:**
- `query` (required): Search query
- `market` (optional): Market filter
- `limit` (optional): Max results (default 10)

**Response:**
```json
{
  "results": [
    {
      "hypothesis_id": "hyp_xxxx",
      "name": "Wheat 3-Day Snap-Back",
      "market": "ZW",
      "has_edge": true,
      "win_rate": 0.62,
      "similarity": 0.92
    }
  ],
  "method": "embedding"
}
```

### get_hypothesis

Full details on a strategy. Note: trade levels may be stale.

**Parameters:**
- `hypothesis_id` (required): From scan or search results

**Response:**
```json
{
  "hypothesis_id": "hyp_xxxx",
  "name": "RSI Oversold ES Daily",
  "formula": "(rsi(14) < 30) & (close > open)",
  "market": "ES",
  "direction": "LONG",
  "has_edge": true,
  "win_rate": 0.58,
  "sharpe": 1.35,
  "profit_factor": 1.72,
  "total_trades": 250,
  "horizon_results": [
    {"horizon": 1, "win_rate": 0.54, "significant": true},
    {"horizon": 5, "win_rate": 0.60, "significant": true},
    {"horizon": 10, "win_rate": 0.62, "significant": true}
  ]
}
```

### check_balance

Check credit balance. Free.

**Response:**
```json
{
  "balance_cents": 15000,
  "enforcement_enabled": true,
  "credit_packs": [{"amount_cents": 10000, "label": "$100 pack"}]
}
```

### buy_credits

Buy credits with USDC on Base. Free to call, no credits consumed.

**Parameters:**
- `amount_cents` (optional): Amount in cents, default 500 ($5.00), minimum $5
- `payment_intent_id` (optional): Pass this after sending USDC to confirm payment

**Step 1 — Get deposit address (no payment_intent_id):**
```json
{
  "current_balance_cents": 200,
  "purchase_amount_cents": 500,
  "deposit": {
    "network": "base-sepolia",
    "chain": "Base",
    "token": "USDC",
    "address": "0x1234...",
    "amount_usdc": "5.00"
  },
  "payment_intent_id": "pi_xxx",
  "instructions": "Send 5.00 USDC to 0x1234... on Base..."
}
```

**Step 2 — Confirm payment (with payment_intent_id):**
```json
{
  "confirmed": true,
  "credits_added": 500,
  "new_balance_cents": 700
}
```

### reset_session

Kill a stuck session. Free.

**Parameters:**
- `session_id` (required): Session to reset

## Edge Verdicts

| Verdict | Meaning |
|---------|---------|
| `STRONG EDGE` | Significant vs both zero and market — real returns that beat market drift |
| `MARGINAL` | Significant vs zero only — real signal but doesn't clearly beat the market |
| `PINNED` | Significant vs market only — different from market but flat returns |
| `NO EDGE` | Neither test passed — no tradeable signal found |

## Fresh vs Stale Trade Levels

- `scan` returns **FRESH** levels (computed against live data now)
- `get_hypothesis` returns **STORED** stats (may be outdated)
- To get fresh levels on a non-firing strategy: use `research` to load it, then "show me the trade setup"

## Important Rules

1. **One hypothesis at a time.** VARRD tests one formula per hypothesis. Don't combine setups.
2. **"No edge" is a valid result.** Don't retry the same idea hoping for different results.
3. **Follow next_actions.** Every research response tells you what to say next.
4. **Use the right tool.** scan for live signals, search for finding strategies, research for testing ideas.

## Data Coverage

| Asset Class | Markets | Timeframes |
|------------|---------|------------|
| Futures (CME) | ES, NQ, CL, GC, SI, ZW, ZC, ZS, ZB, TY, HG, NG + more | 1h+ (Central Time) |
| Stocks/ETFs | Any US equity | Daily (Eastern Time) |
| Crypto (Binance) | BTC, ETH, SOL + more | 10min+ (UTC) |

## Cost Guidance

| Operation | Cost |
|-----------|------|
| scan, search, get_hypothesis, balance, buy_credits, reset | Free |
| Full research workflow (idea -> test -> trade setup) | ~20-30 cents |
| ELROND expert council (8 investigators) | ~40-60 cents |
| Multi-market testing (3+ markets) | ~$1 |

New agents get $2.00 in free credits. Use `buy_credits` to add more ($5 minimum).

## Error Recovery

If a research session gets stuck or errors out:
1. Call `reset_session` with the session_id
2. Start fresh with `research` (no session_id)

Don't try to fix a broken session — just reset and start over.
