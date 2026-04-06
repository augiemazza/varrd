"""VARRD CLI — trading edge discovery from the terminal.

Usage:
    varrd balance
    varrd buy-credits [--amount 500] [--confirm <payment_intent_id>]
    varrd scan [--market ES] [--only-firing]
    varrd search "momentum strategies" [--limit 10]
    varrd research "When RSI drops below 25 on ES, is there a bounce?"
    varrd discover "mean reversion on futures" [--mode explore]
    varrd hypothesis <id>
    varrd reset <session_id>
    varrd auth status
    varrd auth clear
"""

from __future__ import annotations

import argparse
import io
import sys

# Force UTF-8 output on Windows (hypothesis names contain unicode)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from varrd.client import VARRD, AuthError, PaymentRequired, RateLimited, VARRDError
from varrd.display import (
    display_balance,
    display_briefing,
    display_discover,
    display_hypothesis,
    display_research,
    display_reset,
    display_scan,
    display_search,
    BOLD,
    DIM,
    GREEN,
    RED,
    RESET,
    YELLOW,
)


def _client(args) -> VARRD:
    """Create a VARRD client from CLI args."""
    api_key = getattr(args, "key", None)
    base_url = getattr(args, "url", None) or "https://app.varrd.com"
    return VARRD(api_key=api_key, base_url=base_url)


def _handle_error(e: Exception):
    """Print a friendly error message and exit."""
    if isinstance(e, PaymentRequired):
        print(f"\n  {RED}{BOLD}Credits depleted!{RESET}")
        print(f"  Purchase more at https://app.varrd.com")
        sys.exit(1)
    elif isinstance(e, AuthError):
        print(f"\n  {RED}Authentication failed.{RESET}")
        print(f"  Set VARRD_API_KEY or run: varrd auth status")
        sys.exit(1)
    elif isinstance(e, RateLimited):
        print(f"\n  {YELLOW}Rate limited. Wait and retry.{RESET}")
        sys.exit(1)
    elif isinstance(e, VARRDError):
        print(f"\n  {RED}Error: {e}{RESET}")
        sys.exit(1)
    else:
        raise e


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_balance(args):
    try:
        v = _client(args)
        result = v.balance()
        display_balance(result)
    except Exception as e:
        _handle_error(e)


def cmd_scan(args):
    try:
        v = _client(args)
        result = v.scan(
            market=getattr(args, "market", None),
            only_firing=getattr(args, "only_firing", False),
        )
        display_scan(result)
    except Exception as e:
        _handle_error(e)


def cmd_search(args):
    try:
        v = _client(args)
        result = v.search(
            query=args.query,
            market=getattr(args, "market", None),
            limit=getattr(args, "limit", 10),
        )
        display_search(result)
    except Exception as e:
        _handle_error(e)


def cmd_hypothesis(args):
    try:
        v = _client(args)
        result = v.get_hypothesis(args.id)
        display_hypothesis(result)
    except Exception as e:
        _handle_error(e)


def cmd_reset(args):
    try:
        v = _client(args)
        result = v.reset(args.session_id)
        display_reset(result)
    except Exception as e:
        _handle_error(e)


def cmd_buy_credits(args):
    """Buy credits with USDC on Base."""
    try:
        v = _client(args)
        pi_id = getattr(args, "payment_intent_id", None)
        amount = getattr(args, "amount", 500)
        result = v.buy_credits(amount_cents=amount, payment_intent_id=pi_id)

        if pi_id:
            # Confirmation response
            if result.confirmed:
                print(f"\n  {GREEN}{BOLD}Payment confirmed!{RESET}")
                if result.credits_added:
                    print(f"  Credits added: {GREEN}${result.credits_added / 100:.2f}{RESET}")
                if result.new_balance_cents is not None:
                    print(f"  New balance:   {GREEN}${result.new_balance_cents / 100:.2f}{RESET}")
            else:
                print(f"\n  {YELLOW}Payment not yet confirmed.{RESET}")
                print(f"  Check that USDC was sent, then try again.")
        else:
            # Deposit address response
            print(f"\n  {BOLD}Buy Credits — ${amount / 100:.2f}{RESET}")
            print(f"  Current balance: ${result.current_balance_cents / 100:.2f}")
            if result.deposit:
                print(f"\n  {BOLD}Send USDC on Base:{RESET}")
                print(f"  Amount:  {GREEN}{result.deposit.amount_usdc} USDC{RESET}")
                print(f"  Address: {BOLD}{result.deposit.address}{RESET}")
                print(f"  Network: {result.deposit.chain}")
            print(f"\n  After sending, confirm with:")
            print(f"  {DIM}varrd buy-credits --confirm {result.payment_intent_id}{RESET}")
            if result.fallback:
                print(f"\n  {DIM}Or buy at: {result.fallback.web_ui}{RESET}")

    except Exception as e:
        _handle_error(e)


