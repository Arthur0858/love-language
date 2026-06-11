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
  page.on('request', (request) => {
    const url = new URL(request.url());
    const method = request.method();
    const type = request.resourceType();
    const sameOrigin = url.origin === baseOrigin;
    if (isCloudflareRum(url, method, type) || isCloudflareInsightsScript(url, method, type)) return;
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
  await page.evaluate(() => {
    document.addEventListener('click', (event) => {
      const link = event.target && event.target.closest && event.target.closest('a[data-funnel-event]');
      if (link) event.preventDefault();
    }, true);
  });
  const productPackLinks = page.locator('[data-quiz-product-pack-link]');
  const productPackLinkCount = await productPackLinks.count();
  for (let index = 0; index < productPackLinkCount; index += 1) {
    await productPackLinks.nth(index).click();
  }
  await page.goto(makeUrl('/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.evaluate(() => {
    document.addEventListener('click', (event) => {
      const link = event.target && event.target.closest && event.target.closest('a[data-funnel-event], a[data-home-resume-route], a[data-home-resume-plan], a[data-home-resume-luna], a[data-home-resume-keepsake], a[data-home-resume-contact], a[data-home-resume-guardian]');
      if (link) event.preventDefault();
    }, true);
  });
  await page.locator('[data-home-saved]:not([hidden])').waitFor({ state: 'visible', timeout: 10000 });
  const homeProductPackLinks = page.locator('[data-home-saved] [data-home-saved-product-link]');
  const homeProductPackLinkCount = await homeProductPackLinks.count();
  for (let index = 0; index < homeProductPackLinkCount; index += 1) {
    await homeProductPackLinks.nth(index).click();
  }
  for (const selector of [
    '[data-home-resume-route]',
    '[data-home-resume-plan]',
    '[data-home-resume-luna]',
    '[data-home-resume-keepsake]',
    '[data-home-resume-contact]',
    '[data-home-resume-guardian]',
  ]) {
    await page.locator(selector).first().click();
  }
  await page.goto(makeUrl('/contact/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.locator('[data-contact-funnel-copy]').waitFor({ state: 'visible', timeout: 10000 });
  await page.locator('[data-contact-funnel-copy]').click();
  const saved = await storageSnapshot(page);
  validateQuietStorage(saved, issues, 'quiz');
  const quizKeys = saved.localKeys.filter((key) => key.startsWith('lovetypes:') && key.includes('quiz-result'));
  if (!quizKeys.length) issues.push('quiz: saved result was not stored with a lovetypes quiz key');
  if (productPackLinkCount !== 4) issues.push(`quiz: expected 4 product pack links, got ${productPackLinkCount}`);
  if (homeProductPackLinkCount !== 4) issues.push(`quiz: expected 4 home saved product pack links, got ${homeProductPackLinkCount}`);
  const rawFunnel = saved.entries['lovetypes:funnel-events:v1'];
  let funnelEvents = [];
  try {
    funnelEvents = JSON.parse(rawFunnel || '[]');
  } catch {
    issues.push('quiz: funnel events should be JSON');
  }
  const eventNames = new Set(Array.isArray(funnelEvents) ? funnelEvents.map((event) => event.name) : []);
  for (const expected of ['quiz_completed', 'supply_pack_free_keepsake', 'supply_pack_owned_request', 'supply_pack_luna', 'supply_pack_contact']) {
    if (!eventNames.has(expected)) issues.push(`quiz: missing local funnel event ${expected}`);
  }
  for (const expected of ['home_saved_pack_free_keepsake', 'home_saved_pack_owned_request', 'home_saved_pack_luna', 'home_saved_pack_contact', 'home_resume_supply_route', 'home_resume_repair_plan', 'home_resume_luna', 'home_resume_keepsake', 'home_resume_contact', 'home_resume_guardian']) {
    if (!eventNames.has(expected)) issues.push(`quiz: missing home resume local funnel event ${expected}`);
  }
  if (!eventNames.has('contact_funnel_summary_copy')) issues.push('quiz: missing contact funnel summary copy event');
  const invalidValueKeys = Object.entries(saved.entries).flatMap(([key, value]) => {
    if (!key.startsWith('lovetypes:') || !key.includes('quiz-result')) return [];
    try {
      const parsed = JSON.parse(value);
      return parsed && typeof parsed.primaryKey === 'string' && typeof parsed.savedAt === 'string' ? [] : [key];
    } catch {
      return [key];
    }
  });
  if (invalidValueKeys.length) issues.push(`quiz: saved result payload shape changed: ${invalidValueKeys.join(', ')}`);
  await page.evaluate(() => {
    for (const key of Object.keys(localStorage)) {
      if (key.includes('quiz-result')) localStorage.removeItem(key);
    }
  });
  const cleared = await storageSnapshot(page);
  const lingeringQuizKeys = cleared.localKeys.filter((key) => key.includes('quiz-result'));
  if (lingeringQuizKeys.length) issues.push(`quiz: saved result keys did not clear: ${lingeringQuizKeys.join(', ')}`);
  validateQuietStorage(cleared, issues, 'quiz-after-clear');
  if (!response || response.status() >= 400) issues.push(`quiz: HTTP status ${response?.status() || 'missing'}`);
  issues.push(...networkIssues.map((issue) => `quiz network: ${issue}`));
  await context.close();
  return { name: 'quiz-local-storage', checked: 1, localKeysChecked: saved.localKeys.length + cleared.localKeys.length, issues };
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

async function funnelStorageCheck(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true });
  const page = await context.newPage();
  const networkIssues = watchNetwork(page);
  const issues = [];
  const response = await page.goto(makeUrl('/resources/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await resetBrowserStorage(context, page);
  await page.evaluate(() => {
    document.addEventListener('click', (event) => {
      const link = event.target && event.target.closest && event.target.closest('a[data-funnel-event]');
      if (link) event.preventDefault();
    }, true);
  });
  const clickTargets = [
    ['supply_route_copy', '[data-copy-supply-route]'],
    ['supply_wishlist_copy', '[data-supply-owned-card] [data-copy-contact-template]'],
    ['safety_bridge_privacy', '[data-safety-boundary-bridge] [data-funnel-event="safety_bridge_privacy"]'],
    ['safety_bridge_terms', '[data-safety-boundary-bridge] [data-funnel-event="safety_bridge_terms"]'],
    ['safety_bridge_contact', '[data-safety-boundary-bridge] [data-funnel-event="safety_bridge_contact"]'],
  ];
  for (const [_name, selector] of clickTargets) {
    await page.locator(selector).first().click();
  }
  await page.goto(makeUrl('/contact/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.evaluate(() => {
    document.addEventListener('click', (event) => {
      const link = event.target && event.target.closest && event.target.closest('a[data-funnel-event]');
      if (link) event.preventDefault();
    }, true);
  });
  await page.locator('[data-funnel-event="contact_supply_template_copy"]').first().click();
  await page.locator('[data-funnel-event="contact_supply_mailto"]').first().click();
  await page.goto(makeUrl('/luna-yoga-music/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.evaluate(() => {
    document.addEventListener('click', (event) => {
      const link = event.target && event.target.closest && event.target.closest('a[data-funnel-event]');
      if (link) event.preventDefault();
    }, true);
  });
  await page.locator('[data-funnel-event="luna_offer_contact"]').first().click();
  await page.goto(makeUrl('/keepsakes/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.evaluate(() => {
    document.addEventListener('click', (event) => {
      const link = event.target && event.target.closest && event.target.closest('a[data-funnel-event]');
      if (link) event.preventDefault();
    }, true);
  });
  for (const selector of [
    '[data-funnel-event="collector_story_open"]',
    '[data-funnel-event="collector_story_download"]',
    '[data-funnel-event="free_keepsake_open"]',
    '[data-funnel-event="free_keepsake_download"]',
    '[data-funnel-event="free_keepsake_asset_request"]',
  ]) {
    await page.locator(selector).first().click();
  }

  const saved = await storageSnapshot(page);
  validateQuietStorage(saved, issues, 'funnel');
  const raw = saved.entries['lovetypes:funnel-events:v1'];
  let events = [];
  try {
    events = JSON.parse(raw || '[]');
  } catch {
    issues.push('funnel: event store should be JSON');
  }
  const names = new Set(Array.isArray(events) ? events.map((event) => event.name) : []);
  for (const expected of ['supply_route_copy', 'supply_wishlist_copy', 'safety_bridge_privacy', 'safety_bridge_terms', 'safety_bridge_contact', 'contact_supply_template_copy', 'contact_supply_mailto', 'luna_offer_contact', 'collector_story_open', 'collector_story_download', 'free_keepsake_open', 'free_keepsake_download', 'free_keepsake_asset_request']) {
    if (!names.has(expected)) issues.push(`funnel: missing local event ${expected}`);
  }
  if (!Array.isArray(events)) {
    issues.push('funnel: event store should be an array');
  } else {
    if (events.length > 40) issues.push(`funnel: event store should keep at most 40 events, got ${events.length}`);
    for (const [index, event] of events.entries()) {
      if (!event || typeof event.name !== 'string' || typeof event.path !== 'string' || typeof event.at !== 'string') {
        issues.push(`funnel: event ${index} has invalid shape`);
      }
    }
  }
  if (!response || response.status() >= 400) issues.push(`funnel: HTTP status ${response?.status() || 'missing'}`);
  issues.push(...networkIssues.map((issue) => `funnel network: ${issue}`));
  await context.close();
  return { name: 'funnel-local-observability', checked: 1, localKeysChecked: saved.localKeys.length, issues };
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
    console.error('[storage-privacy] funnel-local-observability');
    results.push(await funnelStorageCheck(browser));
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
