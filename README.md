# Business Reporting Automation System

Automated weekly business reporting that pulls data from **Mindbody**, **GoHighLevel**, and **Axle**, calculates metrics, and generates an Excel workbook.

See [docs/business_rules.md](docs/business_rules.md) for confirmed business rules and open items requiring stakeholder sign-off.

## Project status

| Phase | Status |
|-------|--------|
| 1 — Requirements & scaffold | Done |
| 2 — API investigation | Not started |
| 3 — Database | Not started |
| 4+ — Sync, matching, Excel, UI | Not started |

## Setup

1. **Install dependencies** (editable install recommended):

   ```bash
   py -m pip install -e .
   py -m pip install -e ".[dev]"
   ```

   Or install from requirements only:

   ```bash
   py -m pip install -r requirements.txt
   ```

2. **Configure environment**:

   ```bash
   copy .env.example .env
   ```

   Fill in API keys as they become available (Phase 2).

3. **Run Phase 1 CLI**:

   ```bash
   py main.py report info
   py main.py report rules
   py main.py report weeks
   ```

   Or directly:

   ```bash
   py -m business_report.cli info
   ```

4. **Run tests**:

   ```bash
   py -m pytest
   ```

## Project structure

```
docs/business_rules.md     Business rules (Phase 1)
src/business_report/
  config.py                Settings and reporting period
  domain/                  Pydantic models (Member, FreeTrial, etc.)
  services/rules.py        Metric calculation helpers
  util/                    Dates, logging
  cli.py                   Command-line interface
```

## Baseline

First parity target: **Weekly Business Snapshot for week of 7/27/2026** (see business rules doc).
