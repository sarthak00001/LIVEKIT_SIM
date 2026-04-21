const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

<<<<<<< HEAD
<<<<<<< HEAD
// ─── CLI FLAG ────────────────────────────────────────────────
// Dry run:  node create_slots.js --dry-run
// Live run: node create_slots.js
const DRY_RUN = process.argv.includes('--dry-run');
// ─────────────────────────────────────────────────────────────

// ============================================================
// CONFIGURATION — edit these values
// ============================================================
=======
const DRY_RUN = process.argv.includes('--dry-run');

>>>>>>> 7e3a667ed2431b003047ca3f6907eb926e5bf87e
=======
const DRY_RUN = process.argv.includes('--dry-run');

>>>>>>> company/main
const CONFIG = {
  adminUrl: 'https://admin.thefuture.university/masterclasses',

  masterclasses: [
    {
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> company/main
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 12',
      slotTime: '12:00',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 12.5',
      slotTime: '12:30',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
<<<<<<< HEAD
>>>>>>> 7e3a667ed2431b003047ca3f6907eb926e5bf87e
=======
>>>>>>> company/main
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 1',
      slotTime: '13:00',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
<<<<<<< HEAD
<<<<<<< HEAD
    // Add more masterclasses here:
    // {
    //   name: 'Masterclass on AI Based Super Investing with Akshay Gulati 1.5',
    //   slotTime: '14:00',
    //   whatsappLink: 'https://chat.whatsapp.com/XXXXXXX',
    //   daysAhead: 10,
    // },
=======
=======
>>>>>>> company/main
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 1.5',
      slotTime: '13:30',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 2',
      slotTime: '14:00',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 2.5',
      slotTime: '14:30',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 3',
      slotTime: '15:00',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 3.5',
      slotTime: '15:30',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 4',
      slotTime: '16:00',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 4.5',
      slotTime: '16:30',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 5',
      slotTime: '17:00',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 5.5',
      slotTime: '17:30',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
    {
      name: 'Masterclass on AI Based Super Investing with Akshay Gulati 6',
      slotTime: '18:00',
      whatsappLink: 'https://chat.whatsapp.com/DL383bbdPkmJXTvDChmrC8',
      daysAhead: 10,
    },
<<<<<<< HEAD
>>>>>>> 7e3a667ed2431b003047ca3f6907eb926e5bf87e
=======
>>>>>>> company/main
  ],

  authStatePath: path.join(__dirname, 'auth_state.json'),
  logPath: path.join(__dirname, 'slot_creation_log.json'),
  headless: false,

  // Dry run only — dates that already exist (to simulate duplicate skipping).
  // Update this list to match what's currently on your admin page.
  simulatedExistingDates: ['2026-04-08'],
};
// ============================================================

function getDateStrings(daysAhead, slotTime) {
  const dates = [];
  const today = new Date();
  for (let i = 0; i <= daysAhead; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() + i);
    const yyyy = d.getFullYear();
    const mm   = String(d.getMonth() + 1).padStart(2, '0');
    const dd   = String(d.getDate()).padStart(2, '0');
    dates.push(`${yyyy}-${mm}-${dd}T${slotTime}`);
  }
  return dates;
}

function formatReadable(dateTimeStr) {
  return new Date(dateTimeStr).toLocaleString('en-IN', {
    weekday: 'short', day: '2-digit', month: 'short',
    year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true,
  });
}

function log(logs, masterclass, date, status, detail) {
  const entry = { timestamp: new Date().toISOString(), masterclass, date, status, detail };
  logs.push(entry);
  const icon = status === 'SUCCESS' ? '✅' : status === 'SKIPPED' ? '⏭️ ' : '❌';
  console.log(`${icon} [${status}] ${masterclass} | ${date} | ${detail}`);
}

