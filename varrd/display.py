"""Terminal formatting for VARRD CLI output."""

from __future__ import annotations

import os
import sys

from varrd.models import (
    BalanceResult,
    DiscoverResult,
    HypothesisDetail,
    ResearchResult,
    ScanResult,
    SearchResult,
    ResetResult,
)

# ---------------------------------------------------------------------------
# Colors (disabled when not a TTY or NO_COLOR is set)
# ---------------------------------------------------------------------------

_COLOR = (
    hasattr(sys.stdout, "isatty")
    and sys.stdout.isatty()
    and not os.environ.get("NO_COLOR")
)


def _c(code: str) -> str:
    return code if _COLOR else ""


GREEN = _c("\033[92m")
RED = _c("\033[91m")
YELLOW = _c("\033[93m")
CYAN = _c("\033[96m")
MAGENTA = _c("\033[95m")
BOLD = _c("\033[1m")
DIM = _c("\033[2m")
RESET = _c("\033[0m")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pct(val: float | None) -> str:
    if val is None:
        return "-"
    return f"{val:.0%}"


def _dollar(val: float | None) -> str:
    if val is None:
        return "-"
    return f"${val:,.2f}"


def _safe(text: str) -> str:
    """Strip characters that break Windows terminals."""
    try:
        text.encode(sys.stdout.encoding or "utf-8")
        return text
    except (UnicodeEncodeError, LookupError):
        return text.encode("ascii", errors="replace").decode("ascii")


# ---------------------------------------------------------------------------
# Display functions
# ---------------------------------------------------------------------------

def display_balance(result: BalanceResult):
    bal = result.balance_cents / 100
    print(f"  {BOLD}Balance:{RESET}     {GREEN}${bal:.2f}{RESET}")
    print(f"  {BOLD}Enforcement:{RESET} {'ON' if result.enforcement_enabled else 'OFF (tracking only)'}")
    if result.lifetime_added_cents is not None:
        lt = result.lifetime_added_cents / 100
        print(f"  {BOLD}Lifetime:{RESET}    ${lt:.2f}")
    if result.credit_packs:
        packs = ", ".join(p.label for p in result.credit_packs)
        print(f"  {BOLD}Packs:{RESET}       {packs}")


def display_scan(result: ScanResult):
    print(f"  Scanned {BOLD}{result.total_scanned}{RESET} strategies, "
          f"{GREEN}{BOLD}{result.firing_count}{RESET} firing now\n")

    if not result.results:
        print(f"  {DIM}No results.{RESET}")
        return

    for item in result.results:
        if item.firing_now:
            icon = f"{GREEN}{BOLD}>>>{RESET}"
            status = f"{GREEN}FIRING{RESET}"
        else:
            icon = f"{DIM}   {RESET}"
            status = f"{DIM}{item.status}{RESET}"

        name = _safe(item.name or "Unnamed")
        wr = _pct(item.win_rate)

        print(f"  {icon} {BOLD}{name}{RESET} [{item.market} {item.direction}] "
              f"WR={wr}  {status}")

        if item.firing_now and item.trade_setups:
            seen = set()
            for ts in item.trade_setups:
                key = (ts.entry_price, ts.stop_loss, ts.take_profit)
                if key not in seen:
                    seen.add(key)
                    print(f"      Entry: {_dollar(ts.entry_price)}  "
                          f"SL: {_dollar(ts.stop_loss)}  "
                          f"TP: {_dollar(ts.take_profit)}")

        print(f"      {DIM}ID: {item.hypothesis_id}{RESET}")


def display_search(result: SearchResult):
    print(f"  {BOLD}{len(result.results)}{RESET} results"
          f"{f' (via {result.method})' if result.method else ''}\n")

    for item in result.results:
        name = _safe(item.name or "Unnamed")
        wr = _pct(item.win_rate)
        edge = f"{GREEN}EDGE{RESET}" if item.has_edge else f"{DIM}no edge{RESET}"
        sim = f" ({item.similarity:.0%} match)" if item.similarity else ""

        print(f"  {BOLD}{name}{RESET} [{item.market}] WR={wr} {edge}{sim}")
        print(f"    {DIM}ID: {item.hypothesis_id}{RESET}")


