"""
Simulation Auto-Creator — admin.thefuture.university
=====================================================
Fully hardcoded. No sheet reading. No guessing.

Schedule (run at these times):
  11:57 → target: Gulati 12
  12:27 → target: Gulati 12.5
  12:57 → target: Gulati 1
  13:27 → target: Gulati 1.5
  13:57 → target: Gulati 2
  14:27 → target: Gulati 2.5
  ...etc

Usage:
  python3 run_simulation.py              ← runs forever, auto-triggers at scheduled times
  python3 run_simulation.py 13:57        ← manual override for a specific slot

On first run: log in with Google in the browser that opens.
After that: runs silently (headless).
"""

import os
import sys
import time
import schedule
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ─────────────────────────────────────────────────────────────
# HARDCODED DATA — everything the script needs, no sheet access
# ─────────────────────────────────────────────────────────────

# URLs — screen share first (main display), camera second
CAMERA_URL  = "https://tfu-media.s3.ap-south-1.amazonaws.com/recordings/akshay+screen+share+final.mp4"
SCREENSH_URL = "https://tfu-media.s3.ap-south-1.amazonaws.com/recordings/akshay27thcamera.mp4"

# Time offset — same for all slots
OFFSET_HOURS   = "0"
OFFSET_MINUTES = "26"
OFFSET_SECONDS = "40"

# Source meeting — always the same
SOURCE_MASTERCLASS_FILTER = "Masterclass on AI Based Investing with Akshay Gulati"
SOURCE_MEETING_NAME       = "Masterclass on AI Based Investing with Akshay Gulati"

# Schedule: run_time (HH:MM) → exact target meeting name
SCHEDULE = {
    "11:57": "Masterclass on AI Based Super Investing with Akshay Gulati 12",
    "12:27": "Masterclass on AI Based Super Investing with Akshay Gulati 12.5",
    "12:57": "Masterclass on AI Based Super Investing with Akshay Gulati 1",
    "13:27": "Masterclass on AI Based Super Investing with Akshay Gulati 1.5",
    "13:57": "Masterclass on AI Based Super Investing with Akshay Gulati 2",
    "14:27": "Masterclass on AI Based Super Investing with Akshay Gulati 2.5",
    "14:57": "Masterclass on AI Based Super Investing with Akshay Gulati 3",
    "15:27": "Masterclass on AI Based Super Investing with Akshay Gulati 3.5",
    "15:57": "Masterclass on AI Based Super Investing with Akshay Gulati 4",
    "16:27": "Masterclass on AI Based Super Investing with Akshay Gulati 4.5",
    "16:57": "Masterclass on AI Based Super Investing with Akshay Gulati 5",
    "17:27": "Masterclass on AI Based Super Investing with Akshay Gulati 5.5",
}

# Portal URLs
SIMULATIONS_URL = "https://admin.thefuture.university/liveclasses/simulation"
AUTH_STATE_FILE = "auth_state.json"

# ─────────────────────────────────────────────────────────────
# DRY RUN MODE
# True  = does everything but STOPS before "Start Simulation"
#         saves a screenshot so you can verify it looks correct
# False = runs for real, clicks "Start Simulation"
# ─────────────────────────────────────────────────────────────
DRY_RUN = False


# ─────────────────────────────────────────────────────────────
# DETERMINE WHICH SLOT TO RUN
# ─────────────────────────────────────────────────────────────

def get_current_slot():
    """
    Match current time to the closest scheduled slot (within ±5 minutes).
    OR accept a manual override via command line: python3 run_simulation.py 11:57
    Returns (slot_time_str, target_meeting_name) or exits if no match.
    """
    if len(sys.argv) > 1:
        override = sys.argv[1]
        if override in SCHEDULE:
            print(f"🎯 Manual override: slot {override}")
            return override, SCHEDULE[override]
        else:
            print(f"❌ '{override}' is not a valid slot.")
            print(f"   Valid slots: {', '.join(SCHEDULE.keys())}")
            sys.exit(1)

    now = datetime.now()
    now_str = now.strftime("%H:%M")
    now_minutes = now.hour * 60 + now.minute

    print(f"🕐 Current time: {now_str}")

    for slot_time, target_name in SCHEDULE.items():
        slot_h, slot_m = map(int, slot_time.split(":"))
        slot_minutes = slot_h * 60 + slot_m
        diff = abs(now_minutes - slot_minutes)

        if diff <= 5:
            print(f"✅ Matched slot: {slot_time} → {target_name}")
            return slot_time, target_name

    print(f"⚠️  No scheduled slot matches current time {now_str}.")
    print(f"   Scheduled slots: {', '.join(SCHEDULE.keys())}")
    print(f"   Exiting — nothing to do right now.")
    sys.exit(0)


