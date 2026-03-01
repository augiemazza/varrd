"""Full multi-turn research workflow.

This example shows the complete flow:
1. Send a trading idea
2. Follow next_actions through chart -> test -> trade setup
3. Check for edge verdict
"""

from varrd import VARRD

v = VARRD()

# Start with an idea
idea = "When RSI drops below 25 on ES, is there a bounce within 5 days?"
print(f"Researching: {idea}\n")

session_id = None
max_turns = 10

for turn in range(1, max_turns + 1):
    if turn == 1:
        message = idea
    # After first turn, message is set by next_actions below

    print(f"--- Turn {turn} ---")
    print(f"> {message[:100]}")

    r = v.research(message, session_id=session_id)
    session_id = r.session_id

    # Show what came back
    if r.text:
        print(f"  {r.text[:200]}...")

    for w in r.widgets:
        print(f"  [{w.get('type', '?').upper()}]")

    ctx = r.context
    print(f"  State: {ctx.workflow_state} | Edge: {ctx.has_edge}")

    # Terminal states
    if ctx.has_edge is True:
        print(f"\n  EDGE FOUND: {ctx.edge_verdict}")
        if "trade setup" not in message.lower() and turn < max_turns:
            message = "Show me the trade setup"
            continue
        break
    elif ctx.has_edge is False:
        print(f"\n  No edge found. Done.")
        break

    # Follow next_actions
    if ctx.next_actions:
        message = ctx.next_actions[0]
        print(f"  Next: {message}")
    elif ctx.workflow_state in ("charted", "approved"):
        message = "Test it"
    else:
        break

    print()

print(f"\nResearch complete ({turn} turns)")