// ─────────────────────────────────────────────────────────────
// DRY RUN — no browser, prints exactly what live run will do
// ─────────────────────────────────────────────────────────────
function runDryRun() {
  console.log('');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  DRY RUN — No browser opened. No slots created.');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`  Run date : ${new Date().toLocaleString('en-IN')}`);
  console.log(`  Admin URL: ${CONFIG.adminUrl}`);
  console.log('');

  const existingSet = new Set(CONFIG.simulatedExistingDates);
  let grandTotal = 0, grandCreate = 0, grandSkip = 0;

  for (const mc of CONFIG.masterclasses) {
    const dates = getDateStrings(mc.daysAhead, mc.slotTime);
    let willCreate = 0, willSkip = 0;

    console.log(`┌─ Masterclass`);
    console.log(`│  Name    : ${mc.name}`);
    console.log(`│  Time    : ${mc.slotTime}`);
    console.log(`│  WA Link : ${mc.whatsappLink}`);
    console.log(`│  Days    : today + ${mc.daysAhead} = ${dates.length} slots`);
    console.log(`│`);
    console.log(`│  Slots:`);

    dates.forEach((dt, i) => {
      const dateOnly    = dt.split('T')[0];
      const isDuplicate = existingSet.has(dateOnly);
      const label       = i === 0 ? ' ← TODAY' : '';
      const action      = isDuplicate ? '⏭️  SKIP (already exists)' : '✅ CREATE';
      console.log(`│    ${String(i + 1).padStart(2)}. ${formatReadable(dt)}${label}`);
      console.log(`│        Action  : ${action}`);
      if (!isDuplicate) {
        console.log(`│        Input   : ${dt}`);
        console.log(`│        WhatsApp: ${mc.whatsappLink}`);
        willCreate++;
      } else {
        willSkip++;
      }
    });

    grandTotal  += dates.length;
    grandCreate += willCreate;
    grandSkip   += willSkip;

    console.log(`└─ ${dates.length} slots — ✅ ${willCreate} to create, ⏭️  ${willSkip} to skip`);
    console.log('');
  }

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`  TOTAL : ${grandTotal} slots — ✅ ${grandCreate} to create, ⏭️  ${grandSkip} to skip`);
  console.log('');
  console.log('  Looks correct? Run the live script:');
  console.log('    node create_slots.js');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('');
}

// ─────────────────────────────────────────────────────────────
// LIVE RUN — browser automation
// ─────────────────────────────────────────────────────────────
async function saveAuthState(browser) {
  console.log('\n📌 AUTH STATE NOT FOUND.');
  console.log('A browser window will open. Log in manually, then press ENTER here.\n');
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(CONFIG.adminUrl);
  await new Promise(r => process.stdin.once('data', r));
  await context.storageState({ path: CONFIG.authStatePath });
  await context.close();
  console.log('✅ Auth state saved to', CONFIG.authStatePath);
}

