"""Atom — pure value formatters. No UI elements."""


def _fmt_currency(value, sign):
    return f"{sign}{value:,.2f}"


def _fmt_pct(value):
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}%"


def _pnl_pct(pnl, total_invested):
    """Return % return relative to total invested, or None if indeterminate."""
    if total_invested and total_invested != 0:
        return (pnl / total_invested) * 100
    return None
