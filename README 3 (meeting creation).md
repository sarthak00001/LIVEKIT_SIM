# TheFuture.University — Live Class Meeting Automation

Automates the creation of LiveKit meeting rooms on the TheFuture.University admin dashboard. Handles duplicate detection, slot matching, server selection, and toast-based result reporting.

---

## Requirements

**Python 3.8+** and the Playwright library:

```bash
pip install playwright
playwright install chromium
```

---

## First-Time Setup (Login)

The script uses a saved browser session so you only log in once. Run:

```bash
python create_meetings.py --login
```

A browser window will open. Log in manually, navigate to the Live Classes dashboard, then come back to the terminal and press **Enter**. Your session is saved to `auth_state.json` in the same folder.

> ⚠️ Keep `auth_state.json` private — it contains your login session.

---

## Usage

### Dry Run (no changes made)
Preview exactly what the script would do — no browser automation, no meetings created:

```bash
python create_meetings.py --dry-run
```

### Live Run (creates meetings)
Creates all scheduled meetings for today:

```bash
python create_meetings.py --run
```

---

## What It Does

For each meeting in the schedule, the script:

1. Opens the **Add Meeting** modal
2. Sets **UI Type** → `WEBINAR`
3. Sets **Class Type** → `MASTERCLASS`
4. Clicks and types into the masterclass search field, then selects the matching option
5. Picks today's **slot** from the dropdown
6. Sets **Duration** → 6 hours
7. Clicks **Next** and selects the assigned **LiveKit server**
8. Submits the form and reads the **toast notification**

Between each meeting, the page is reloaded to ensure a clean React state.

---

## Duplicate Detection

Before opening the modal for any meeting, the script scans the existing table on the dashboard. If a meeting with the same name, date, and time already exists, it is **skipped automatically** — no duplicate will be created.

---

## Output & Toast Reporting

During the run, each meeting prints live status. After submission, the script captures the actual toast message shown by the page and reports it:

```
   Toast: "Meeting created successfully"
✓  Created successfully
```

In the final summary, each meeting shows one of the following:

| Icon | Status | Meaning |
|------|--------|---------|
| `✓` | Created | Meeting created successfully |
| `⏭` | Skipped (already existed) | Duplicate found in dashboard table |
| `⏭` | Skipped (no slot for today) | No matching slot found in dropdown |
| `✗` | `(toast: <message>)` | Page returned an error toast — message shown |
| `✗` | `(no toast — check manually)` | Form submitted but no toast appeared |
| `✗` | `(error — check manually)` | Python/Playwright exception during automation |

Example summary output:

```
=================================================================
  SUMMARY — 10 Apr, 2026
=================================================================
  ✓  12:00PM  Livekit New 09  Gulati 12
  ✓  12:30PM  Livekit New 10  Gulati 12.5
  ⏭  1:00PM   Livekit New 10  Gulati 1    (already existed)
  ✗  1:30PM   Livekit New 09  Gulati 1.5  (toast: Slot already booked)
=================================================================
  Created : 2  |  Skipped : 1  |  Failed : 1
=================================================================
```

---

## Meeting Schedule

The schedule is defined in the `MEETINGS` list near the top of the script. Each entry is a tuple of:

```python
("Masterclass name", "Time", "Server name")
```

Edit this list to add, remove, or change meetings. Times must match the format used in the slot dropdown (e.g. `12:00PM`, `1:30PM`).

---

## File Structure

```
create_meetings.py   # Main automation script
auth_state.json      # Saved login session (created by --login, gitignore this)
README.md            # This file
```

---

## Troubleshooting

**`auth_state.json` not found**
Run `--login` first to save your session.

**Masterclass option not found**
The search text in `MEETINGS` must match the masterclass name exactly as it appears in the dropdown. Check for extra spaces or punctuation.

**No slot for today**
The masterclass doesn't have a slot configured for today's date in the admin panel. Create the slot manually first.

**No toast / check manually**
The form may have submitted but the page didn't show a recognisable toast. Open the dashboard and verify whether the meeting was created.

**Session expired**
Re-run `--login` to refresh `auth_state.json`.