def cmd_research(args):
    """Multi-turn research — follows next_actions automatically."""
    try:
        v = _client(args)
        message = args.idea
        session_id = None
        max_turns = getattr(args, "max_turns", 15)

        for turn in range(1, max_turns + 1):
            print(f"\n  {BOLD}--- Turn {turn} ---{RESET}")
            print(f"  {DIM}> {message[:120]}{'...' if len(message) > 120 else ''}{RESET}")

            result = v.research(message, session_id=session_id)
            session_id = result.session_id
            display_research(result)

            ctx = result.context

            # Terminal states
            if ctx.has_edge is True:
                if "trade setup" not in message.lower() and turn < max_turns:
                    message = "Show me the trade setup"
                    continue
                break
            elif ctx.has_edge is False and ctx.workflow_state in ("tested", "optimized"):
                break

            # Follow next_actions
            if ctx.next_actions:
                message = ctx.next_actions[0]
                print(f"\n  {YELLOW}Next: {message[:80]}{RESET}")
            elif ctx.workflow_state in ("tested", "optimized"):
                break
            elif ctx.workflow_state in ("charted", "approved"):
                message = "Test it"
            elif ctx.workflow_state == "researching":
                message = "Continue"
            else:
                break

        print(f"\n  {GREEN}Research complete ({turn} turns){RESET}")

    except Exception as e:
        _handle_error(e)


def cmd_discover(args):
    try:
        v = _client(args)
        result = v.discover(
            topic=args.topic,
            markets=getattr(args, "markets", None),
            test_type=getattr(args, "test_type", "event_study"),
            search_mode=getattr(args, "mode", "focused"),
            asset_classes=getattr(args, "asset_classes", None),
        )
        display_discover(result)
    except Exception as e:
        _handle_error(e)


def cmd_briefing(args):
    try:
        v = _client(args)
        result = v.briefing()
        display_briefing(result)
    except Exception as e:
        _handle_error(e)


def cmd_auth(args):
    from varrd.auth import get_credentials, clear_credentials, CREDENTIALS_FILE

    subcmd = getattr(args, "auth_command", None)
    if subcmd == "clear":
        clear_credentials()
        print(f"  {GREEN}Credentials cleared.{RESET}")
    else:
        # status
        creds = get_credentials()
        if creds:
            token = creds["token"]
            masked = token[:16] + "..." if len(token) > 16 else token
            print(f"  {GREEN}Authenticated{RESET}")
            print(f"  Token: {masked}")
            print(f"  File:  {CREDENTIALS_FILE}")
        else:
            print(f"  {YELLOW}No stored credentials.{RESET}")
            print(f"  VARRD will auto-create an anonymous agent on first use.")
            print(f"  Or set VARRD_API_KEY environment variable.")


def cmd_agent_instructions(args):
    from varrd.instructions import AGENT_INSTRUCTIONS
    print(AGENT_INSTRUCTIONS)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _print_welcome():
    """Print a rich welcome guide when running `varrd` with no args."""
    print(f"""
  {BOLD}VARRD{RESET} — Trading edge discovery

  {BOLD}Quick start:{RESET}
    varrd research "When RSI drops below 25 on ES, is there a bounce?"
    varrd discover "mean reversion on futures"
    varrd scan --only-firing
    varrd briefing

  {BOLD}Commands:{RESET}
    research <idea>        Multi-turn research (auto-follows workflow)
    discover <topic>       Autonomous edge discovery
    scan                   What's firing right now
    briefing               Personalized market news (uses your edge library)
    search <query>         Find saved strategies
    hypothesis <id>        Get strategy details
    balance                Check credits
    buy-credits            Buy credits with USDC on Base ($5 min)
    auth status|clear      Manage authentication

  {DIM}First time? Just run a research command — VARRD auto-creates
  an account and saves credentials to ~/.varrd/credentials.{RESET}

  {BOLD}AI agent?{RESET} Run: varrd agent-instructions

  MCP (recommended for AI): https://app.varrd.com/mcp
  Docs: https://github.com/varrd-ai/varrd
""")


