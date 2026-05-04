"""VARRD Quick Start — see what's firing right now."""

from varrd import VARRD

v = VARRD()

# What edges are firing right now? (free)
result = v.edges()
print(result.text)

# Get stats + trade levels on all active edges ($0.50)
result = v.edges(depth=1)
print(result.text)

# Filter: only short setups on futures
result = v.edges(depth=1, direction="SHORT", asset_class="futures")
print(result.text)

# Full audit trail on a specific edge ($1)
result = v.edges(depth=2, edge_id="your-edge-id-here")
print(result.text)
