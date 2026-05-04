"""Agent instructions text for the CLI."""

AGENT_INSTRUCTIONS = """\
VARRD CLI — Instructions for AI Agents

You are using VARRD, the governed live edge layer. VARRD maintains a
library of statistically validated trading edges running 24/7 against
live market data — and lets you test your own ideas with institutional-
grade methodology.

YOUR COMMANDS:

1. varrd edges [--depth 0|1|2] [--edge-id ID] [--market ES] [--status firing]
               [--direction LONG|SHORT] [--timeframe daily] [--asset-class futures]
   Browse VARRD's validated edge library. The main command.
     depth=0 (free):  Which markets have edges firing right now
     depth=1 ($0.50): 15-min snapshot — direction, win rate, EV, stops, entry date
     depth=2 ($1):    Full audit trail — methodology, performance, formula, interactive view

   Filters: market, status (firing/pending/active), direction (LONG/SHORT),
   timeframe (60min/120min/240min/360min/480min/daily/weekly),
   asset_class (futures/equities/crypto)

2. varrd research "<idea>"
   Multi-turn research conversation. VARRD auto-follows the workflow:
   idea -> chart -> test -> trade setup. Usually completes in 3-5 turns.

   Examples:
     varrd research "When RSI drops below 25 on ES, is there a bounce?"
     varrd research "What happens to gold when silver ETFs make 100-day new lows?"
     varrd research "Use the ELROND council on NQ"

3. varrd discover "<topic>"
   Fully autonomous. VARRD generates a hypothesis, loads data, charts,
   tests, and gets trade setup if an edge is found. One command, one result.

   Examples:
     varrd discover "momentum on grains"
     varrd discover "mean reversion on crypto" --mode explore

4. varrd briefing
   Personalized market news briefing based on your validated edge library.
   Connects today's headlines to your specific positions and edges.
   Requires 5+ strong edges in your library.

5. varrd search "<query>" [--market ES] [--limit 10]
   Find your saved strategies by keyword or natural language.

6. varrd hypothesis <id>
   Full details for one of your own strategies.

7. varrd balance
   Check credit balance. Free, no credits consumed.
   Also auto-detects completed payments — call after paying to confirm.

8. varrd buy-credits [--amount 500]
   Buy credits ($5 minimum). Returns a Stripe Checkout link for card payment.
   After your user pays, call varrd balance to confirm credits were added.
   Pass --confirm <payment_intent_id> for USDC on Base (crypto, autonomous).

9. varrd reset <session_id>
   Reset a broken research session. Free.

EDGE STATUSES:
- FIRING:  Signal confirmed. Enter at next bar open. Actionable now.
- PENDING: Bar hasn't closed yet. Signal may fire when it does. Don't act.
- ACTIVE:  Already in a trade from a previous signal. Entry already happened.

TWO TEST TYPES:
- EVENT STUDY: Statistical forward returns over N bars. Entry at next bar open,
  exit after N bars at close. The edge is probabilistic.
- BACKTEST: Simulated trading with stop-loss and take-profit. Entry at next bar
  open, exit when SL/TP hits or max hold.

HOW TO BE EFFICIENT:
- What's firing right now? -> varrd edges
- Stats + trade levels? -> varrd edges --depth 1
- Full methodology on one edge? -> varrd edges --depth 2 --edge-id <id>
- Only shorts? -> varrd edges --depth 1 --direction SHORT
- Only equities? -> varrd edges --depth 1 --asset-class equities
- Test YOUR idea? -> varrd research "your idea"
- Hands-free discovery -> varrd discover "topic"
- Morning briefing -> varrd briefing

DATA COVERAGE:
- Futures (CME): ES, NQ, CL, GC, SI, ZW, ZC, ZS, ZB, TY, HG, NG + more
  1h through weekly, back to 1985
- Stocks/ETFs: Any US equity (12,600+ tickers) — 1h through weekly
- Crypto (Binance): BTC, ETH, SOL + more — 1h through weekly

CREDITS & PAYMENT:
  Sign up at app.varrd.com to get $2.00 in free credits.
  MCP-only agents start with $0 — use buy-credits to add funds.
  varrd edges depth=0, search, hypothesis, balance are FREE.
  varrd edges depth=1 costs $0.50, depth=2 costs $1/edge or $5/all.
  Research costs ~$0.25/query. Autonomous discovery ~$1/idea.

AUTHENTICATION:
  First call auto-creates an agent identity. Credentials saved to
  ~/.varrd/credentials. Your passkey (VARRD-XXXX...) is printed once
  on first use — SAVE IT.

  To get $2 free credits and link to a browser account:
    1. Sign up at https://app.varrd.com
    2. Click avatar -> Connect Agent -> Merge an Existing Agent
    3. Enter your passkey
    4. Credits combine, everything merges.

MCP ALTERNATIVE:
  For richer integration, use the MCP server at https://app.varrd.com/mcp
  — streaming progress, 9 tools, automatic instructions, session management.
"""
