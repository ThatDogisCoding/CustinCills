"""CLI entry point for the Business Reporting Automation System."""

import argparse
import logging
import sys

from business_report.config import get_settings
from business_report.services.rules import format_percentage, show_percentage, sold_percentage
from business_report.util.dates import (
    current_reporting_period,
    parse_reporting_period,
    reporting_period_for_week_offset,
)
from business_report.util.logging import setup_logging


def _cmd_info(args: argparse.Namespace) -> int:
    settings = get_settings()
    period = parse_reporting_period(args.week, settings)

    print("Business Reporting Automation System")
    print("=" * 40)
    print(f"Reporting period:  {period.start} to {period.end}")
    print(f"Week start day:    {settings.report_week_start_day.value}")
    print(f"Business timezone: {settings.business_timezone}")
    print(f"Output directory:  {settings.output_dir}")
    print()
    print("API configuration:")
    print(f"  Mindbody:     {'configured' if settings.mindbody_api_key else 'not configured'}")
    print(f"  GoHighLevel:  {'configured' if settings.ghl_api_token else 'not configured'}")
    print(f"  Axle:         {'configured' if settings.axle_api_key else 'not configured'}")
    print(f"  Database:     {settings.database_url}")
    print()
    print("See docs/business_rules.md for confirmed rules and open TBD items.")
    return 0


def _cmd_rules(args: argparse.Namespace) -> int:
    print("Confirmed business rules (Phase 1)")
    print("=" * 40)
    print("Reporting week:     Monday through Sunday (inclusive)")
    print("Show %:             Showed / Scheduled * 100")
    print("Sold %:             Sold / Scheduled * 100")
    print("New member:         Join date within reporting period")
    print("Termination:        Termination date within reporting period")
    print("4-week follow-up:   Join date + 28 days within reporting period")
    print("At-risk source:     Axle (not calculated in-app)")
    print("Uncertain matches:  Flagged, not auto-merged")
    print()
    print("Baseline (7/27/2026): Scheduled 13, Showed 8 (62%), Sold 3 (23%)")
    print(f"  Calculated show %: {format_percentage(show_percentage(8, 13))}")
    print(f"  Calculated sold %: {format_percentage(sold_percentage(3, 13))}")
    print()
    print("Open TBD items: see docs/business_rules.md section 16")
    return 0


def _cmd_weeks(args: argparse.Namespace) -> int:
    current = current_reporting_period()
    previous = reporting_period_for_week_offset(-1)
    print(f"Current week:  {current.start} to {current.end}")
    print(f"Previous week: {previous.start} to {previous.end}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="business_report",
        description="Weekly business reporting automation (Mindbody + GoHighLevel + Axle)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info", help="Show configuration and reporting period")
    info.add_argument(
        "--week",
        default="current",
        help="Week selector: current, previous, or YYYY-MM-DD",
    )
    info.set_defaults(func=_cmd_info)

    rules = sub.add_parser("rules", help="Print confirmed business rules")
    rules.set_defaults(func=_cmd_rules)

    weeks = sub.add_parser("weeks", help="Show current and previous reporting weeks")
    weeks.set_defaults(func=_cmd_weeks)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(logging.DEBUG if args.verbose else logging.INFO)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
