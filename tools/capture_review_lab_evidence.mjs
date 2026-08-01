import { access, mkdir, rm } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const run = promisify(execFile);
const base = (process.env.BASE_URL || 'http://127.0.0.1:4173').replace(/\/$/, '');
const outputDir = 'assets/lovetypes/lab';
const temporaryDir = 'output/playwright/lab-evidence-source';

async function loadPlaywright() {
  const candidates = [
    'playwright',
    process.env.PLAYWRIGHT_MODULE_PATH,
    '/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs',
  ].filter(Boolean);
  let lastError;
  for (const candidate of candidates) {
    try {
      const module = await import(candidate);
      return module.chromium ? module : module.default;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

async function saveEvidence(page, slug, detail = false) {
  const stem = `${slug}${detail ? '-detail' : ''}`;
  const png = `${temporaryDir}/${stem}.png`;
  const webp = `${outputDir}/${stem}.webp`;
  await page.waitForTimeout(120);
  await page.screenshot({ path: png, fullPage: false });
  await run(process.env.PYTHON || 'python3', [
    '-c',
    'from PIL import Image; import sys; image=Image.open(sys.argv[1]).convert("RGB"); image.save(sys.argv[2], "WEBP", quality=88, method=6)',
    png,
    webp,
  ]);
  await access(webp);
}

async function newPage(browser, options = {}) {
  const context = await browser.newContext({
    viewport: { width: 1200, height: 750 },
    reducedMotion: options.reducedMotion ? 'reduce' : 'no-preference',
    javaScriptEnabled: options.javaScriptEnabled !== false,
  });
  const page = await context.newPage();
  return { context, page };
}

async function open(page, path) {
  const response = await page.goto(`${base}${path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  if (!response || response.status() >= 400) throw new Error(`${path} returned ${response?.status() || 'no response'}`);
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
}

async function completeQuiz(page, answers) {
  await page.locator('[data-quiz-start]').first().click();
  for (const answer of answers) {
    await page.locator(`.quiz-option[data-type="${answer}"]`).click();
    await page.locator('.quiz-next').click();
  }
  await page.locator('[data-quiz-result]').waitFor({ state: 'visible', timeout: 10000 });
}

async function quizScoring(browser) {
  const { context, page } = await newPage(browser);
  await open(page, '/');
  await completeQuiz(page, ['W', 'T', 'G', 'S', 'P', 'W', 'T', 'G', 'S', 'P', 'W', 'T', 'G', 'S', 'P']);
  await page.locator('.quiz-result-card').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'quiz-scoring-test');
  await page.locator('.quiz-score-card').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'quiz-scoring-test', true);
  await context.close();
}

async function resultConsistency(browser) {
  const { context, page } = await newPage(browser);
  await open(page, '/');
  await completeQuiz(page, ['W', 'W', 'W', 'W', 'T', 'T', 'T', 'G', 'G', 'G', 'S', 'S', 'P', 'P', 'P']);
  await page.locator('.quiz-result-card').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'result-consistency-test');
  await page.locator('.quiz-score-card').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'result-consistency-test', true);
  await context.close();
}

async function localStorageEvidence(browser) {
  const { context, page } = await newPage(browser);
  await open(page, '/repair-plan/#repair-worksheet');
  const values = ['艾莉絲 · 肯定的言詞', 'LT-LOCAL-ONLY-0731', '希望今晚有十分鐘專心聽', '使用關係羅盤整理一句請求'];
  for (let index = 0; index < values.length; index += 1) {
    await page.locator(`[data-repair-worksheet] [data-field="${index}"]`).fill(values[index]);
  }
  await page.waitForTimeout(500);
  await page.locator('[data-repair-worksheet]').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'local-storage-privacy-test');
  await page.locator('[data-clear-worksheet]').click();
  await page.locator('[data-repair-worksheet]').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'local-storage-privacy-test', true);
  await context.close();
}

async function sharePrivacy(browser) {
  const { context, page } = await newPage(browser);
  await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: base });
  await open(page, '/');
  await completeQuiz(page, Array(15).fill('S'));
  await page.locator('.quiz-collector-card').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'share-card-privacy-test');
  await page.locator('[data-copy-result]').click();
  await page.locator('.quiz-tools').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'share-card-privacy-test', true);
  await context.close();
}

async function compassSafety(browser) {
  const { context, page } = await newPage(browser);
  await open(page, '/compass/#relationship-compass-tool');
  await page.locator('[name="self"]').selectOption('W');
  await page.locator('[name="partner"]').selectOption('T');
  await page.locator('[name="status"]').selectOption('dating');
  await page.locator('[name="issue"]').selectOption('feeling-unheard');
  await page.locator('[data-compass-form] button[type="submit"]').click();
  await page.locator('[data-compass-result]').waitFor({ state: 'visible' });
  await page.locator('.compass-result-head').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'compatibility-safety-test');
  await page.locator('.compass-result-next-steps').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'compatibility-safety-test', true);
  await context.close();
}

async function repairUsability(browser) {
  const { context, page } = await newPage(browser, { reducedMotion: true });
  await open(page, '/repair-plan/#repair-worksheet');
  const values = ['艾莉絲', '昨晚訊息被略過', '希望今晚有十分鐘專心聽', '週日回看'];
  for (let index = 0; index < values.length; index += 1) {
    await page.locator(`[data-repair-worksheet] [data-field="${index}"]`).fill(values[index]);
  }
  await page.locator('[data-repair-worksheet]').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'repair-plan-usability-test');
  await page.locator('[data-field="2"]').fill('希望今晚能留十分鐘，不用立刻解決問題，只要先聽我說完；如果現在不方便，也可以提出一個今晚可行的替代時間。'.repeat(3));
  await page.locator('[data-field="2"]').focus();
  await page.locator('[data-field="2"]').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'repair-plan-usability-test', true);
  await context.close();
}

async function keyboardEvidence(browser) {
  const { context, page } = await newPage(browser, { reducedMotion: true });
  await open(page, '/');
  await page.keyboard.press('Tab');
  await saveEvidence(page, 'keyboard-accessibility-test');
  await page.locator('[data-quiz-start]').first().focus();
  await page.locator('[data-quiz-start]').first().scrollIntoViewIfNeeded();
  await saveEvidence(page, 'keyboard-accessibility-test', true);
  await context.close();
}

async function slowNetworkEvidence(browser) {
  const { context, page } = await newPage(browser, { javaScriptEnabled: false });
  await open(page, '/guides/share-your-result/');
  await page.locator('h1').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'slow-network-performance-test');
  await open(page, '/about/');
  await page.locator('#editorial-method').scrollIntoViewIfNeeded();
  await saveEvidence(page, 'slow-network-performance-test', true);
  await context.close();
}

await mkdir(outputDir, { recursive: true });
await rm(temporaryDir, { recursive: true, force: true });
await mkdir(temporaryDir, { recursive: true });

const { chromium } = await loadPlaywright();
const browser = await chromium.launch({ headless: true });
const cases = [quizScoring, resultConsistency, localStorageEvidence, sharePrivacy, compassSafety, repairUsability, keyboardEvidence, slowNetworkEvidence];
try {
  for (const capture of cases) {
    await capture(browser);
    console.error(`[lab-evidence] ${capture.name}`);
  }
} finally {
  await browser.close();
}

console.log(`lab_evidence_reports=${cases.length}`);
console.log(`lab_evidence_images=${cases.length * 2}`);
