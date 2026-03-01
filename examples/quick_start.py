"""VARRD Quick Start — 5 lines to get started."""

from varrd import VARRD

v = VARRD()
signals = v.scan(only_firing=True)

print(f"Scanned {signals.total_scanned} strategies, {signals.firing_count} firing now\n")
for s in signals.results:
    if s.firing_now:
        print(f"  {s.name}: {s.direction} {s.market}")
        for ts in s.trade_setups:
            print(f"    Entry: ${ts.entry_price}  SL: ${ts.stop_loss}  TP: ${ts.take_profit}")
