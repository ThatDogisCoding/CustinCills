# Excel Layout — Weekly Business Snapshot

Reference document based on **Weekly Business Snapshot_2026 - Week of 7_27_2026.pdf**.

The real report is a **single dashboard-style workbook** (not separate abstract tabs for every section). Sections are laid out side-by-side where noted. Automation should reproduce this layout as closely as possible.

Output filename: `Weekly Business Snapshot_YYYY - Week of M_D_YYYY.xlsx`

---

## Page 1 — Main snapshot

### Header

```
Business Snapshot for Week 7/27/2026
```

Use the **Monday start date** of the reporting week (e.g. `7/27/2026`).

---

### Section A — Free Trials Conversion Rates

**Source:** GoHighLevel

| Column | Description |
|--------|-------------|
| Week of | Week start date (M/D/YYYY) |
| Scheduled | Count |
| Showed | Count |
| Showed % | Whole-number percent (e.g. `62%`) |
| Sold | Count |
| Sold % | Whole-number percent (e.g. `23%`) |
| Be a advocate of bring a friend | Weekly coaching note / reminder (manual or rotating template) |

**Rows:** Current week plus **3 prior weeks** (4 weeks total).

**Baseline (7/27/2026 week):**

| Week of | Scheduled | Showed | Showed % | Sold | Sold % | Note |
|---------|-----------|--------|----------|------|--------|------|
| 7/27/2026 | 13 | 8 | 62% | 3 | 23% | When's the last time we gave out a character band |
| 7/20/2026 | 14 | 10 | 71% | 7 | 50% | |
| 7/13/2026 | 16 | 11 | 69% | 4 | 25% | |
| 7/6/2026 | 16 | 7 | 44% | 2 | 13% | |

Percent display: round to **whole percent** (62%, not 61.5%).

---

### Section B — Total Members (left) + Total Terminations (right)

Two blocks on the same row.

#### B1 — Total Members

**Source:** Mindbody

| Column | Description |
|--------|-------------|
| Week of | Week start date |
| Active Members | Count as of that week |

4 weeks of history (same dates as free trials).

#### B2 — Total Terminations

**Source:** Mindbody

| Column | Description |
|--------|-------------|
| Week | Week start date |
| Total | Count **and names in the same cell**, e.g. `4 Ahlaila Dasher, Johan Tan, Caleb Nickens, Omar Wright` |

**Baseline terminations (7/27 week):** `4 Ahlaila Dasher, Johan Tan, Caleb Nickens, Omar Wright`

**Coaching note** (below terminations block, full width):

> Take some time and give these parents/athletes calls. Focus on building the relationship. Our comments should show the relationship that is growing. Do not be a transaction for them.

This note may be static template text each week.

---

### Section C — New Members (left) + Members at Risk (right)

Two blocks side-by-side.

#### C1 — New Members

**Source:** Mindbody

| Column | Description |
|--------|-------------|
| Name | Member full name |
| Date Joined | M/D or M/D/YYYY |
| Demotu | Yes / No (assessment/onboarding field) |
| NAO Completed | Yes / No |

**Scope:** Members who joined during the reporting period (and possibly recent joins still tracked — confirm with staff).

**Baseline sample rows:** Samir Twyman, Williams Archie, Jasmine Edwards, Chase Evans, Nasir Jackson, etc.

#### C2 — Members at Risk

**Source:** Axle

| Column | Description |
|--------|-------------|
| Name | Member name |
| Follow Up | Follow-up date (M/D or M/D/YYYY) |
| Business comments | Staff notes (multi-line) |
| Member Experience Follow - Up | Additional follow-up notes (multi-line) |

Comments must be preserved **verbatim** — not summarized by the app.

**Baseline sample:** Alani Dennis, David Fonyad, Demarcus Young, Austin Holmes, etc. with detailed relationship notes.

---

### Section D — 4-week Member Follow Up

**Source:** Mindbody

**Title format:**

```
4-week Member Follow Up (6/29-7/05) (source: Mindbody)
```

The date range in the title is the **join-date cohort window** (~4 weeks before the reporting week). For week of 7/27/2026, the cohort is members who joined **6/29–7/05**.

| Column | Description |
|--------|-------------|
| Name | Auto-populated from Mindbody |
| Comments | Blank for staff |
| Coaches' Comments | Blank for staff |

**Baseline names:** Aarav Khanal, Aarogya Khanal, Archie Williams, Compton Zuri, Jelks Emma, etc.

---

## Page 2 — Small Habits Dashboard

### Section E — Small Habits Make Huge Impact Dashboard

