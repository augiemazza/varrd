---
name: varrd-reset
description: Reset a broken or stuck research session and start fresh
tools: ["Bash"]
---

# VARRD Reset — Fix Stuck Sessions

Use this skill when a research session gets stuck, errors out, or enters a bad state.

## Command

```bash
varrd reset <session_id>
```

## How It Works

Kills the broken session on the server. After resetting, start a new research session by running `varrd research` without a session ID.

## When to Use

- Research session returns errors on subsequent turns
- Session feels stuck or unresponsive
- You got a 404 on a session ID (server restarted)

## Important

- Don't try to fix a broken session — just reset and start over
- Session state is not precious — validated hypotheses are already saved to your library
- After reset, call `varrd research "your idea"` to start fresh

## Cost

Free. No credits consumed.

## Python SDK Equivalent

```python
from varrd import VARRD
v = VARRD()
v.reset("sess_abc123")
# Start fresh
r = v.research("your idea here")
```
