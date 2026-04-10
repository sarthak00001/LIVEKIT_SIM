# Masterclass Slot Automation

## One-Time Setup

### 1. Install dependencies
```bash
npm install playwright
npx playwright install chromium
```

### 2. Save your login session (do this once)
```bash
node create_slots.js
```
- A browser window opens on the admin login page
- Log in manually with your credentials
- Come back to the terminal and press **ENTER**
- Your session is saved to `auth_state.json` — keep this file secret

After this, the script uses the saved session and never asks for login again (until the session expires — then just delete `auth_state.json` and repeat step 2).

---

## Configuration (inside `create_slots.js`)

```js
masterclasses: [
  {
    name: 'Masterclass on AI Based Super Investing with Akshay Gulati 1',
    slotTime: '13:00',   // 24h format — 1:00 PM
    whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
    daysAhead: 10,       // slots for today + next 10 days
  },
  // Add more entries for other masterclasses
]
```

To change timing per masterclass, just change `slotTime` per entry.

---

## Running

```bash
node create_slots.js
```

- Set `headless: true` in config for silent background runs
- Set `headless: false` to watch the browser work (good for debugging)

---

## Scheduling (run automatically every day)

Add a cron job to run at 9 AM daily:
```bash
crontab -e
# Add this line:
0 9 * * * cd /path/to/script && node create_slots.js >> cron.log 2>&1
```

---

## Logs

Every run writes to `slot_creation_log.json`:
```json
{
  "runAt": "2026-04-08T09:00:00Z",
  "total": 11,
  "success": 11,
  "failed": 0,
  "entries": [
    {
      "timestamp": "...",
      "masterclass": "Masterclass on AI Based...",
      "date": "2026-04-08T13:00",
      "status": "SUCCESS",
      "detail": "Toast confirmed: Masterclass Slot Created"
    }
  ]
}
```

Status values: `SUCCESS` | `FAILED` | `SKIPPED`

If a slot fails, the `detail` field explains why (error toast text, missing element, etc.) and a screenshot is saved alongside the log.
