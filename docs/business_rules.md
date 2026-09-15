# Business Rules — Weekly Business Report

This document defines the business logic for the Business Reporting Automation System.
Rules marked **CONFIRMED** are taken from the project requirements PDF or the 7/27/2026 baseline report.
Rules marked **TBD** require stakeholder sign-off before implementation.

---

## 1. Reporting Period

| Rule | Status | Definition |
|------|--------|------------|
| Week boundaries | **CONFIRMED** | Monday (inclusive) through Sunday (inclusive). Example baseline: 07/27/2026 – 08/02/2026. |
| Configurable period | **CONFIRMED** | User may select current week, a previous week, or a custom date range. |
| Time zone | **TBD** | Confirm business time zone for date boundaries (e.g. `America/New_York`). |
| "As of" timestamp | **TBD** | Confirm whether membership counts are as-of end of Sunday or end of business day Sunday. |

---

## 2. Data Sources

| System | Role | Status |
|--------|------|--------|
| Mindbody | Primary membership source: active members, terminations, new members, join dates, 4-week follow-up | **CONFIRMED** |
| GoHighLevel | Free trial source: scheduled, showed, sold, pipeline/stage, staff assignment | **CONFIRMED** |
| Axle | Members at risk: risk status, follow-up, business comments, member experience | **CONFIRMED** |

The application must not invent at-risk definitions; Axle is the source of truth for at-risk status.

---

## 3. Free Trial Metrics

Applies to trials whose relevant dates fall within the reporting period (exact date field **TBD** — trial date vs scheduled date).

| Metric | Formula | Status |
|--------|---------|--------|
| Scheduled | Count of trials marked scheduled in period | **CONFIRMED** |
| Showed | Count of trials marked showed in period | **CONFIRMED** |
| Sold | Count of trials marked sold in period | **CONFIRMED** |
| Show % | `Showed ÷ Scheduled × 100` | **CONFIRMED** |
| Sold % | `Sold ÷ Scheduled × 100` | **CONFIRMED** (PDF baseline uses scheduled as denominator) |
| Zero scheduled | If Scheduled = 0, show % and sold % display as `N/A` (not divide-by-zero) | **CONFIRMED** (implementation default) |

### GoHighLevel status mapping

| GHL field / stage | Maps to | Status |
|-------------------|---------|--------|
| Scheduled | `scheduled = true` | **TBD** — confirm pipeline stage or custom field |
| Showed | `showed = true` | **TBD** |
| Sold | `sold = true` | **TBD** |

Baseline comparison week (7/27/2026): Scheduled 13, Showed 8 (62%), Sold 3 (23%).

---

## 4. Membership Metrics

| Metric | Definition | Status |
|--------|------------|--------|
| Active members | Total active members at end of reporting period | **CONFIRMED** (concept); exact API field **TBD** |
| Terminations | Members whose termination date falls within the reporting period | **CONFIRMED** |
| New members | Members whose join date falls within the reporting period | **CONFIRMED** |

Baseline comparison (7/27/2026): Active 148, Terminations 4.

Prior-week columns appear on Executive Summary and Membership sheets for week-over-week comparison.

---

## 5. Termination Tracking

Terminations appear in the **Total Terminations** block alongside Total Members.

Format: count and names in one cell, e.g. `4 Ahlaila Dasher, Johan Tan, Caleb Nickens, Omar Wright` (**CONFIRMED** from baseline).

Where available from Mindbody, also store termination date, membership type, and reason internally for audit (not necessarily shown in snapshot cell).

---

## 6. New Member Tracking

A member qualifies as **new** when their join date is within `[period_start, period_end]`.

**New Members** section includes:

- Member name (**CONFIRMED**)
- Date joined (**CONFIRMED**)
- Demotu — Yes/No (**CONFIRMED** from baseline snapshot)
- NAO Completed — Yes/No (**CONFIRMED**)

See [excel_layout.md](excel_layout.md) for column layout.

---

## 7. New Athlete Orientation (NAO)

| Status | Meaning | Status |
|--------|---------|--------|
| Yes | Orientation completed | **CONFIRMED** |
| No | Not completed | **CONFIRMED** |
| Unknown | Status not available | **CONFIRMED** |

| Rule | Status |
|------|--------|
| NAO data source | **TBD** — Mindbody custom field, GoHighLevel tag, manual entry column, or other |
| Demotu data source | **TBD** — confirm Mindbody/GHL field for Demotu Yes/No |
| Follow-up trigger | Members with NAO = No or Unknown may appear on **Follow Up Needed** | **CONFIRMED** (concept) |

---

## 8. Members at Risk

| Rule | Status |
|------|--------|
| Source | Axle only — do not calculate risk in-app | **CONFIRMED** |
| Preserve comments | Business comments and member experience text copied verbatim | **CONFIRMED** |
| Follow-up fields | Follow-up date, status, comments as provided by Axle | **CONFIRMED** |