| Column | Description |
|--------|-------------|
| Metric | Habit / operational checklist item |
| Status | Rating text |
| Owner | `Training` or `Business` |

**Status values (from baseline):**

- `Didn't Meet Expectations, Needs Major Improvement`
- `Meet Some Expectations, Need Some Improvement`
- `Meet or Exceeded Expectations, Keep Up the Good Work`

**Baseline metrics:**

| Metric | Status | Owner |
|--------|--------|-------|
| Complete New Athlete Orientation | Didn't Meet Expectations, Needs Major Improvement | Training |
| Publish Demotu Weekly Reports | Didn't Meet Expectations, Needs Major Improvement | Training |
| Publish 2 IG Posts (reviewed and approved) | Didn't Meet Expectations, Needs Major Improvement | Training |
| Character Bands Distributed/Documented | Didn't Meet Expectations, Needs Major Improvement | Training |
| Conduct Outreach | Didn't Meet Expectations, Needs Major Improvement | Training |
| Display Free Trial Names | Meet Some Expectations, Need Some Improvement | Business |
| Collect Free Trial Info Prior to Session | Meet Some Expectations, Need Some Improvement | Business |
| Execute Free Trials Tour (5Ts) | Meet Some Expectations, Need Some Improvement | Business |
| Follow Up w Free Trials | Didn't Meet Expectations, Needs Major Improvement | Business |
| HL Buckets Up-to Date | Didn't Meet Expectations, Needs Major Improvement | Business |
| Follow Up w/4 week Members | Didn't Meet Expectations, Needs Major Improvement | Business |
| Training Floor Clean | Meet or Exceeded Expectations, Keep Up the Good Work | Training |
| Bathroom Supplies Stocked | Meet Some Expectations, Need Some Improvement | Business |
| Lobby Clean | Meet or Exceeded Expectations, Keep Up the Good Work | Business |
| Basketball Court Clean | Meet or Exceeded Expectations, Keep Up the Good Work | Training |
| Equipment Organized | Meet or Exceeded Expectations, Keep Up the Good Work | Training |
| Weight Room Floor and Equipment Clean | Meet or Exceeded Expectations, Keep Up the Good Work | Training |

**Footer note:**

> Be sure to take a look at these small habits. These habits help to not just maintain membership growth but also member activity.

**Automation note:** This section appears to be **manually scored** each week. Options:
- Leave as editable template rows in Excel (Phase 7)
- Optional future UI for staff to fill before export
- Not sourced from Mindbody/GHL/Axle

---

## Layout diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Business Snapshot for Week 7/27/2026                       │
├─────────────────────────────────────────────────────────────┤
│  Free Trials Conversion Rates (GoHighLevel)                 │
│  [4-week table + coaching note column]                      │
├──────────────────────────┬──────────────────────────────────┤
│  Total Members           │  Total Terminations              │
│  (Mindbody)              │  (Mindbody)                      │
├──────────────────────────┴──────────────────────────────────┤
│  [coaching note — terminations]                             │
├──────────────────────────┬──────────────────────────────────┤
│  New Members             │  Members at Risk                 │
│  (Mindbody)              │  (Axle)                          │
├──────────────────────────┴──────────────────────────────────┤
│  4-week Member Follow Up (cohort date range)                │
│  (Mindbody)                                                 │
└─────────────────────────────────────────────────────────────┘

Page 2:
┌─────────────────────────────────────────────────────────────┐
│  Small Habits Make Huge Impact Dashboard                    │
│  [Metric | Status | Owner]                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Differences from initial project PDF

| Initial plan | Actual snapshot |
|--------------|-----------------|
| 9 separate Excel tabs | Dashboard layout (1–2 pages/sections) |
| Terminations on own sheet | Count + names combined in one cell |
| NAO only on new members | **Demotu** + **NAO Completed** columns |
| Executive Summary tab | Metrics embedded in section tables |
| Follow Up Needed sheet | Not a separate section in this snapshot |
| Raw Data sheet | Not in manual snapshot (optional for automation audit) |

---

## Parity checklist (7/27/2026)

Use this when validating generated output:

- [ ] Free trials: 13 / 8 / 62% / 3 / 23% for 7/27 row
- [ ] Active members: 148 for 7/27 row
- [ ] Terminations: `4 Ahlaila Dasher, Johan Tan, Caleb Nickens, Omar Wright`
- [ ] New members list includes Samir Twyman, Archie Williams, Jasmine Edwards, …
- [ ] At-risk list includes Alani Dennis, David Fonyad, … with full comments
- [ ] 4-week follow-up title: `(6/29-7/05)` with 17+ names
- [ ] Small Habits section present with 17 metrics
