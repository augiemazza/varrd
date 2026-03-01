"""VARRD client — thin HTTP wrapper around the VARRD MCP server.

Usage:
    from varrd import VARRD

    v = VARRD()                          # auto-auth (anonymous agent)
    v = VARRD(api_key="your-key")        # explicit key

    # Free tools
    v.balance()
    v.scan(only_firing=True)
    v.search("momentum on grains")
    v.get_hypothesis("hyp_abc123")

    # Research (costs credits)
    r = v.research("When RSI drops below 25 on ES, is there a bounce?")
    r = v.research("test it", session_id=r.session_id)

    # Autonomous discovery (costs credits)
    d = v.discover("mean reversion on futures")
"""

from __future__ import annotations

import json
import time
from typing import Any

import requests

from varrd.auth import get_token, save_credentials
from varrd.models import (
    BalanceResult,
    DiscoverResult,
    HypothesisDetail,
    ResetResult,
    ResearchResult,
    ScanResult,
    SearchResult,
)

DEFAULT_BASE_URL = "https://app.varrd.com"
DEFAULT_TIMEOUT = 300  # 5 minutes — research calls can be slow


class VARRDError(Exception):
    """Base exception for VARRD client errors."""


class PaymentRequired(VARRDError):
    """Raised when credits are depleted (HTTP 402)."""

    def __init__(self, detail: dict | str | None = None):
        self.detail = detail
        super().__init__("Credits depleted. Purchase more at https://app.varrd.com")


class AuthError(VARRDError):
    """Raised on authentication failure (HTTP 401)."""


class RateLimited(VARRDError):
    """Raised on rate limit (HTTP 429)."""


