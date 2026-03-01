"""Test many ideas using autonomous discovery.

Each call to discover() tests one hypothesis end-to-end.
Great for batch exploration of a theme.
"""

from varrd import VARRD

v = VARRD()

ideas = [
    "RSI oversold reversals on ES",
    "Momentum breakouts on gold",
    "Mean reversion after VIX spikes",
    "Seasonal patterns in wheat",
    "Volume surge breakdowns on NQ",
]

print(f"Testing {len(ideas)} ideas...\n")

edges_found = []

for i, idea in enumerate(ideas, 1):
    print(f"[{i}/{len(ideas)}] {idea}")

    try:
        result = v.discover(idea)
        verdict = result.edge_verdict or "?"
        wr = f"{result.win_rate:.0%}" if result.win_rate else "-"
        print(f"  -> {verdict} | WR={wr} | {result.market}")

        if result.has_edge:
            edges_found.append(result)
            if result.trade_setup:
                ts = result.trade_setup
                print(f"     Entry: ${ts.entry_price}  SL: ${ts.stop_loss}  TP: ${ts.take_profit}")
    except Exception as e:
        print(f"  -> Error: {e}")

    print()

print(f"\n{'='*50}")
print(f"Results: {len(edges_found)} edges found out of {len(ideas)} ideas tested")
for r in edges_found:
    print(f"  - {r.name} [{r.market}] {r.edge_verdict}")
