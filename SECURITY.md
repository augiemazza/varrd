# Security Policy

VARRD handles financial data, authentication credentials, and payment processing. We take security seriously.

## Reporting a Vulnerability

**Do not open a public issue.** Email security findings to:

**management@varrd.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Impact assessment (what an attacker could do)
- Any proof-of-concept code

## What's In Scope

| Area | Examples |
|------|----------|
| **Authentication** | JWT handling, passkey system, agent provisioning, session management |
| **Billing** | Credit deduction, payment replay, balance manipulation, Stripe webhook handling |
| **MCP Server** | Tool injection, parameter manipulation, rate limit bypass, unauthorized data access |
| **API** | Endpoint auth bypass, IDOR, injection, information disclosure |
| **Data Exposure** | Edge formulas/methodology leaking at unpaid tiers, user data cross-contamination |

## Out of Scope

- Rate limiting thresholds (we're aware, actively tuning)
- Self-XSS or attacks requiring physical device access
- Denial of service (please don't load-test production)
- Social engineering of VARRD staff
- Vulnerabilities in third-party services (Stripe, AWS, Anthropic)

## Response Timeline

| Step | Target |
|------|--------|
| Acknowledgment | 24 hours |
| Initial assessment | 72 hours |
| Fix deployed | 7 days for critical, 30 days for moderate |
| Disclosure | Coordinated, after fix is live |

## What We've Already Hardened

We've run multiple rounds of penetration testing. Current protections include:

- Atomic idempotency on all payment paths (DynamoDB ConditionExpression)
- Cross-user payment replay blocked (PaymentIntent metadata verification)
- Stripe webhook signature verification
- Per-agent billing isolation (balance deduction with ConditionExpression)
- IP rate limiting on agent provisioning and API endpoints
- JWT expiry enforcement, brute-force lockout (15 fails in 5 min)
- Dormant edges completely blocked from all tiers
- Request body size limits (1MB) and batch limits (10)
- No secrets in client-facing responses or documentation
- Lookahead bias verification on all validated edges

## Recognition

We'll credit researchers who report valid vulnerabilities (with permission) in our release notes. No bug bounty program at this time, but significant findings will be acknowledged.
