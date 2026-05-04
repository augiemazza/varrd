---
name: varrd-edges
description: Browse VARRD's validated edge library — see which edges are firing right now, get stats and trade levels, or drill into the full methodology and performance of any edge.
version: 1.0.0
tools: ["Bash"]
homepage: https://varrd.com
metadata: {"openclaw": {"requires": {"bins": ["varrd"]}, "emoji": "📈"}}
---

# VARRD Edges — Browse the Validated Edge Library

## What this does

VARRD maintains a library of statistically validated trading edges running 24/7 against live market data. This skill lets you browse which edges are firing, get trade levels, and drill into the full methodology.

## Three tiers

### Free — which markets are firing
```bash
varrd edges
```
Shows markets and status. No direction, no stats, no trade levels.

### $0.50 — 15-minute snapshot with stats + trade levels
```bash
varrd edges --depth 1
```
Direction, win rate, EV, stops, entry date, hold period for every active edge.

### $1/edge — full audit trail
```bash
varrd edges --depth 2 --edge-id <id>
```
Complete methodology: formula, discovery story, per-horizon results, SQN, profit factor, Kelly %, Monte Carlo, drawdown, regime analysis, edge decay, and interactive view link.

## Filters

```bash
varrd edges --depth 1 --direction SHORT           # only shorts
varrd edges --depth 1 --asset-class equities       # only stocks/ETFs
varrd edges --depth 1 --timeframe 240min           # only 4-hour edges
varrd edges --depth 1 --market GC                  # only gold
varrd edges --depth 1 --status firing              # only actionable now
```

## Edge statuses

- **FIRING** — signal confirmed, enter at next bar open
- **PENDING** — bar hasn't closed, don't act yet
- **ACTIVE** — already in a trade from a previous signal

## Typical flow

1. `varrd edges` — see what's firing (free)
2. User picks a market they're interested in
3. `varrd edges --depth 1 --market AAPL` — get stats ($0.50)
4. User wants the full picture on one edge
5. `varrd edges --depth 2 --edge-id <id>` — full audit trail ($1)
6. Share the interactive view link with the user
