"""Validate existing Jesse strategies using VARRD's statistical engine."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of validating a Jesse strategy through VARRD."""

    strategy_name: str = ""
    pair: str = ""
    timeframe: str = ""
    indicators_found: list[str] = field(default_factory=list)
    entry_conditions: list[str] = field(default_factory=list)
    natural_language: str = ""

    # Populated after VARRD validation
    has_edge: bool | None = None
    edge_verdict: str = ""
    win_rate: float | None = None
    sharpe: float | None = None
    hypothesis_id: str = ""
    session_id: str = ""


def _extract_class_name(tree: ast.Module) -> str:
    """Find the Strategy subclass name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = ""
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name == "Strategy":
                    return node.name
    return ""


def _extract_method_source(source: str, method_name: str) -> str:
    """Extract the source code of a method from the raw file text."""
    pattern = rf"(def {method_name}\(.*?\n(?:(?:        .+|[ \t]*)\n)*)"
    match = re.search(pattern, source)
    if match:
        return match.group(1).strip()
    return ""


def _extract_routes_pair(project_dir: str) -> tuple[str, str]:
    """Try to extract pair and timeframe from routes.py in the project dir."""
    routes_path = Path(project_dir) / "routes.py"
    if not routes_path.exists():
        return "", ""

    text = routes_path.read_text(encoding="utf-8")
    # Match route tuples like ('Binance Futures', 'BTC-USDT', '1D', 'MyStrategy')
    match = re.search(r"\(\s*['\"].*?['\"]\s*,\s*['\"](.+?)['\"]\s*,\s*['\"](.+?)['\"]\s*,", text)
    if match:
        return match.group(1), match.group(2)
    return "", ""


def _conditions_to_natural_language(
    strategy_name: str,
    timeframe: str,
    before_body: str,
    should_long_body: str,
    should_short_body: str,
) -> str:
    """Convert extracted code into a natural-language research prompt for VARRD."""
    parts = [f"I have a Jesse strategy called '{strategy_name}'."]
    parts.append(f"It runs on the {timeframe} timeframe.")

    if before_body:
        parts.append(f"It calculates these indicators in before():\n```python\n{before_body}\n```")

    if should_long_body:
        parts.append(f"The long entry condition (should_long):\n```python\n{should_long_body}\n```")

    if should_short_body:
        parts.append(f"The short entry condition (should_short):\n```python\n{should_short_body}\n```")

    parts.append(
        "Can you validate whether this strategy has a real statistical edge? "
        "Please test the entry logic and tell me if the results are significant."
    )
    return "\n\n".join(parts)


def parse_strategy(strategy_path: str) -> ValidationResult:
    """Parse a Jesse strategy file and extract entry logic.

    This does NOT call VARRD — it just extracts the relevant code
    so you can inspect it or pass it to validate_strategy().
    """
    path = Path(strategy_path)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    class_name = _extract_class_name(tree)

    # Try to get pair/timeframe from routes.py in the same directory
    pair, timeframe = _extract_routes_pair(str(path.parent))
    if not timeframe:
        timeframe = "1D"

    before_body = _extract_method_source(source, "before")
    should_long_body = _extract_method_source(source, "should_long")
    should_short_body = _extract_method_source(source, "should_short")

    # Rough indicator detection
    indicator_names: list[str] = []
    indicator_patterns = [
        "RSI", "EMA", "SMA", "MACD", "BBANDS", "ATR", "ADX",
        "STOCH", "CCI", "MFI", "OBV", "WILLR", "ROC", "MOM",
    ]
    combined = before_body + should_long_body + should_short_body
    for name in indicator_patterns:
        if name.lower() in combined.lower():
            indicator_names.append(name)

    # Extract return expressions from should_long/should_short as conditions
    conditions: list[str] = []
    for body in (should_long_body, should_short_body):
        for match in re.finditer(r'return\s+(.+)', body):
            expr = match.group(1).strip()
            if expr not in ("False", "True"):
                conditions.append(expr)

    nl = _conditions_to_natural_language(
        class_name, timeframe, before_body, should_long_body, should_short_body,
    )

    return ValidationResult(
        strategy_name=class_name,
        pair=pair,
        timeframe=timeframe,
        indicators_found=indicator_names,
        entry_conditions=conditions,
        natural_language=nl,
    )


def validate_strategy(
    strategy_path: str,
    varrd_client=None,
) -> ValidationResult:
    """Parse a Jesse strategy and validate it through VARRD.

    Args:
        strategy_path: Path to a Jesse strategy .py file.
        varrd_client: Optional VARRD client instance. If None, creates one.

    Returns:
        ValidationResult with edge verdict and stats.
    """
    result = parse_strategy(strategy_path)

    if varrd_client is None:
        from varrd import VARRD
        varrd_client = VARRD()

    # Run the natural-language description through VARRD research
    r = varrd_client.research(result.natural_language)

    # Follow up until we get an edge verdict or exhaust next_actions
    max_turns = 10
    for _ in range(max_turns):
        ctx = r.context
        if ctx.has_edge is not None:
            break
        if ctx.next_actions:
            action = ctx.next_actions[0]
            r = varrd_client.research(action, session_id=r.session_id)
        else:
            break

    result.session_id = r.session_id
    result.has_edge = r.context.has_edge
    result.edge_verdict = r.context.edge_verdict or ""
    result.hypothesis_id = ""

    return result
