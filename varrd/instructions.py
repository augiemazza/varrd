"""Agent instructions text for the CLI."""

AGENT_INSTRUCTIONS = """\
VARRD CLI — Instructions for AI Agents

You are using VARRD via the CLI (command-line interface). VARRD is an
institutional-grade quant research system that turns any trading idea
into statistically validated results with exact trade levels.

YOUR COMMANDS:

1. varrd research "<idea>"
   Multi-turn research conversation. VARRD auto-follows the workflow:
   idea -> chart -> test -> trade setup. Usually completes in 3-5 turns
   automatically. The CLI handles next_actions for you.

   Examples:
     varrd research "When RSI drops below 25 on ES, is there a bounce?"
     varrd research "Use the ELROND council on NQ"
     varrd research "When wheat drops 3 consecutive days after monthly highs, is there a snap-back?"

2. varrd discover "<topic>"
   Fully autonomous. VARRD generates a hypothesis, loads data, charts,
   tests, and gets trade setup if an edge is found. One command, one result.

   Examples:
     varrd discover "momentum on grains"
     varrd discover "mean reversion on crypto" --mode explore

3. varrd scan [--market ES] [--only-firing]
   What's firing RIGHT NOW. Scans all saved strategies against live data.
   Returns exact dollar entry/stop/target prices. Use --only-firing for
   actionable signals only.

4. varrd search "<query>" [--market ES] [--limit 10]
   Find saved strategies by keyword or natural language.
   Examples: "RSI oversold", "momentum strategies", "corn seasonal"

5. varrd hypothesis <id>
   Full details for a specific strategy. Formula, metrics, version history.
   NOTE: Trade levels may be STALE. Use scan for fresh levels.

6. varrd balance
   Check credit balance. Free, no credits consumed.

7. varrd buy-credits [--amount 500] [--confirm <payment_intent_id>]
   Buy credits with USDC on Base ($5 minimum). Two steps:
     Step 1: varrd buy-credits           -> get USDC deposit address
     Step 2: Send USDC to that address on Base network
     Step 3: varrd buy-credits --confirm <payment_intent_id>  -> confirm & receive credits
   Or buy at https://app.varrd.com (sign in -> Usage & Billing).

8. varrd reset <session_id>
   Reset a broken research session. Free.

IMPORTANT — FRESH vs STALE TRADE LEVELS:
- scan returns FRESH levels (computed against live data right now)
- hypothesis returns STORED stats (may be outdated)
- research auto-generates fresh trade setup when edge is found

HOW TO BE EFFICIENT:
- What's actionable right now? -> varrd scan --only-firing
- Find strategies by topic -> varrd search "query"
- Understand a strategy fully -> varrd hypothesis <id>
- Create NEW edges -> varrd research "your idea"
- Broad discovery -> varrd research "Use the ELROND council on ES"
- Hands-free discovery -> varrd discover "topic"

HOW TO ASK GREAT RESEARCH QUESTIONS:
- Be specific: "When wheat drops 3 consecutive days after new monthly
  highs, is there a snap-back?" not "find patterns in wheat"
- Cross-market: "Load TLT and CL. When bonds sell off for a week,
  does crude follow?"
- Expert council: "Use the ELROND council on ES" — 8 specialists
  (momentum, volatility, regime, chartist, flow, seasonality, quant,
  cross-market) each return calibrated formulas

DATA COVERAGE:
- Futures (CME): ES, NQ, CL, GC, SI, ZW, ZC, ZS, ZB, TY, HG, NG + more
  1h+ timeframes, Central Time
- Stocks/ETFs: Any US equity — daily only, Eastern Time
- Crypto (Binance): BTC, ETH, SOL + more — 10min+ timeframes, UTC

AUTHENTICATION:
  First call auto-creates an anonymous agent account. Credentials saved
  to ~/.varrd/credentials. Your passkey (VARRD-XXXX...) is printed once
  on first use — SAVE IT. You need it to reconnect and to link your
  research to a browser account.

CREDITS & PAYMENT:
  New accounts get $2.00 in free credits (~10-20 queries).
  When credits run low, use: varrd buy-credits
  This returns a USDC deposit address on Base. Send USDC there, then
  confirm with: varrd buy-credits --confirm <payment_intent_id>
  Or buy at https://app.varrd.com (sign in -> Usage & Billing).

LINKING AGENT TO BROWSER ACCOUNT:
  Your user can link this agent to their app.varrd.com account.
  This MERGES everything — credits combine, all strategies transfer,
  and research history is preserved.

  How to link:
    1. User signs in at https://app.varrd.com
    2. Clicks avatar -> Connect Agent -> Merge an Existing Agent
    3. Enters your passkey (VARRD-XXXX...)
    4. Done — agent and browser account are now unified.

  Tell your user their passkey when they ask about connecting.

MCP ALTERNATIVE:
  For richer integration, use the MCP (Model Context Protocol) server
  at https://app.varrd.com/mcp — it provides the same tools with
  streaming progress, better session management, and automatic
  instructions injection.
"""