def display_hypothesis(result: HypothesisDetail):
    name = _safe(result.name or "Unnamed")
    edge = f"{GREEN}{BOLD}EDGE{RESET}" if result.has_edge else f"{RED}no edge{RESET}"

    print(f"  {BOLD}{name}{RESET} [{result.market}] {edge}")
    print(f"  {DIM}ID: {result.hypothesis_id}{RESET}")
    print()
    if result.formula:
        print(f"  {BOLD}Formula:{RESET}   {_safe(result.formula[:120])}")
    if result.direction:
        print(f"  {BOLD}Direction:{RESET} {result.direction}")
    if result.test_type:
        print(f"  {BOLD}Test:{RESET}      {result.test_type}")
    print()

    # Stats
    stats = []
    if result.win_rate is not None:
        stats.append(f"WR={_pct(result.win_rate)}")
    if result.sharpe is not None:
        stats.append(f"Sharpe={result.sharpe:.2f}")
    if result.profit_factor is not None:
        stats.append(f"PF={result.profit_factor:.2f}")
    if result.total_trades is not None:
        stats.append(f"Trades={result.total_trades}")
    if result.max_drawdown is not None:
        stats.append(f"MaxDD={result.max_drawdown:.1%}")
    if stats:
        print(f"  {BOLD}Stats:{RESET}     {' | '.join(stats)}")

    # Horizon results
    if result.horizon_results:
        print(f"\n  {BOLD}Horizons:{RESET}")
        for h in result.horizon_results:
            sig = f"{GREEN}*{RESET}" if h.significant else " "
            wr = _pct(h.win_rate)
            mr = f"{h.mean_return:.3%}" if h.mean_return is not None else "-"
            print(f"    {sig} {h.horizon}d: WR={wr}  MeanRet={mr}")

    # Versions
    if result.versions:
        print(f"\n  {BOLD}Versions:{RESET} {len(result.versions)}")


def display_research(result: ResearchResult):
    ctx = result.context

    # Print text
    if result.text:
        lines = result.text.strip().split("\n")
        for line in lines[:30]:
            print(f"  {_safe(line)}")
        if len(lines) > 30:
            print(f"  {DIM}... ({len(lines) - 30} more lines){RESET}")
    print()

    # Widget summaries
    for w in result.widgets:
        wtype = w.get("type", "unknown")
        wdata = w.get("data", {})
        if wtype == "event_study":
            edge = wdata.get("has_edge")
            best = wdata.get("best_horizon", {})
            wr = best.get("win_rate", "?") if isinstance(best, dict) else "?"
            color = GREEN if edge else RED if edge is False else YELLOW
            print(f"  {color}[EVENT STUDY]{RESET} edge={edge} best_wr={wr}")
        elif wtype == "trade_setup":
            entry = wdata.get("entry_price", "?")
            sl = wdata.get("stop_loss", "?")
            tp = wdata.get("take_profit", "?")
            print(f"  {GREEN}[TRADE SETUP]{RESET} entry={entry} SL={sl} TP={tp}")
        elif wtype == "backtest":
            trades = wdata.get("total_trades", "?")
            wr = wdata.get("win_rate", "?")
            print(f"  {MAGENTA}[BACKTEST]{RESET} trades={trades} WR={wr}")
        elif wtype == "sltp_optimization":
            best = wdata.get("best", wdata.get("best_combo", {}))
            print(f"  {CYAN}[SL/TP OPTIMIZATION]{RESET} best={best}")
        elif wtype == "chart":
            signals = wdata.get("occurrences", wdata.get("signal_count", "?"))
            print(f"  {CYAN}[CHART]{RESET} signals={signals}")
        else:
            print(f"  [{wtype.upper()}]")

    # Context summary
    if ctx.has_edge is True:
        print(f"\n  {GREEN}{BOLD}Edge found!{RESET} "
              f"Verdict: {ctx.edge_verdict or '?'}")
    elif ctx.has_edge is False:
        print(f"\n  {RED}No edge found.{RESET}")

    if ctx.next_actions:
        print(f"\n  {YELLOW}Next actions:{RESET}")
        for action in ctx.next_actions:
            print(f"    - {action}")


def display_discover(result: DiscoverResult):
    name = _safe(result.name or "Unnamed")
    edge = f"{GREEN}{BOLD}EDGE{RESET}" if result.has_edge else f"{RED}no edge{RESET}"

    print(f"  {BOLD}{name}{RESET} [{result.market}] {edge}")
    if result.edge_verdict:
        print(f"  Verdict: {result.edge_verdict}")
    if result.direction:
        print(f"  Direction: {result.direction}")

    stats = []
    if result.win_rate is not None:
        stats.append(f"WR={_pct(result.win_rate)}")
    if result.sharpe is not None:
        stats.append(f"Sharpe={result.sharpe:.2f}")
    if stats:
        print(f"  {' | '.join(stats)}")

    if result.trade_setup:
        ts = result.trade_setup
        print(f"\n  {GREEN}Trade Setup:{RESET}")
        print(f"    Entry: {_dollar(ts.entry_price)}  "
              f"SL: {_dollar(ts.stop_loss)}  "
              f"TP: {_dollar(ts.take_profit)}")

    if result.text:
        print(f"\n  {DIM}{_safe(result.text[:500])}{RESET}")


def display_reset(result: ResetResult):
    if result.reset:
        print(f"  {GREEN}Session reset.{RESET} {result.message}")
    else:
        print(f"  {RED}Reset failed.{RESET} {result.message}")