def cmd_mcp(args):
    """MCP stdio server — proxies JSON-RPC over stdin/stdout to app.varrd.com/mcp.

    Used by Claude Desktop, LobeHub, Cursor, and any MCP client that launches
    a local process. Each newline-delimited JSON-RPC message on stdin is
    forwarded to the remote HTTP endpoint; the response is written to stdout.
    """
    import json
    import requests

    base_url = getattr(args, "url", None) or "https://app.varrd.com"
    mcp_url = f"{base_url}/mcp"

    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    })

    # Attach agent key if available
    try:
        from varrd.auth import get_credentials
        creds = get_credentials()
        if creds and creds.get("api_key"):
            session.headers["X-Agent-Key"] = creds["api_key"]
    except Exception:
        pass

    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            continue

        try:
            resp = session.post(mcp_url, json=msg, timeout=30)
            ct = resp.headers.get("Content-Type", "")
            if "text/event-stream" in ct:
                # SSE — collect all data events, return the last result
                result = None
                for line in resp.text.splitlines():
                    if line.startswith("data: "):
                        try:
                            result = json.loads(line[6:])
                        except Exception:
                            pass
                if result:
                    sys.stdout.write(json.dumps(result) + "\n")
                    sys.stdout.flush()
            else:
                sys.stdout.write(json.dumps(resp.json()) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": msg.get("id"), "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(
        prog="varrd",
        description="VARRD — trading edge discovery from the terminal",
    )
    parser.add_argument("--url", help="API base URL (default: https://app.varrd.com)")
    parser.add_argument("--key", help="API key (default: $VARRD_API_KEY or auto)")

    sub = parser.add_subparsers(dest="command", help="Command")

    # balance
    sub.add_parser("balance", help="Check credit balance")

    # scan
    p_scan = sub.add_parser("scan", help="Scan strategies against live market data")
    p_scan.add_argument("--market", help="Filter by market symbol")
    p_scan.add_argument("--only-firing", action="store_true", help="Only show firing strategies")

    # search
    p_search = sub.add_parser("search", help="Search saved strategies")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--market", help="Filter by market")
    p_search.add_argument("--limit", type=int, default=10, help="Max results")

    # research
    p_res = sub.add_parser("research", help="Multi-turn research session")
    p_res.add_argument("idea", help="Trading idea or research question")
    p_res.add_argument("--max-turns", type=int, default=15, help="Max conversation turns")

    # discover
    p_disc = sub.add_parser("discover", help="Autonomous edge discovery")
    p_disc.add_argument("topic", help="Research topic")
    p_disc.add_argument("--markets", nargs="+", help="Focus markets")
    p_disc.add_argument("--test-type", choices=["event_study", "backtest", "both"], default="event_study")
    p_disc.add_argument("--mode", choices=["focused", "explore"], default="focused")

    # hypothesis
    p_hyp = sub.add_parser("hypothesis", help="Get full details for a strategy")
    p_hyp.add_argument("id", help="Hypothesis ID")

    # buy-credits
    p_buy = sub.add_parser("buy-credits", help="Buy credits with USDC on Base ($5 min)")
    p_buy.add_argument("--amount", type=int, default=500, help="Amount in cents (default 500 = $5)")
    p_buy.add_argument("--confirm", dest="payment_intent_id", help="Payment intent ID to confirm")

    # reset
    p_reset = sub.add_parser("reset", help="Reset a broken research session")
    p_reset.add_argument("session_id", help="Session ID to reset")

    # auth
    p_auth = sub.add_parser("auth", help="Manage authentication")
    auth_sub = p_auth.add_subparsers(dest="auth_command")
    auth_sub.add_parser("status", help="Show current auth status")
    auth_sub.add_parser("clear", help="Clear stored credentials")

    # briefing
    sub.add_parser("briefing", help="Get personalized market news briefing")

    # agent-instructions
    sub.add_parser("agent-instructions", help="Print instructions for AI agents using this CLI")

    # mcp — stdio proxy for Claude Desktop, LobeHub, Cursor, etc.
    sub.add_parser("mcp", help="Start as MCP stdio server (proxies to app.varrd.com/mcp)")

    args = parser.parse_args()

    if not args.command:
        # If stdin is a pipe (not a terminal), act as MCP stdio server.
        # This lets LobeHub/Claude Desktop use `command: "varrd"` directly.
        if not sys.stdin.isatty():
            cmd_mcp(args)
            return
        _print_welcome()
        sys.exit(0)

    # First-run welcome (no credentials yet)
    from varrd.auth import get_credentials
    if not get_credentials() and args.command not in ("auth", "agent-instructions"):
        print(f"\n  {BOLD}Welcome to VARRD!{RESET}")
        print(f"  An account will be auto-created on your first API call.")
        print(f"  Save your passkey when it appears — you'll need it to")
        print(f"  access your research at app.varrd.com")
        print(f"  {DIM}Tip: Run 'varrd agent-instructions' for full AI agent guide{RESET}\n")

    cmd_map = {
        "balance": cmd_balance,
        "briefing": cmd_briefing,
        "buy-credits": cmd_buy_credits,
        "scan": cmd_scan,
        "search": cmd_search,
        "research": cmd_research,
        "discover": cmd_discover,
        "hypothesis": cmd_hypothesis,
        "reset": cmd_reset,
        "auth": cmd_auth,
        "agent-instructions": cmd_agent_instructions,
        "mcp": cmd_mcp,
    }

    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
