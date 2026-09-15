"""Business rule calculations (see docs/business_rules.md)."""

from typing import Optional


def show_percentage(showed: int, scheduled: int) -> Optional[float]:
    """Show % = Showed / Scheduled * 100. Returns None if scheduled is 0."""
    if scheduled == 0:
        return None
    return round(showed / scheduled * 100, 1)


def sold_percentage(sold: int, scheduled: int) -> Optional[float]:
    """Sold % = Sold / Scheduled * 100. Returns None if scheduled is 0."""
    if scheduled == 0:
        return None
    return round(sold / scheduled * 100, 1)


def format_percentage(value: Optional[float]) -> str:
    """Format as a decimal percentage to match the business snapshot."""
    if value is None:
        return "N/A"
    return f"{value}%"
