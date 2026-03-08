"""Freqtrade integration — generate and validate strategies."""

from varrd.freqtrade.generator import generate_strategy
from varrd.freqtrade.validator import validate_strategy, ValidationResult

__all__ = ["generate_strategy", "validate_strategy", "ValidationResult"]