async function createSlotsForMasterclass(context, mc, logs) {
  const page = await context.newPage();

  try {
    console.log(`\n🔍 Searching for: "${mc.name}"`);
    await page.goto(CONFIG.adminUrl, { waitUntil: 'networkidle' });

    const searchInput = page.locator('input[type="text"], input[placeholder*="search" i]').first();
    await searchInput.fill(mc.name);
    await page.waitForTimeout(1000);

    const link = page.locator(`a:has-text("${mc.name}")`).first();
    if (!await link.count()) {
      log(logs, mc.name, 'N/A', 'FAILED', 'Masterclass not found in search results');
      await page.close();
      return;
    }
    await link.click();
    await page.waitForLoadState('networkidle');
    console.log(`✅ Opened masterclass page`);

    // Read existing dates from the table
    const existingSlotDates = await page.locator('table tbody tr td:nth-child(2), td[data-label="START DATE-TIME"]').allTextContents();
    const existingDateSet = new Set(
      existingSlotDates.map(text => {
        const d = new Date(text.trim());
        if (isNaN(d)) return null;
        return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
      }).filter(Boolean)
    );
    console.log(`  📅 Existing slots: ${existingDateSet.size > 0 ? [...existingDateSet].join(', ') : 'none'}`);

    const dates = getDateStrings(mc.daysAhead, mc.slotTime);

    for (const dateTimeValue of dates) {
      const dateOnly = dateTimeValue.split('T')[0];

      if (existingDateSet.has(dateOnly)) {
        log(logs, mc.name, dateTimeValue, 'SKIPPED', `Slot for ${dateOnly} already exists`);
        continue;
      }

      await page.locator('button:has-text("Add Slot")').last().click();
      await page.waitForSelector('text=Add Slot', { state: 'visible' });
      await page.waitForTimeout(300);

      await page.locator('input[type="datetime-local"]').fill(dateTimeValue);
      await page.locator('input[placeholder*="WhatsApp" i], input[placeholder*="whatsapp" i]').fill(mc.whatsappLink);
      await page.locator('dialog button:has-text("Add Slot"), [role="dialog"] button:has-text("Add Slot"), .modal button:has-text("Add Slot")').click();
      await page.waitForTimeout(1500);

      const successVisible = await page.locator('text=/Masterclass Slot Created/i').isVisible().catch(() => false);
      const errorToast     = page.locator('text=/error|failed|invalid/i');
      const errorVisible   = await errorToast.isVisible().catch(() => false);

      if (successVisible) {
        log(logs, mc.name, dateTimeValue, 'SUCCESS', 'Toast confirmed: Masterclass Slot Created');
        existingDateSet.add(dateOnly);
      } else if (errorVisible) {
        const errorText = await errorToast.textContent().catch(() => 'unknown error');
        log(logs, mc.name, dateTimeValue, 'FAILED', `Error toast: ${errorText.trim()}`);
      } else {
        const humanDate = new Date(dateTimeValue).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
        const rowExists = await page.locator(`text=${humanDate}`).count();
        log(logs, mc.name, dateTimeValue,
          rowExists > 0 ? 'SUCCESS' : 'FAILED',
          rowExists > 0 ? 'Slot row found in table' : 'No toast and no row found');
        if (rowExists > 0) existingDateSet.add(dateOnly);
      }

      await page.waitForTimeout(500);
    }

  } catch (err) {
    log(logs, mc.name, 'N/A', 'FAILED', `Unhandled error: ${err.message}`);
    const ssPath = path.join(__dirname, `error_${Date.now()}.png`);
    await page.screenshot({ path: ssPath });
    console.log(`  📸 Screenshot: ${ssPath}`);
  } finally {
    await page.close();
  }
}

async function runLive() {
  const logs = [];
  const startTime = new Date().toISOString();
  console.log(`\n🚀 Slot Automation Started — ${startTime}`);

  const browser = await chromium.launch({ headless: CONFIG.headless });

  if (!fs.existsSync(CONFIG.authStatePath)) {
    await saveAuthState(browser);
  }

  const context = await browser.newContext({ storageState: CONFIG.authStatePath });

  for (const mc of CONFIG.masterclasses) {
    await createSlotsForMasterclass(context, mc, logs);
  }

  await context.close();
  await browser.close();

  const report = {
    runAt: startTime,
    completedAt: new Date().toISOString(),
    total:   logs.length,
    success: logs.filter(l => l.status === 'SUCCESS').length,
    failed:  logs.filter(l => l.status === 'FAILED').length,
    skipped: logs.filter(l => l.status === 'SKIPPED').length,
    entries: logs,
  };
  fs.writeFileSync(CONFIG.logPath, JSON.stringify(report, null, 2));

  console.log(`\n📋 SUMMARY`);
  console.log(`   ✅ Success : ${report.success}`);
  console.log(`   ❌ Failed  : ${report.failed}`);
  console.log(`   ⏭️  Skipped : ${report.skipped}`);
  console.log(`   Log saved  : ${CONFIG.logPath}`);
}

// ─── ENTRY POINT ─────────────────────────────────────────────
if (DRY_RUN) {
  runDryRun();
} else {
  runLive().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}