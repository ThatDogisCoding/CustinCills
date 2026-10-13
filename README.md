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

   Add Mindbody login email and password under `MINDBODY_LOGIN_EMAIL` and
   `MINDBODY_LOGIN_PASSWORD` in `.env`. Keep these credentials out of source
   control.

3. **Enable the Playwright browser session** (optional):

   ```bash
   py -m pip install -e ".[browser]"
   py -m playwright install chromium
   ```

   The browser automation window can test the Mindbody staff login and reports
   working, done, verification-needed, or error status. Keep login credentials
   in `.env`; the browser is visible by default so you can complete any
   verification prompts. The other source integrations and data collection
   workflows are not implemented yet.

4. **Launch the dashboard UI**:

   ```bash
   py main.py
   ```

5. **Run Phase 1 CLI**:

   ```bash
   py main.py report info
   py main.py report rules
   py main.py report weeks
   ```

   Or directly:

   ```bash
   py -m business_report.cli info
   ```

6. **Run tests**:

   ```bash
   py -m pytest
   ```

## Legacy task reporter

```bash
py main.py legacy
```

## Project structure

```
docs/business_rules.md     Business rules (Phase 1)
docs/excel_layout.md       Target spreadsheet layout
src/business_report/
  ui/app.py                Redline dashboard (default: py main.py)
  config.py                Settings and reporting period
  domain/                  Pydantic models (Member, FreeTrial, etc.)
  services/rules.py        Metric calculation helpers
  util/                    Dates, logging
  cli.py                   Command-line interface
```

## Baseline

First parity target: **Weekly Business Snapshot for week of 7/27/2026** (see business rules doc).