class VARRD:
    """VARRD trading edge discovery client.

    Connects to the VARRD MCP server over HTTP. Handles authentication,
    session management, and response parsing automatically.

    Args:
        api_key: API key or JWT. If not provided, checks VARRD_API_KEY env
                 var, then ~/.varrd/credentials, then auto-creates an
                 anonymous agent on first call.
        base_url: VARRD server URL. Defaults to https://app.varrd.com.
        timeout: Request timeout in seconds. Defaults to 300.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._mcp_session_id: str | None = None
        self._req_id = 0
        self._initialized = False

    # ------------------------------------------------------------------
    # Public API — free tools
    # ------------------------------------------------------------------

    def balance(self) -> BalanceResult:
        """Check credit balance. Free, no credits consumed."""
        data = self._call_tool("check_balance", {})
        return BalanceResult.model_validate(data)

    def scan(
        self,
        market: str | None = None,
        only_firing: bool = False,
    ) -> ScanResult:
        """Scan saved strategies against current market data.

        Args:
            market: Filter by market symbol (e.g. 'ES', 'NQ').
            only_firing: Only return strategies firing right now.

        Returns:
            ScanResult with firing status and trade levels.
        """
        args: dict[str, Any] = {}
        if market:
            args["market"] = market
        if only_firing:
            args["only_firing"] = True
        data = self._call_tool("scan", args)
        return ScanResult.model_validate(data)

    def search(
        self,
        query: str,
        market: str | None = None,
        limit: int = 10,
    ) -> SearchResult:
        """Search saved strategies by keyword or natural language.

        Args:
            query: Search query (e.g. 'momentum strategies', 'RSI oversold').
            market: Optional market filter.
            limit: Max results to return.

        Returns:
            SearchResult ranked by relevance.
        """
        args: dict[str, Any] = {"query": query, "limit": limit}
        if market:
            args["market"] = market
        data = self._call_tool("search", args)
        return SearchResult.model_validate(data)

    def get_hypothesis(self, hypothesis_id: str) -> HypothesisDetail:
        """Get full details for a specific strategy.

        Note: Trade levels from get_hypothesis may be stale (from when last
        tested). Use scan() for fresh levels on firing strategies, or
        research() to load and get fresh trade setup.

        Args:
            hypothesis_id: The hypothesis ID from scan or search results.

        Returns:
            HypothesisDetail with formula, metrics, and version history.
        """
        data = self._call_tool("get_hypothesis", {"hypothesis_id": hypothesis_id})
        return HypothesisDetail.model_validate(data)

    def reset(self, session_id: str) -> ResetResult:
        """Reset a broken research session. Free, no credits consumed.

        Args:
            session_id: The session ID to reset.

        Returns:
            ResetResult confirming the reset.
        """
        data = self._call_tool("reset_session", {"session_id": session_id})
        return ResetResult.model_validate(data)

    # ------------------------------------------------------------------
    # Public API — research tools (cost credits)
    # ------------------------------------------------------------------

    def research(
        self,
        message: str,
        session_id: str | None = None,
    ) -> ResearchResult:
        """Talk to VARRD AI — multi-turn research conversation.

        First call (no session_id) starts a new session. Pass the returned
        session_id to continue the conversation.

        Typical flow:
            r = v.research("When RSI < 25 on ES, is there a bounce?")
            r = v.research("test it", session_id=r.session_id)
            r = v.research("show me the trade setup", session_id=r.session_id)

        Check r.context.has_edge (True/False) and r.context.next_actions
        to know when to stop and what to say next.

        Args:
            message: Your trading idea, question, or instruction.
            session_id: Session ID from a previous call. Omit to start new.

        Returns:
            ResearchResult with text, widgets, and context.
        """
        args: dict[str, Any] = {"message": message}
        if session_id:
            args["session_id"] = session_id
        data = self._call_tool("research", args)
        return ResearchResult.model_validate(data)

    def discover(
        self,
        topic: str,
        markets: list[str] | None = None,
        test_type: str = "event_study",
        search_mode: str = "focused",
        asset_classes: list[str] | None = None,
    ) -> DiscoverResult:
        """Launch autonomous research — VARRD discovers and tests an edge.

        Give it a topic and it handles everything: generates a hypothesis,
        loads data, charts, runs statistical tests, and gets trade setup
        if an edge is found. Each call tests ONE hypothesis.

        Args:
            topic: Research topic (e.g. 'momentum on grains').
            markets: Focus markets (e.g. ['ES', 'NQ']). Omit for auto.
            test_type: 'event_study', 'backtest', or 'both'.
            search_mode: 'focused' (stay close) or 'explore' (creative).
            asset_classes: Limit to 'crypto', 'futures', 'equities'.

        Returns:
            DiscoverResult with edge verdict and trade setup.
        """
        args: dict[str, Any] = {"topic": topic}
        if markets:
            args["markets"] = markets
        if test_type != "event_study":
            args["test_type"] = test_type
        if search_mode != "focused":
            args["search_mode"] = search_mode
        if asset_classes:
            args["asset_classes"] = asset_classes
        data = self._call_tool("autonomous_research", args)
        return DiscoverResult.model_validate(data)

    # ------------------------------------------------------------------
    # Internal — MCP transport
    # ------------------------------------------------------------------

    def _ensure_auth(self) -> str:
        """Resolve authentication token.

        Priority: explicit api_key > env var > stored credentials > auto-create.
        """
        if self._api_key:
            return self._api_key

        token = get_token()
        if token:
            return token

        # Auto-create: make a request with no auth, server creates anonymous agent
        # and returns JWT in the response. We'll handle this in _initialize().
        return ""

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _post(self, body: dict) -> tuple[requests.Response, dict | None]:
        """Send a JSON-RPC request to the MCP endpoint. Retries on 429."""
        max_retries = 3
        for attempt in range(max_retries + 1):
            token = self._ensure_auth()
            headers: dict[str, str] = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            }
            if token:
                headers["Authorization"] = f"Bearer {token}"
            if self._mcp_session_id:
                headers["Mcp-Session-Id"] = self._mcp_session_id

            r = requests.post(
                f"{self._base_url}/mcp",
                json=body,
                headers=headers,
                timeout=self._timeout,
            )

            if r.status_code == 429 and attempt < max_retries:
                wait = 2 ** attempt  # 1s, 2s, 4s
                time.sleep(wait)
                continue

            break

        # Check for auto-created token in response headers
        new_token = r.headers.get("X-Varrd-Token")
        if new_token and not self._api_key:
            self._api_key = new_token
            passkey = r.headers.get("X-Varrd-Passkey")
            save_credentials(new_token, passkey)
            if passkey:
                import sys
                print(
                    f"\n  VARRD account created.\n"
                    f"  Your passkey: {passkey}\n"
                    f"  Saved to: ~/.varrd/credentials\n"
                    f"\n"
                    f"  Keep this passkey safe. To see your strategies in the\n"
                    f"  browser, go to app.varrd.com and link your agent using\n"
                    f"  this passkey with an email and password.\n",
                    file=sys.stderr,
                )

        try:
            data = r.json()
        except (ValueError, requests.JSONDecodeError):
            data = None

        return r, data

    def _initialize(self):
        """MCP handshake — initialize + notifications/initialized."""
        if self._initialized:
            return

        r, data = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "varrd-python", "version": "0.1.0"},
            },
        })

        if r.status_code == 401:
            raise AuthError("Authentication failed. Check your API key.")

        self._mcp_session_id = r.headers.get("Mcp-Session-Id")

        # Send initialized notification
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self._initialized = True

    def _call_tool(self, name: str, arguments: dict) -> dict:
        """Call an MCP tool and return the parsed result.

        Raises:
            PaymentRequired: Credits depleted (402).
            AuthError: Authentication failed (401).
            RateLimited: Rate limited (429).
            VARRDError: Other server errors.
        """
        self._initialize()

        r, data = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })

        if r.status_code == 401:
            raise AuthError("Authentication failed. Check your API key.")
        if r.status_code == 429:
            raise RateLimited("Rate limited. Wait and retry.")

        if not data:
            raise VARRDError(f"HTTP {r.status_code}: {r.text[:500]}")

        # Check for JSON-RPC error
        if "error" in data:
            err = data["error"]
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            raise VARRDError(f"Server error: {msg}")

        result = data.get("result", {})
        content = result.get("content", [])
        is_error = result.get("isError", False)

        if not content:
            if is_error:
                raise VARRDError("Tool returned an error with no content")
            return result

        text = content[0].get("text", "")
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            if is_error:
                raise VARRDError(f"Tool error: {text}")
            return {"text": text}

        # Check for 402 inside MCP result
        if isinstance(parsed, dict) and (
            parsed.get("error") == "payment_required"
            or parsed.get("x402Version")
        ):
            raise PaymentRequired(parsed)

        if is_error:
            msg = parsed.get("error", parsed) if isinstance(parsed, dict) else parsed
            raise VARRDError(f"Tool error: {msg}")

        return parsed

    def close(self):
        """Clean up the MCP session."""
        if self._mcp_session_id:
            try:
                token = self._ensure_auth()
                headers = {"Authorization": f"Bearer {token}"}
                if self._mcp_session_id:
                    headers["Mcp-Session-Id"] = self._mcp_session_id
                requests.delete(
                    f"{self._base_url}/mcp",
                    headers=headers,
                    timeout=10,
                )
            except Exception:
                pass
            self._mcp_session_id = None
            self._initialized = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f"VARRD(base_url={self._base_url!r})"
