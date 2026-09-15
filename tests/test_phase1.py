import sys
import types
from datetime import date

import pytest

import main
from business_report.config import ReportingPeriod, WeekStartDay
from business_report.services.rules import format_percentage, show_percentage, sold_percentage
from business_report.util.dates import parse_reporting_period, reporting_period_for_date


def test_reporting_period_monday_sunday_baseline():
    """7/27/2026 baseline week is Monday 7/27 through Sunday 8/2."""
    period = reporting_period_for_date(date(2026, 7, 29), WeekStartDay.MONDAY)
    assert period.start == date(2026, 7, 27)
    assert period.end == date(2026, 8, 2)


def test_parse_reporting_period_from_date_string():
    period = parse_reporting_period("2026-07-27")
    assert period.start == date(2026, 7, 27)
    assert period.end == date(2026, 8, 2)


def test_show_and_sold_percentage_baseline():
    assert show_percentage(8, 13) == 61.5
    assert sold_percentage(3, 13) == 23.1
    assert format_percentage(show_percentage(8, 13)) == "61.5%"
    assert format_percentage(sold_percentage(3, 13)) == "23.1%"


def test_percentage_zero_scheduled():
    assert show_percentage(0, 0) is None
    assert format_percentage(None) == "N/A"


def test_reporting_period_invalid_end():
    with pytest.raises(ValueError):
        ReportingPeriod(date(2026, 8, 2), date(2026, 7, 27))


def test_main_does_not_fallback_to_legacy_task_reporter(monkeypatch):
    legacy_called = {"value": False}

    def fake_legacy_main():
        legacy_called["value"] = True

    fake_legacy_module = types.ModuleType("task_reporter")
    fake_legacy_module.main = fake_legacy_main
    monkeypatch.setitem(sys.modules, "task_reporter", fake_legacy_module)

    report_calls = {"argv": None}

    def fake_report_main(argv=None):
        report_calls["argv"] = argv
        return 0

    monkeypatch.setattr("business_report.cli.main", fake_report_main)
    monkeypatch.setattr(sys, "argv", ["main"])

    with pytest.raises(SystemExit) as exc:
        main.main()

    assert exc.value.code == 0
    assert not legacy_called["value"]
    assert report_calls["argv"] == []
