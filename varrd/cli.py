"""VARRD CLI — trading edge discovery from the terminal.

Usage:
    varrd balance
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

  {BOLD}Commands:{RESET}
    research <idea>        Multi-turn research (auto-follows workflow)
    discover <topic>       Autonomous edge discovery
    scan                   What's firing right now
    search <query>         Find saved strategies
    hypothesis <id>        Get strategy details
    balance                Check credits
    auth status|clear      Manage authentication

  {DIM}First time? Just run a research command — VARRD auto-creates
  an account and saves credentials to ~/.varrd/credentials.{RESET}

  {BOLD}AI agent?{RESET} Run: varrd agent-instructions

  MCP (recommended for AI): https://app.varrd.com/mcp
  Docs: https://github.com/varrd-ai/varrd
""")


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

    # reset
    p_reset = sub.add_parser("reset", help="Reset a broken research session")
    p_reset.add_argument("session_id", help="Session ID to reset")

    # auth
    p_auth = sub.add_parser("auth", help="Manage authentication")
    auth_sub = p_auth.add_subparsers(dest="auth_command")
    auth_sub.add_parser("status", help="Show current auth status")
    auth_sub.add_parser("clear", help="Clear stored credentials")

    # agent-instructions
    sub.add_parser("agent-instructions", help="Print instructions for AI agents using this CLI")

    args = parser.parse_args()

    if not args.command:
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
        "scan": cmd_scan,
        "search": cmd_search,
        "research": cmd_research,
        "discover": cmd_discover,
        "hypothesis": cmd_hypothesis,
        "reset": cmd_reset,
        "auth": cmd_auth,
        "agent-instructions": cmd_agent_instructions,
    }

    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
