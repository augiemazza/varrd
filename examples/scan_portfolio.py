"""Scan all saved strategies and show a summary."""

from varrd import VARRD

v = VARRD()

# Scan everything
result = v.scan()
print(f"Portfolio: {result.total_scanned} strategies, {result.firing_count} firing\n")

# Show firing strategies with trade levels
firing = [r for r in result.results if r.firing_now]
dormant = [r for r in result.results if not r.firing_now]

if firing:
    print("FIRING NOW:")
    for s in firing:
        wr = f"{s.win_rate:.0%}" if s.win_rate else "-"
        print(f"  >>> {s.name} [{s.market} {s.direction}] WR={wr}")
        for ts in s.trade_setups:
            print(f"      Entry: ${ts.entry_price}  SL: ${ts.stop_loss}  TP: ${ts.take_profit}")
    print()

if dormant:
    print(f"DORMANT ({len(dormant)}):")
    for s in dormant[:10]:
        wr = f"{s.win_rate:.0%}" if s.win_rate else "-"
        edge = "EDGE" if s.has_edge else ""
        print(f"      {s.name} [{s.market}] WR={wr} {edge}")
