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
const TAB_CASES = [
  { name: 'home-mobile', path: '/', width: 390, height: 844 },
  { name: 'home-en-mobile', path: '/en/', width: 390, height: 844 },
  { name: 'garden-map-mobile', path: '/garden-map/', width: 390, height: 844 },
  { name: 'characters-mobile', path: '/characters/', width: 390, height: 844 },
  { name: 'resources-mobile', path: '/resources/', width: 390, height: 844 },
  { name: 'repair-plan-mobile', path: '/repair-plan/', width: 390, height: 844 },
  { name: 'luna-mobile', path: '/luna-yoga-music/', width: 390, height: 844 },
  { name: 'contact-mobile', path: '/contact/', width: 390, height: 844 },
];

function makeUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

async function focusSnapshot(page) {
  return page.evaluate(() => {
    const node = document.activeElement;
    if (!node || node === document.body) {
      return { tag: 'body', id: '', text: '', href: '', visible: false, outline: 'none', boxShadow: 'none' };
    }
    const style = window.getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    return {
      tag: node.tagName.toLowerCase(),
      id: node.id || '',
      text: (node.getAttribute('aria-label') || node.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80),
      href: node.getAttribute('href') || '',
      visible: style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0,
      outline: style.outlineStyle,
      outlineWidth: style.outlineWidth,
      boxShadow: style.boxShadow,
    };
  });
}

function hasVisibleFocus(snapshot) {
  if (!snapshot.visible) return false;
  if (snapshot.outline && snapshot.outline !== 'none' && snapshot.outlineWidth !== '0px') return true;
  return Boolean(snapshot.boxShadow && snapshot.boxShadow !== 'none');
}

