## What it does
At each scheduled time, the script:
1. Opens the portal in a visible Chrome window
2. Goes to Create New Simulation
3. Selects the source meeting (Akshay Gulati, 27th March)
4. Selects the correct target (LIVE) meeting for that time slot
5. Adds both video URLs and the time offset (26 min 40 sec)
6. Skips timelines
7. Stops just before Start Simulation (DRY RUN mode) OR clicks it (LIVE mode)

---

## First-time setup (do this once)
**1. Install dependencies**
```bash
pip install playwright requests
playwright install chromium
```
**2. Log in to the portal (one time only)**
```bash
python3 login.py
```
A browser will open. Click **Sign in with Google** and log in with your admin Google account. Once you see the Simulations Dashboard, come back to Terminal and press **Enter**. Your session is saved — you won't need to do this again.

---

## Testing (DRY RUN mode)

`DRY_RUN = True` is set by default. In this mode the script does everything but **stops just before clicking Start Simulation** and saves a screenshot instead.

**Test any slot:**
```bash
python3 run_simulation.py 13:27
```
---

## Going live (real runs)

**1. Open `run_simulation.py` in VS Code**

**2. Find this line near the top:**
```python
DRY_RUN = True ->> DRY_RUN = True
```
**3. Activate the scheduler (runs at all 12 times automatically):**
```bash
bash schedule.sh
```
---

## Checking logs

Each slot has its own log file in the `logs/` folder:
```bash
# Watch live log for the 11:57 slot
tail -f logs/simulation_1157.log

# Check any slot
cat logs/simulation_1327.log
```

---

## Stopping the scheduler

```bash
bash stop.sh
```

This removes all 12 scheduled jobs. The script won't run automatically anymore.

To restart it:
```bash
bash schedule.sh
```

---

## If something breaks

1. Check `error_screenshot.png` in the folder — saved automatically on failure
2. Check the log file for that slot in `logs/`
3. Run manually to see what happens:
```bash
python3 run_simulation.py 13:27
```
---

## Files in this folder

| File | What it does |
|------|-------------|
| `run_simulation.py` | Main script |
| `login.py` | One-time Google login |
| `setup.sh` | Installs dependencies |
| `schedule.sh` | Activates all 12 scheduled slots |
| `stop.sh` | Removes all scheduled slots |
| `auth_state.json` | Saved login session (auto-created) |
| `logs/` | Log files, one per slot |
| `error_screenshot.png` | Auto-saved when script fails |
| `dryrun_verify_*.png` | Screenshot from dry run test |