# ─────────────────────────────────────────────────────────────
# BROWSER AUTOMATION
# ─────────────────────────────────────────────────────────────

def run_simulation(target_meeting_name):
    auth_exists = os.path.exists(AUTH_STATE_FILE)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )

        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            storage_state=AUTH_STATE_FILE if auth_exists else None
        )
        page = context.new_page()

        try:
            # ── 1. Navigate & check login ──────────────────────────────
            print(f"\n🌐 Opening simulations page...")
            page.goto(SIMULATIONS_URL, wait_until="domcontentloaded", timeout=120000)
            time.sleep(3)

            if "login" in page.url.lower() or "accounts.google" in page.url.lower():
                print("\n🔐 Not logged in.")
                print("   Please log in with your Google account in the browser.")
                print("   Waiting up to 5 minutes...")
                page.wait_for_url("**/admin.thefuture.university/**", timeout=300000)
                print("✅ Logged in!")
                context.storage_state(path=AUTH_STATE_FILE)
                print("💾 Session saved. Future runs will be headless.")

            # ── 2. Go directly to Create Simulation page ──────────────
            print("🌐 Navigating to Create Simulation...")
            page.goto(
                "https://admin.thefuture.university/liveclasses/simulation/new-simulation",
                wait_until="domcontentloaded",
                timeout=120000
            )
            time.sleep(2)

            # ══════════════════════════════════════════════════════════
            # STEP 1: Select Meeting
            # ══════════════════════════════════════════════════════════
            print("\n── STEP 1: Select Meeting ──")

            # Step 1a: Type in the masterclass filter search box
            print("   Typing masterclass filter...")
            filter_input = page.locator("input[placeholder*='Search masterclasses']")
            filter_input.click()
            filter_input.fill("")
            time.sleep(0.3)
            filter_input.type(SOURCE_MASTERCLASS_FILTER, delay=40)

            # Step 1b: Wait for dropdown to load
            print("   Waiting for dropdown to load...")
            page.wait_for_function(
                "() => !document.body.innerText.includes('Loading masterclasses')",
                timeout=30000
            )
            time.sleep(0.5)

            # Step 1c: Click the correct option in the dropdown
            print("   Clicking dropdown option...")
            dropdown_container = page.locator("div.absolute.z-10")
            option = dropdown_container.get_by_text(SOURCE_MASTERCLASS_FILTER).first
            option.click()
            print("   ✅ Masterclass filter selected")
            time.sleep(2)

            # Step 1d: Set date range to 27/03/2026
            print("   Setting date range to 27/03/2026...")
            date_inputs = page.locator("input[type='date']").all()
            if len(date_inputs) >= 2:
                date_inputs[0].click()
                date_inputs[0].evaluate("el => el.value = ''")
                date_inputs[0].fill("2026-03-27")
                date_inputs[0].press("Tab")
                time.sleep(0.3)
                date_inputs[1].click()
                date_inputs[1].evaluate("el => el.value = ''")
                date_inputs[1].fill("2026-03-27")
                date_inputs[1].press("Tab")
                time.sleep(2)

            # Step 1e: Click the source meeting card
            print(f"   Selecting source meeting...")
            source_card = page.locator("h3").filter(
                has_text="Masterclass on AI Based Investing with Akshay Gulati"
            ).first
            source_card.click()
            print("   ✅ Source meeting selected")
            time.sleep(1.5)

            # Step 1f: Click the target meeting
            print(f"   Selecting target meeting: {target_meeting_name}")
            target_card = page.locator("h3").filter(has_text=target_meeting_name).first
            target_card.scroll_into_view_if_needed()
            target_card.click()
            print("   ✅ Target meeting selected")
            time.sleep(1)

            # Step 1g: Click Next Step
            next_btn = page.locator("button:has-text('Next Step')")
            next_btn.click()
            page.wait_for_load_state("domcontentloaded", timeout=60000)
            time.sleep(2)
            print("   ✅ Step 1 done")

            # ══════════════════════════════════════════════════════════
            # STEP 2: Add Video URLs
            # ══════════════════════════════════════════════════════════
            print("\n── STEP 2: Add Video URLs ──")

            # Fill time offset — Hours, Minutes, Seconds
            number_inputs = page.locator("input[type='number']").all()
            if len(number_inputs) >= 3:
                number_inputs[0].fill(OFFSET_HOURS)
                number_inputs[1].fill(OFFSET_MINUTES)
                number_inputs[2].fill(OFFSET_SECONDS)
                print(f"   Time offset: {OFFSET_HOURS}h {OFFSET_MINUTES}m {OFFSET_SECONDS}s")
            else:
                print(f"   ⚠️  Could not find 3 number inputs for time offset. Found: {len(number_inputs)}")

            # URL input field
            url_input = page.locator(
                "input[placeholder*='video.mp4'], input[placeholder*='https://example'], input[placeholder*='m3u8']"
            ).first

            # Add Camera URL (first)
            print(f"   Adding Camera URL (1st)...")
            url_input.fill(CAMERA_URL)
            page.locator("button:has-text('Add URL')").click()
            time.sleep(1.5)

            # Add Screen Share URL (second)
            print(f"   Adding Screen Share URL (2nd)...")
            url_input.fill(SCREENSH_URL)
            page.locator("button:has-text('Add URL')").click()
            time.sleep(1.5)

            # Verify both URLs were added
            added = page.locator("text=Main, text=Participant").count()
            print(f"   URLs added: {added} visible")

            # Next Step
            page.locator("button:has-text('Next Step')").click()
            page.wait_for_load_state("networkidle", timeout=60000)
            time.sleep(1.5)
            print("   ✅ Step 2 done")

            # ══════════════════════════════════════════════════════════
            # STEP 3: Edit Timelines — no changes, just Next Step
            # ══════════════════════════════════════════════════════════
            print("\n── STEP 3: Edit Timelines (skip) ──")
            page.locator("button:has-text('Next Step')").click()
            page.wait_for_load_state("networkidle", timeout=60000)
            time.sleep(1.5)
            print("   ✅ Step 3 done")

            # ══════════════════════════════════════════════════════════
            # STEP 4: Verify → Start Simulation
            # ══════════════════════════════════════════════════════════
            print("\n── STEP 4: Verify ──")

            if DRY_RUN:
                screenshot_path = f"dryrun_verify_{datetime.now().strftime('%H%M%S')}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"\n{'='*50}")
                print(f"🧪 DRY RUN — Stopped before Start Simulation")
                print(f"   Screenshot saved: {screenshot_path}")
                print(f"   Open it and verify everything looks correct.")
                print(f"   If happy → set DRY_RUN = False and run for real.")
                print(f"{'='*50}")
            else:
                page.locator("button:has-text('Start Simulation')").click()
                time.sleep(2)
                context.storage_state(path=AUTH_STATE_FILE)
                print(f"\n{'='*50}")
                print(f"✅ SIMULATION STARTED SUCCESSFULLY")
                print(f"   Target: {target_meeting_name}")
                print(f"   Time:   {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*50}")

        except PlaywrightTimeout as e:
            print(f"\n❌ TIMEOUT: {e}")
            page.screenshot(path="error_screenshot.png")
            print("📸 Saved error_screenshot.png — open it to see where it got stuck")
            raise
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            try:
                page.screenshot(path="error_screenshot.png")
                print("📸 Saved error_screenshot.png")
            except:
                pass
            raise
        finally:
            time.sleep(2)
            browser.close()


