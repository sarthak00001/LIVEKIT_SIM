"""
TheFuture.University - Live Class Meeting Automation
=====================================================
Usage:
  First time (saves login session):
    python create_meetings.py --login

  Dry run (see what it WOULD do, no actual clicks):
    python create_meetings.py --dry-run

  Real run (creates all meetings):
    python create_meetings.py --run

Requirements:
  pip install playwright
  playwright install chromium
"""

import asyncio
import argparse
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeoutError

# ─── CONFIG ────────────────────────────────────────────────────────────────────

BASE_URL  = "https://admin.thefuture.university/liveclasses"
AUTH_FILE = "auth_state.json"

TODAY = datetime.now()

# "10 Apr, 2026"  — matches slot option text
# Windows: replace with TODAY.strftime("%#d %b, %Y")
TODAY_SLOT_STR  = TODAY.strftime("%-d %b, %Y")

# "10/04"  — matches dashboard table start time column
TODAY_TABLE_STR = TODAY.strftime("%d/%m")

# ─── MEETING SCHEDULE ──────────────────────────────────────────────────────────

MEETINGS = [
    ("Masterclass on AI Based Super Investing with Akshay Gulati 12",   "12:00PM", "Livekit New 10"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 12.5", "12:30PM", "Livekit New 09"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 1",    "1:00PM",  "Livekit New 10"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 1.5",  "1:30PM",  "Livekit New 09"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 2",    "2:00PM",  "Livekit New 10"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 2.5",  "2:30PM",  "Livekit New 09"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 3",    "3:00PM",  "Livekit New 10"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 3.5",  "3:30PM",  "Livekit New 09"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 4",    "4:00PM",  "Livekit New 10"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 4.5",  "4:30PM",  "Livekit New 09"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 5",    "5:00PM",  "Livekit New 10"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 5.5",  "5:30PM",  "Livekit New 09"),
    ("Masterclass on AI Based Super Investing with Akshay Gulati 6",    "6:00PM",  "Livekit New 10"),
]

# ─── LOGGING ───────────────────────────────────────────────────────────────────

def log(msg: str, mode: str = "INFO"):
    icons = {"INFO": "   ", "SKIP": "⏭  ", "OK": "✓  ", "FAIL": "✗  ", "DRY": "○  "}
    print(f"{icons.get(mode, '   ')}{msg}", flush=True)

# ─── DUPLICATE DETECTION ───────────────────────────────────────────────────────

def normalise_slot_time(slot_time: str) -> str:
    """Convert "12:00PM" -> "12:00 pm" to match dashboard table format."""
    try:
        t = datetime.strptime(slot_time.strip(), "%I:%M%p")
        return t.strftime("%-I:%M %p").lower()
    except Exception:
        s = slot_time.strip()
        if s.upper().endswith("AM") or s.upper().endswith("PM"):
            return (s[:-2] + " " + s[-2:]).lower()
        return s.lower()


async def scrape_existing_meetings(page: Page) -> list:
    rows = await page.query_selector_all("table tbody tr")
    existing = []
    for row in rows:
        try:
            name_cell  = await row.query_selector("td:nth-child(2)")
            start_cell = await row.query_selector("td:nth-child(8)")
            if not name_cell or not start_cell:
                continue
            name_text  = (await name_cell.inner_text()).strip()
            start_text = (await start_cell.inner_text()).strip()
            existing.append((name_text, start_text))
        except Exception:
            continue
    return existing


def is_duplicate(existing: list, name: str, slot_time: str) -> bool:
    norm_time = normalise_slot_time(slot_time)
    for ex_name, ex_start in existing:
        if (name.strip().lower() in ex_name.strip().lower()
                and TODAY_TABLE_STR in ex_start
                and norm_time in ex_start.lower()):
            return True
    return False

# ─── JS HELPERS ────────────────────────────────────────────────────────────────

async def wait_for_modal(page: Page):
    """Poll DOM until the dialog form exists."""
    await page.wait_for_function(
        "() => document.querySelector('[role=\"dialog\"] form') !== null",
        timeout=8000
    )
    await page.wait_for_timeout(600)


async def close_modal_if_open(page: Page):
    try:
        exists = await page.evaluate(
            "() => document.querySelector('[role=\"dialog\"]') !== null"
        )
        if exists:
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(700)
    except Exception:
        pass


async def js_set_select(page: Page, select_name: str, value: str):
    """
    Set a React-controlled <select> by name attribute using native value setter
    so React's synthetic event system picks up the change.
    """
    result = await page.evaluate(
        """([name, val]) => {
            const el = document.querySelector(`select[name="${name}"]`);
            if (!el) return 'NOT_FOUND:' + name;
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLSelectElement.prototype, 'value'
            ).set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input',  { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            return 'OK';
        }""",
        [select_name, value]
    )
    if result != "OK":
        raise Exception(f"js_set_select failed: {result}")
    await page.wait_for_timeout(600)


# ─── FIX: MASTERCLASS SEARCH INPUT ────────────────────────────────────────────
# The "Select Masterclass" field is a plain <input> with placeholder
# "Search for masterclasses..." that must be CLICKED first to activate,
# then typed into. Only after typing do [role="option"] items appear.

async def wait_for_masterclass_input(page: Page):
    """
    Wait for the masterclass search input to appear in the DOM.
    It renders only after classType is set to MASTERCLASS.
    """
    await page.wait_for_function(
        """() => {
            const inputs = [...document.querySelectorAll('[role="dialog"] input')];
            return inputs.some(i =>
                i.placeholder && i.placeholder.toLowerCase().includes('masterclass')
            );
        }""",
        timeout=8000
    )
    await page.wait_for_timeout(400)


async def click_and_fill_masterclass(page: Page, search_text: str):
    """
    1. Click the masterclass search input to open/activate the dropdown.
    2. Type the search text character-by-character so React onChange fires.
    3. Wait for [role="option"] items to appear.
    4. Click the best matching option via JS (bypasses portal interception).
    """
    # Step 1: Click the input via JS to focus + open the dropdown
    clicked = await page.evaluate(
        """() => {
            const inputs = [...document.querySelectorAll('[role="dialog"] input')];
            const input = inputs.find(i =>
                i.placeholder && i.placeholder.toLowerCase().includes('masterclass')
            );
            if (!input) return false;
            input.click();
            input.focus();
            return true;
        }"""
    )
    if not clicked:
        raise Exception("Masterclass search input not found in dialog")
    await page.wait_for_timeout(400)

    # Step 2: Type into the now-active input using Playwright keyboard
    # (real key events so React's onChange / onInput handlers fire)
    input_locator = page.locator(
        '[role="dialog"] input[placeholder*="masterclass" i], '
        '[role="dialog"] input[placeholder*="Masterclass"]'
    ).first
    await input_locator.press_sequentially(search_text, delay=40)
    await page.wait_for_timeout(1500)

    # Step 3: Wait for dropdown options to appear
    await page.wait_for_function(
        "() => document.querySelectorAll('[role=\"option\"]').length > 0",
        timeout=8000
    )
    await page.wait_for_timeout(400)

    # Step 4: Click the best-matching option via JS
    clicked_option = await page.evaluate(
        """(text) => {
            const options = [...document.querySelectorAll('[role="option"]')];
            let opt = options.find(o => o.textContent.trim() === text);
            if (!opt) opt = options.find(o => o.textContent.trim().includes(text));
            if (!opt) {
                const available = options.map(o => o.textContent.trim()).join(' || ');
                return 'NOT_FOUND: ' + available;
            }
            opt.click();
            return 'OK';
        }""",
        search_text
    )
    if not clicked_option.startswith("OK"):
        raise Exception(f"Masterclass option not found. {clicked_option}")
    await page.wait_for_timeout(700)

# ──────────────────────────────────────────────────────────────────────────────


async def find_slot_value(page: Page, slot_time: str):
    """
    Find the <option> value in select[name="slotId"] whose text contains
    today's date AND the slot time. Returns None if not found.
    Slot option text example: " 10 Apr, 2026 12:00PM"
    """
    options = await page.query_selector_all('select[name="slotId"] option')
    for opt in options:
        val  = await opt.get_attribute("value")
        text = (await opt.inner_text()).strip()
        if not val:
            continue
        if TODAY_SLOT_STR in text and slot_time in text:
            return val
    return None


async def js_click_button(page: Page, text: str):
    """Click an enabled button inside the dialog by its text content via JS."""
    clicked = await page.evaluate(
        """(text) => {
            const btns = [...document.querySelectorAll('[role="dialog"] button')];
            const btn = btns.find(b => b.textContent.trim() === text && !b.disabled);
            if (!btn) return false;
            btn.click();
            return true;
        }""",
        text
    )
    if not clicked:
        raise Exception(f"Button '{text}' not found or disabled in dialog")
    await page.wait_for_timeout(800)


async def js_click_server_card(page: Page, server_name: str):
    """Click the server card whose h5 text matches server_name via JS."""
    clicked = await page.evaluate(
        """(name) => {
            const cards = [...document.querySelectorAll('.space-y-4 .border.rounded-lg')];
            const card = cards.find(c => {
                const h5 = c.querySelector('h5');
                return h5 && h5.textContent.trim().toLowerCase() === name.toLowerCase();
            });
            if (!card) {
                const available = cards.map(c => {
                    const h = c.querySelector('h5');
                    return h ? h.textContent.trim() : '';
                }).join(' | ');
                return 'NOT_FOUND: ' + available;
            }
            card.click();
            return 'OK';
        }""",
        server_name
    )
    if not clicked.startswith("OK"):
        raise Exception(f"Server card not found. {clicked}")
    await page.wait_for_timeout(600)

# ─── CORE FLOW ─────────────────────────────────────────────────────────────────

async def create_one_meeting(page: Page, name: str, slot_time: str, server_name: str) -> str:
    """
    Full Add Meeting modal flow for one masterclass.

    ACTUAL PAGE FLOW (confirmed from HTML):
    ----------------------------------------
    Page 1 (visible):  uiType + classType selects
                       → after classType=MASTERCLASS, search input + slotId + duration appear
    Click Next         → hides page 1 fields, shows server list
    Click Submit       → submits form

    Returns: "created" | "skipped_no_slot" | "failed"
    """

    # ── 1. Open modal ───────────────────────────────────────────────────────
    add_btn = page.get_by_role("button", name="Add Meeting")
    await add_btn.click()
    await wait_for_modal(page)
    log("Modal open")

    # ── 2. Set UI Type = WEBINAR ────────────────────────────────────────────
    await js_set_select(page, "uiType", "WEBINAR")
    log("UI Type → WEBINAR")

    # ── 3. Set Class Type = MASTERCLASS ─────────────────────────────────────
    await js_set_select(page, "classType", "MASTERCLASS")
    log("Class Type → MASTERCLASS")

    # ── 4. Wait for search input, then click + type + select masterclass ────
    #       (FIXED: was using [role="combobox"] focus — field is a plain input
    #        that must be clicked first to open its dropdown)
    await wait_for_masterclass_input(page)
    log(f"Search input appeared, clicking + searching: {name}")
    await click_and_fill_masterclass(page, name)
    log("Masterclass selected")

    # ── 5. Select today's slot ───────────────────────────────────────────────
    slot_value = await find_slot_value(page, slot_time)
    if slot_value is None:
        log(f"No slot for today ({TODAY_SLOT_STR} {slot_time})", "SKIP")
        await close_modal_if_open(page)
        return "skipped_no_slot"
    await js_set_select(page, "slotId", slot_value)
    log(f"Slot → {slot_time}")

    # ── 6. Set Duration = 6 hours ────────────────────────────────────────────
    await js_set_select(page, "duration", "6")
    log("Duration → 6 hours")

    # ── 7. Click Next → reveals server selection ─────────────────────────────
    await js_click_button(page, "Next")
    log("Clicked Next → server selection")

    # ── 8. Select server card ────────────────────────────────────────────────
    await js_click_server_card(page, server_name)
    log(f"Server → {server_name}")

    # ── 9. Submit ────────────────────────────────────────────────────────────
    submitted = await page.evaluate(
        """() => {
            const btn = document.querySelector('[role="dialog"] button[type="submit"]');
            if (!btn) return false;
            btn.click();
            return true;
        }"""
    )
    if not submitted:
        raise Exception("Submit button not found")
    log("Submitted")

    await page.wait_for_timeout(2500)

    # Check success toast
    try:
        await page.wait_for_function(
            "() => document.body.innerText.includes('Meeting created successfully')",
            timeout=5000
        )
        return "created"
    except PWTimeoutError:
        return "failed"

# ─── LOGIN ─────────────────────────────────────────────────────────────────────

async def do_login(playwright):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page    = await context.new_page()
    await page.goto(BASE_URL)

    print("\n" + "="*55)
    print("  Browser opened. Please log in manually.")
    print("  Once you can see the Live Classes dashboard,")
    print("  come back here and press ENTER to save session.")
    print("="*55)
    input("\n  Press ENTER after logging in >>> ")

    await context.storage_state(path=AUTH_FILE)
    print(f"\n  ✓ Session saved to '{AUTH_FILE}'")
    print("  You can now run --dry-run or --run\n")
    await browser.close()

# ─── MAIN AUTOMATION ───────────────────────────────────────────────────────────

async def run_automation(dry_run: bool):

    if not dry_run and not os.path.exists(AUTH_FILE):
        print(f"\nERROR: '{AUTH_FILE}' not found. Run --login first.\n")
        sys.exit(1)

    print("\n" + "="*60)
    print("  TheFuture.University  —  Meeting Automation")
    print(f"  Mode  : {'DRY RUN (no changes)' if dry_run else 'LIVE (creating meetings)'}")
    print(f"  Date  : {TODAY_SLOT_STR}")
    print(f"  Total : {len(MEETINGS)} meetings to process")
    print("="*60 + "\n")

    if dry_run:
        for name, slot_time, server in MEETINGS:
            short = name.replace(
                "Masterclass on AI Based Super Investing with Akshay Gulati ", "Gulati ")
            log(f"[{slot_time}]  [{server}]  {short}", "DRY")
        print("\n  Dry run complete. Zero changes made.\n")
        return

    results = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=AUTH_FILE)
        page    = await context.new_page()

        await page.goto(BASE_URL)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1500)

        for name, slot_time, server in MEETINGS:
            short = name.replace(
                "Masterclass on AI Based Super Investing with Akshay Gulati ", "Gulati ")
            print(f"\n── {short}  [{slot_time}]  [{server}] ──", flush=True)

            # Duplicate check before touching modal
            existing = await scrape_existing_meetings(page)
            if is_duplicate(existing, name, slot_time):
                log("Already exists — skipping", "SKIP")
                results.append((name, slot_time, server, "skipped_duplicate"))
                await page.reload()
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(1000)
                continue

            status = "failed"
            try:
                status = await create_one_meeting(page, name, slot_time, server)
                if status == "created":
                    log("Created successfully", "OK")
                elif status == "skipped_no_slot":
                    pass
                else:
                    log("Submitted but no success toast — check manually", "FAIL")
            except Exception as e:
                log(f"Error: {e}", "FAIL")
                await close_modal_if_open(page)
                status = "failed"

            results.append((name, slot_time, server, status))

            # Reload between meetings for clean React state
            await page.wait_for_timeout(1000)
            await page.reload()
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1200)

        await browser.close()

    # ── SUMMARY ──────────────────────────────────────────────────────────────
    created = [r for r in results if r[3] == "created"]
    skipped = [r for r in results if r[3].startswith("skipped")]
    failed  = [r for r in results if r[3] == "failed"]

    print("\n" + "="*65)
    print(f"  SUMMARY — {TODAY_SLOT_STR}")
    print("="*65)
    for name, slot_time, server, status in results:
        short = name.replace(
            "Masterclass on AI Based Super Investing with Akshay Gulati ", "Gulati ")
        icon   = {"created": "✓", "failed": "✗"}.get(status, "⏭")
        reason = {
            "skipped_duplicate": "(already existed)",
            "skipped_no_slot":   "(no slot for today)",
            "failed":            "(error — check manually)",
            "created":           "",
        }.get(status, "")
        print(f"  {icon}  {slot_time:<8}  {server:<14}  {short}  {reason}")

    print("="*65)
    print(f"  Created : {len(created)}  |  Skipped : {len(skipped)}  |  Failed : {len(failed)}")
    print("="*65 + "\n")

# ─── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TheFuture.University meeting automation")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--login",   action="store_true",
                       help="Open browser for manual login and save session")
    group.add_argument("--dry-run", action="store_true",
                       help="Simulate — prints what would happen, zero browser actions")
    group.add_argument("--run",     action="store_true",
                       help="Create all meetings for today")
    args = parser.parse_args()

    async def main():
        async with async_playwright() as p:
            if args.login:
                await do_login(p)
            else:
                await run_automation(dry_run=args.dry_run)

    asyncio.run(main())