Staff-entered context (e.g. "Left VM", "Out of town") must not be reduced to a boolean flag.

---

## 9. Four-Week Member Follow-Up

| Rule | Status |
|------|--------|
| Section title | **CONFIRMED** — includes cohort date range, e.g. `4-week Member Follow Up (6/29-7/05)` |
| Cohort window | Members whose join date falls in the window ~4 weeks before the reporting week | **CONFIRMED** (baseline: 6/29–7/05 for week of 7/27) |
| Sheet columns | Name (auto), Comments (staff), Coaches' Comments (staff) | **CONFIRMED** |
| Auto-populate names only | Staff fills comment columns manually | **CONFIRMED** |

---

## 10. Follow-Up Management

Standard statuses (finalize list with staff):

| Status | Description |
|--------|-------------|
| NOT_STARTED | Default for new follow-ups |
| IN_PROGRESS | Contact attempt underway |
| COMPLETED | Resolved |
| LEFT_VM | Voicemail left |
| NO_RESPONSE | No response after attempts |
| SCHEDULED | Follow-up appointment set |
| RESOLVED | Issue closed |

Each follow-up record tracks: member, reason, assigned to, due date, status, last contact date, contact method, notes (**CONFIRMED** from PDF §16).

---

## 11. Cross-System Matching

Priority order when linking records across Mindbody, GoHighLevel, and Axle:

1. Unique system/member ID (when a crosswalk exists)
2. Email address (normalized, lowercase)
3. Phone number (E.164 normalized)
4. Exact full name
5. Normalized name (case/punctuation stripped)
6. Fuzzy name match (last resort)

| Rule | Status |
|------|--------|
| Never match on name alone when email/phone available | **CONFIRMED** |
| Uncertain matches flagged for review, not auto-merged | **CONFIRMED** |
| Fuzzy threshold | **TBD** — default 90% similarity proposed |

---

## 12. Excel Workbook Structure

Full layout documented in **[excel_layout.md](excel_layout.md)** (from baseline snapshot PDF).

The report is a **dashboard-style workbook**, not nine separate abstract tabs:

| Section | Source | Notes |
|---------|--------|-------|
| Free Trials Conversion Rates | GoHighLevel | 4-week history + coaching note column |
| Total Members | Mindbody | Paired with terminations |
| Total Terminations | Mindbody | Count + names in one cell |
| New Members | Mindbody | Name, Date Joined, Demotu, NAO Completed |
| Members at Risk | Axle | Name, Follow Up date, two comment columns |
| 4-week Member Follow Up | Mindbody | Cohort range in title; blank comment cols |
| Small Habits Dashboard | Manual | Metric, Status, Owner — staff-scored |

Optional for automation (not in manual snapshot): **Raw Data** audit sheet.

---

## 13. Validation & Failure Behavior

| Condition | Behavior | Status |
|-----------|----------|--------|
| API connection failure after retries | Abort report; do not generate a "complete" workbook | **CONFIRMED** |
| Missing optional fields | Warn; include in validation summary | **CONFIRMED** |
| Unmatched cross-system records | Warn; count in validation summary | **CONFIRMED** |
| Partial data with warnings | Generate report with validation banner | **CONFIRMED** |

Example validation output:

```
REPORT VALIDATION
143 members successfully matched
5 members could not be matched
2 free trials have missing status
3 members have missing email addresses
Report generated with warnings.
```

---

## 14. Historical Data

| Rule | Status |
|------|--------|
| Never overwrite previous weeks | **CONFIRMED** |
| Store each reporting period in database | **CONFIRMED** |
| Enable week-over-week, monthly, and trend comparisons | **CONFIRMED** |

---

## 15. Baseline for Parity Testing

First validation target: **Weekly Business Snapshot for week of 7/27/2026**.

Expected Executive Summary values:

| Metric | Current Week | Previous Week |
|--------|--------------|---------------|
| Free Trials Scheduled | 13 | 14 |
| Free Trials Showed | 8 | 10 |
| Show % | 62% | 71% |
| Free Trials Sold | 3 | 7 |
| Sold % | 23% | 50% |
| Active Members | 148 | 149 |
| Terminations | 4 | 2 |

---

## 16. Open Questions (Stakeholder Sign-Off)

- [ ] Business time zone for all date calculations
- [ ] Active member count methodology (snapshot vs average)
- [ ] GoHighLevel field/stage mapping for scheduled, showed, sold
- [ ] NAO data source
- [ ] Four-week follow-up tolerance (exact day vs window)
- [ ] Fuzzy match threshold
- [ ] Final follow-up status enum list

---

## Revision History

| Date | Change |
|------|--------|
| 2026-08-11 | Initial Phase 1 document created from project requirements PDF |
| 2026-08-11 | Updated Excel structure from baseline snapshot PDF (7/27/2026) |
