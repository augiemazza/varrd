---
name: varrd-balance
description: Check VARRD credit balance and available credit packs
tools: ["Bash"]
---

# VARRD Balance — Check Credits

Use this skill to check how many credits the user has before running paid operations.

## Command

```bash
varrd balance
```

## How It Works

Returns the current credit balance in cents, whether billing enforcement is enabled, and available credit packs for purchase.

## When to Check

- Before running `varrd research` or `varrd discover` (these cost credits)
- After getting a "credits depleted" error
- `varrd scan`, `varrd search`, `varrd hypothesis`, and `varrd reset` are free — no need to check first

## Cost Reference

| Operation | Approximate Cost |
|-----------|-----------------|
| scan, search, hypothesis, balance, reset | Free |
| Full research workflow | ~20-30 cents |
| ELROND expert council | ~40-60 cents |
| Multi-market testing (3+ markets) | ~$1 |

## If Credits Are Low

Direct the user to purchase more at [app.varrd.com](https://app.varrd.com). Credit packs: $5 / $20 / $50.

New accounts start with $2.00 in free credits (~10-20 research queries).

## Cost

Free. No credits consumed.

## Python SDK Equivalent

```python
from varrd import VARRD
v = VARRD()
b = v.balance()
print(f"Balance: ${b.balance_cents / 100:.2f}")
```