async function tabOrderCheck(browser, item) {
  const context = await browser.newContext({
    viewport: { width: item.width, height: item.height },
    isMobile: item.width <= 720,
    deviceScaleFactor: item.width <= 720 ? 2 : 1,
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  const response = await page.goto(makeUrl(item.path), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  const issues = [];
  const snapshots = [];
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);

  for (let index = 0; index < 10; index += 1) {
    await page.keyboard.press('Tab');
    const snapshot = await focusSnapshot(page);
    snapshots.push(snapshot);
  }

  const namedFocuses = snapshots.filter((snapshot) => snapshot.visible && (snapshot.text || snapshot.href || snapshot.id));
  const uniqueFocuses = new Set(namedFocuses.map((snapshot) => `${snapshot.tag}:${snapshot.id}:${snapshot.href}:${snapshot.text}`));
  const visibleFocusCount = snapshots.filter(hasVisibleFocus).length;
  if (namedFocuses.length < 4) issues.push(`expected at least 4 named tab stops, got ${namedFocuses.length}`);
  if (uniqueFocuses.size < 4) issues.push(`expected at least 4 unique tab stops, got ${uniqueFocuses.size}`);
  if (visibleFocusCount < Math.min(4, namedFocuses.length)) issues.push(`expected visible focus indicators on tab stops, got ${visibleFocusCount}`);

  for (const message of consoleErrors) issues.push(`console error: ${message}`);
  for (const message of pageErrors) issues.push(`page error: ${message}`);
  await context.close();
  return { name: item.name, tabStopsChecked: snapshots.length, namedFocuses: namedFocuses.length, issues };
}

async function skipLinkCheck(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, deviceScaleFactor: 2 });
  const page = await context.newPage();
  const issues = [];
  const response = await page.goto(makeUrl('/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);
  await page.keyboard.press('Tab');
  let snapshot = await focusSnapshot(page);
  if (!snapshot.href.includes('#main')) issues.push(`first tab should focus skip link to #main, got ${JSON.stringify(snapshot)}`);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(120);
  snapshot = await focusSnapshot(page);
  if (snapshot.id !== 'main') issues.push(`skip link should move focus to main, got ${JSON.stringify(snapshot)}`);
  await context.close();
  return { name: 'skip-link-home-mobile', tabStopsChecked: 1, namedFocuses: 1, issues };
}

async function languageMenuKeyboardCheck(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, deviceScaleFactor: 2 });
  const page = await context.newPage();
  const issues = [];
  const response = await page.goto(makeUrl('/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);
  await page.locator('.language-menu summary').focus();
  await page.keyboard.press('Enter');
  const opened = await page.locator('.language-menu').evaluate((node) => node.hasAttribute('open')).catch(() => false);
  if (!opened) issues.push('language menu should open with Enter on summary');
  const links = await page.locator('.language-switcher a').count().catch(() => 0);
  if (links !== 5) issues.push(`language menu should expose 5 language links, got ${links}`);
  await page.keyboard.press('Escape');
  const closed = await page.locator('.language-menu').evaluate((node) => !node.hasAttribute('open')).catch(() => false);
  if (!closed) issues.push('language menu should close with Escape');
  await context.close();
  return { name: 'language-menu-keyboard', tabStopsChecked: 1, namedFocuses: links, issues };
}

async function quizKeyboardCheck(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, deviceScaleFactor: 2 });
  const page = await context.newPage();
  const issues = [];
  const response = await page.goto(makeUrl('/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);
  await page.waitForFunction(() => (
    Boolean(window.__LOVETYPES_QUIZ_DATA)
    && Boolean(document.querySelector('[data-quiz-root] [data-quiz-start]'))
  ), undefined, { timeout: 10000 }).catch(() => {
    issues.push('quiz script did not become ready');
  });
  await page.locator('[data-quiz-start]').focus();
  await page.keyboard.press('Enter');
  await page.waitForTimeout(150);
  const firstQuestionVisible = await page.locator('[data-quiz-box]:not([hidden]) [id^="quiz-question-"]').first().isVisible().catch(() => false);
  if (!firstQuestionVisible) issues.push('quiz should start with Enter on start button');
  await page.locator('.quiz-option').first().focus();
  await page.keyboard.press('Space');
  const optionPressed = await page.locator('.quiz-option').first().getAttribute('aria-pressed').catch(() => '');
  if (optionPressed !== 'true') issues.push(`quiz option should toggle with Space, got aria-pressed=${optionPressed}`);
  await page.locator('.quiz-next').focus();
  await page.keyboard.press('Enter');
  const questionIndex = await page.locator('.quiz-progress-bar').getAttribute('aria-valuenow').catch(() => '');
  if (questionIndex !== '2') issues.push(`quiz next should advance with Enter, got progress ${questionIndex}`);
  await context.close();
  return { name: 'quiz-keyboard-home-mobile', tabStopsChecked: 3, namedFocuses: 3, issues };
}

async function main() {
  const playwright = await loadPlaywright();
  const browser = await playwright.chromium.launch(await browserLaunchOptions());
  const results = [];
  try {
    console.error('[keyboard] skip-link-home-mobile');
    results.push(await skipLinkCheck(browser));
    console.error('[keyboard] language-menu-keyboard');
    results.push(await languageMenuKeyboardCheck(browser));
    console.error('[keyboard] quiz-keyboard-home-mobile');
    results.push(await quizKeyboardCheck(browser));
    for (const item of TAB_CASES) {
      console.error(`[keyboard] ${item.name}`);
      results.push(await tabOrderCheck(browser, item));
    }
  } finally {
    await browser.close();
  }

  const issues = results.flatMap((result) => result.issues.map((issue) => `${result.name}: ${issue}`));
  const tabStopsChecked = results.reduce((sum, result) => sum + result.tabStopsChecked, 0);
  const namedFocusesChecked = results.reduce((sum, result) => sum + result.namedFocuses, 0);
  console.log(`keyboard_navigation_cases_checked=${results.length}`);
  console.log(`keyboard_navigation_tab_stops_checked=${tabStopsChecked}`);
  console.log(`keyboard_navigation_named_focuses_checked=${namedFocusesChecked}`);
  console.log(`keyboard_navigation_issues=${issues.length}`);
  for (const issue of issues.slice(0, 100)) console.log(issue);
  if (issues.length > 100) console.log(`... ${issues.length - 100} more issue(s)`);
  process.exitCode = issues.length ? 1 : 0;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
