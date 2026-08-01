import { access } from 'node:fs/promises';

async function loadPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_MODULE_PATH,
    '/Users/mac/Documents/New project 3/shorts-factory/lovetypes-shorts/node_modules/playwright/index.js',
    '/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs',
    'playwright',
  ].filter(Boolean);

  let lastError;
  for (const candidate of candidates) {
    try {
      if (candidate.startsWith('/')) await access(candidate);
      const playwright = await import(candidate);
      return playwright.chromium ? playwright : playwright.default;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

async function browserLaunchOptions() {
  const candidates = [
    process.env.CHROMIUM_EXECUTABLE_PATH,
    '/Users/mac/Library/Caches/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-mac-arm64/chrome-headless-shell',
    '/Users/mac/Library/Caches/ms-playwright/chromium-1223/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
  ].filter(Boolean);
  for (const executablePath of candidates) {
    try {
      await access(executablePath);
      return { headless: true, executablePath };
    } catch {
      // Continue to Playwright's default browser lookup.
    }
  }
  return { headless: true };
}

const BASE_URL = process.env.BASE_URL || 'https://lovetypes.tw';
const PASSIVE_RESOURCE_TYPES = new Set(['document', 'stylesheet', 'script', 'image', 'font', 'other']);

function makeUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

async function resetBrowserStorage(context, page) {
  await context.clearCookies();
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

function watchNetwork(page) {
  const issues = [];
  const baseOrigin = new URL(BASE_URL).origin;
  const isCloudflareRum = (url, method, type) => (
    url.origin === baseOrigin
    && url.pathname === '/cdn-cgi/rum'
    && ['POST', 'GET'].includes(method)
    && ['xhr', 'fetch', 'ping'].includes(type)
  );
  const isCloudflareInsightsScript = (url, method, type) => (
    method === 'GET'
    && type === 'script'
    && url.origin === 'https://static.cloudflareinsights.com'
    && url.pathname.includes('/beacon.min.js/')
  );
  const isExpectedLocalMetric = (url, method, type) => (
    url.origin === baseOrigin
    && method === 'GET'
    && type === 'fetch'
    && ['/go/quiz-started.gif', '/go/quiz-completed.gif'].includes(url.pathname)
  );
  page.on('request', (request) => {
    const url = new URL(request.url());
    const method = request.method();
    const type = request.resourceType();
    const sameOrigin = url.origin === baseOrigin;
    if (isCloudflareRum(url, method, type) || isCloudflareInsightsScript(url, method, type) || isExpectedLocalMetric(url, method, type)) return;
    if (method !== 'GET' && method !== 'HEAD') {
      issues.push(`${method} ${type} ${url.origin}${url.pathname}`);
    }
    if (!sameOrigin) {
      issues.push(`external ${method} ${type} ${url.origin}${url.pathname}`);
    }
    if (!PASSIVE_RESOURCE_TYPES.has(type)) {
      issues.push(`active ${method} ${type} ${url.origin}${url.pathname}`);
    }
  });
  return issues;
}

async function storageSnapshot(page) {
  return page.evaluate(() => ({
    localKeys: Object.keys(localStorage).sort(),
    sessionKeys: Object.keys(sessionStorage).sort(),
    cookie: document.cookie,
    entries: Object.fromEntries(Object.entries(localStorage)),
  }));
}

function validateQuietStorage(snapshot, issues, scope) {
  const nonNamespaced = snapshot.localKeys.filter((key) => !key.startsWith('lovetypes:'));
  if (nonNamespaced.length) issues.push(`${scope}: non-namespaced localStorage keys: ${nonNamespaced.join(', ')}`);
  if (snapshot.sessionKeys.length) issues.push(`${scope}: sessionStorage should stay empty: ${snapshot.sessionKeys.join(', ')}`);
  if (snapshot.cookie) issues.push(`${scope}: first-party cookies should stay empty`);
}

async function completeQuiz(page) {
  await page.locator('[data-quiz-start]').first().click();
  for (let index = 0; index < 15; index += 1) {
    await page.locator('.quiz-option').first().click();
    await page.locator('.quiz-next').click();
  }
  await page.locator('.quiz-result-card').waitFor({ state: 'visible', timeout: 10000 });
}

async function quizStorageCheck(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true });
  const page = await context.newPage();
  const networkIssues = watchNetwork(page);
  const issues = [];
  const response = await page.goto(makeUrl('/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await resetBrowserStorage(context, page);
  await completeQuiz(page);
  const completed = await storageSnapshot(page);
  validateQuietStorage(completed, issues, 'quiz');
  const quizKeys = completed.localKeys.filter((key) => key.startsWith('lovetypes:') && key.includes('quiz-result'));
  if (quizKeys.length !== 2) issues.push(`quiz: expected 2 namespaced result keys, got ${quizKeys.length}`);
  const invalidValueKeys = Object.entries(completed.entries).flatMap(([key, value]) => {
    if (!key.startsWith('lovetypes:') || !key.includes('quiz-result')) return [];
    try {
      const parsed = JSON.parse(value);
      return parsed && typeof parsed.primaryKey === 'string' && typeof parsed.savedAt === 'string' ? [] : [key];
    } catch {
      return [key];
    }
  });
  if (invalidValueKeys.length) issues.push(`quiz: saved result payload shape changed: ${invalidValueKeys.join(', ')}`);

  await page.goto(makeUrl('/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.locator('[data-home-saved]:not([hidden])').waitFor({ state: 'visible', timeout: 10000 });
  const saved = await storageSnapshot(page);
  validateQuietStorage(saved, issues, 'quiz');
  const rawFunnel = saved.entries['lovetypes:funnel-events:v1'];
  let funnelEvents = [];
  try {
    funnelEvents = JSON.parse(rawFunnel || '[]');
  } catch {
    issues.push('quiz: funnel events should be JSON');
  }
  const eventNames = new Set(Array.isArray(funnelEvents) ? funnelEvents.map((event) => event.name) : []);
  if (!eventNames.has('quiz_completed')) issues.push('quiz: missing local quiz_completed event');
  if (Array.isArray(funnelEvents)) {
    const event = funnelEvents.find((item) => item.name === 'quiz_completed');
    if (event && (typeof event.lang !== 'string' || !event.lang)) issues.push('quiz: quiz_completed missing language context');
    if (event && event.guardian !== 'iris') issues.push(`quiz: quiz_completed should infer guardian iris, got ${event.guardian || 'empty'}`);
  }
  await page.locator('[data-clear-home-result]').click();
  await page.waitForFunction(() => !Object.keys(localStorage).some((key) => key.includes('quiz-result')), undefined, { timeout: 5000 });
  const cleared = await storageSnapshot(page);
  const lingeringQuizKeys = cleared.localKeys.filter((key) => key.includes('quiz-result'));
  if (lingeringQuizKeys.length) issues.push(`quiz: saved result keys did not clear: ${lingeringQuizKeys.join(', ')}`);
  validateQuietStorage(cleared, issues, 'quiz-after-clear');
  if (!response || response.status() >= 400) issues.push(`quiz: HTTP status ${response?.status() || 'missing'}`);
  issues.push(...networkIssues.map((issue) => `quiz network: ${issue}`));
  await context.close();
  return { name: 'quiz-local-storage', checked: 1, localKeysChecked: completed.localKeys.length + saved.localKeys.length + cleared.localKeys.length, issues };
}

async function worksheetStorageCheck(browser) {
  const context = await browser.newContext({ viewport: { width: 960, height: 1200 } });
  const page = await context.newPage();
  const networkIssues = watchNetwork(page);
  const issues = [];
  const response = await page.goto(makeUrl('/repair-plan/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await resetBrowserStorage(context, page);
  await page.reload({ waitUntil: 'domcontentloaded' });
  const fields = page.locator('[data-repair-worksheet] textarea[data-field]');
  const fieldCount = await fields.count();
  const values = [
    'privacy smoke guardian',
    'privacy smoke wound',
    'privacy smoke repair line',
    'privacy smoke supply',
  ];
  for (let index = 0; index < Math.min(fieldCount, values.length); index += 1) {
    await fields.nth(index).fill(values[index]);
  }
  const autosaved = await page.waitForFunction((expected) => Object.entries(localStorage).some(([key, value]) => {
    if (!key.startsWith('lovetypes:') || !key.includes('repair-worksheet')) return false;
    try {
      const parsed = JSON.parse(value);
      return expected.every((item, index) => parsed[index] === item);
    } catch {
      return false;
    }
  }), values, { timeout: 5000 }).then(() => true).catch(() => false);
  const saved = await storageSnapshot(page);
  validateQuietStorage(saved, issues, 'repair-worksheet');
  if (fieldCount !== 4) issues.push(`repair-worksheet: expected 4 fields, got ${fieldCount}`);
  if (!autosaved) issues.push('repair-worksheet: autosave did not write expected local-only payload');
  const worksheetKeys = saved.localKeys.filter((key) => key.startsWith('lovetypes:') && key.includes('repair-worksheet'));
  if (worksheetKeys.length !== 1) issues.push(`repair-worksheet: expected 1 worksheet key, got ${worksheetKeys.length}`);
  await page.locator('[data-clear-worksheet]').click();
  const clearedOk = await page.waitForFunction(() => !Object.keys(localStorage).some((key) => key.includes('repair-worksheet')), undefined, { timeout: 5000 })
    .then(() => true)
    .catch(() => false);
  const cleared = await storageSnapshot(page);
  validateQuietStorage(cleared, issues, 'repair-worksheet-after-clear');
  if (!clearedOk) issues.push('repair-worksheet: clear did not remove worksheet key');
  if (!response || response.status() >= 400) issues.push(`repair-worksheet: HTTP status ${response?.status() || 'missing'}`);
  issues.push(...networkIssues.map((issue) => `repair-worksheet network: ${issue}`));
  await context.close();
  return { name: 'repair-worksheet-local-storage', checked: 1, localKeysChecked: saved.localKeys.length + cleared.localKeys.length, issues };
}

async function compassStorageCheck(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true });
  const page = await context.newPage();
  const networkIssues = watchNetwork(page);
  const issues = [];
  const response = await page.goto(makeUrl('/compass/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await resetBrowserStorage(context, page);
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.locator('[data-compass-form]').waitFor({ state: 'visible', timeout: 10000 });
  await page.locator('#compass-self').selectOption('W');
  await page.locator('#compass-partner').selectOption('T');
  await page.locator('#compass-status').selectOption('long-distance');
  await page.locator('#compass-issue').selectOption('after-fight');
  await page.locator('[data-compass-form] button[type="submit"]').click();
  await page.locator('[data-compass-result]:not([hidden])').waitFor({ state: 'visible', timeout: 10000 });
  const saved = await storageSnapshot(page);
  validateQuietStorage(saved, issues, 'compass');
  const compassKeys = saved.localKeys.filter((key) => key.includes('compass'));
  if (compassKeys.length) issues.push(`compass: selections should not create dedicated storage keys: ${compassKeys.join(', ')}`);
  if (!response || response.status() >= 400) issues.push(`compass: HTTP status ${response?.status() || 'missing'}`);
  issues.push(...networkIssues.map((issue) => `compass network: ${issue}`));
  await context.close();
  return { name: 'compass-ephemeral-input', checked: 1, localKeysChecked: saved.localKeys.length, issues };
}

async function main() {
  const playwright = await loadPlaywright();
  const browser = await playwright.chromium.launch(await browserLaunchOptions());
  let results = [];
  try {
    console.error('[storage-privacy] quiz-local-storage');
    results.push(await quizStorageCheck(browser));
    console.error('[storage-privacy] repair-worksheet-local-storage');
    results.push(await worksheetStorageCheck(browser));
    console.error('[storage-privacy] compass-ephemeral-input');
    results.push(await compassStorageCheck(browser));
  } finally {
    await browser.close();
  }

  const issues = results.flatMap((result) => result.issues.map((issue) => `${result.name}: ${issue}`));
  const checks = results.reduce((sum, result) => sum + result.checked, 0);
  const localKeysChecked = results.reduce((sum, result) => sum + result.localKeysChecked, 0);
  console.log(`storage_privacy_checks=${checks}`);
  console.log(`storage_privacy_local_keys_checked=${localKeysChecked}`);
  console.log(`storage_privacy_issues=${issues.length}`);
  for (const issue of issues.slice(0, 100)) console.log(issue);
  process.exitCode = issues.length ? 1 : 0;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