# ─────────────────────────────────────────────────────────────
# SCHEDULER JOB — called automatically at each scheduled time
# ─────────────────────────────────────────────────────────────

def scheduled_job(slot_time, target_meeting_name):
    print(f"\n{'='*50}")
    print(f"  ⏰ Scheduled trigger: {slot_time}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    try:
        run_simulation(target_meeting_name)
    except Exception as e:
        print(f"\n❌ Slot {slot_time} failed: {e}")
        print(f"   Will continue waiting for next slot...")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Simulation Auto-Creator")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Manual override — run immediately and exit
    if len(sys.argv) > 1:
        slot_time, target_meeting_name = get_current_slot()
        run_simulation(target_meeting_name)
        sys.exit(0)

    # Auto mode — register all slots and loop forever
    print("\n🕐 Scheduler started. Running all day automatically.")
    print(f"   Slots scheduled: {', '.join(SCHEDULE.keys())}")
    print(f"   Waiting for next slot...\n")

    for slot_time, target_meeting_name in SCHEDULE.items():
        # Use default args to capture loop variables correctly
        schedule.every().day.at(slot_time).do(
            scheduled_job,
            slot_time=slot_time,
            target_meeting_name=target_meeting_name
        )

    while True:
        schedule.run_pending()
        time.sleep(30)