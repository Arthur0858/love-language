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
const CASES = [
  { name: 'home-mobile', path: '/', width: 390, height: 844, isMobile: true, quiz: true },
  { name: 'characters-mobile', path: '/characters/', width: 390, height: 844, selector: '[data-universe-map] .guardian-card' },
  { name: 'iris-mobile', path: '/characters/iris/', width: 390, height: 844, selector: '[data-domain-marker]' },
  { name: 'resources-mobile', path: '/resources/', width: 390, height: 844, selector: '.supply-route-card' },
  { name: 'repair-plan-mobile', path: '/repair-plan/', width: 390, height: 844, selector: '[data-repair-worksheet]' },
  { name: 'luna-mobile', path: '/luna-yoga-music/', width: 390, height: 844, selector: '[id^="luna-"]' },
];

function makeUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

function initCspCollector() {
  window.__lovetypesCspViolations = [];
  document.addEventListener('securitypolicyviolation', (event) => {
    window.__lovetypesCspViolations.push({
      blockedURI: event.blockedURI,
      violatedDirective: event.violatedDirective,
      effectiveDirective: event.effectiveDirective,
      sourceFile: event.sourceFile,
      lineNumber: event.lineNumber,
    });
  });
}

function isBlockingConsoleMessage(message) {
  if (message.type() !== 'error') return false;
  const text = message.text();
  return ![
    'Failed to load resource: the server responded with a status of 404',
    'favicon',
  ].some((token) => text.includes(token));
}

async function completeQuiz(page) {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
  await page.locator('[data-quiz-start]').first().click();
  for (let index = 0; index < 15; index += 1) {
    await page.locator('.quiz-option').first().click();
    await page.locator('.quiz-next').click();
  }
  await page.locator('.quiz-result-card').waitFor({ state: 'visible', timeout: 10000 });
  await page.locator('[data-conversion-route]').first().waitFor({ state: 'visible', timeout: 10000 });
}

async function runCase(browser, item) {
  const context = await browser.newContext({
    viewport: { width: item.width, height: item.height },
    isMobile: Boolean(item.isMobile),
    deviceScaleFactor: item.isMobile ? 2 : 1,
  });
  const page = await context.newPage();
  await page.addInitScript(initCspCollector);
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', (message) => {
    if (isBlockingConsoleMessage(message)) consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  const response = await page.goto(makeUrl(item.path), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  if (item.quiz) await completeQuiz(page);
  if (item.selector) await page.locator(item.selector).first().waitFor({ state: 'visible', timeout: 10000 });
  const result = await page.evaluate(() => ({
    title: document.title,
    h1: document.querySelector('h1')?.textContent?.trim() || '',
    cspViolations: window.__lovetypesCspViolations || [],
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  }));
  await context.close();

  const issues = [];
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);
  if (!result.title) issues.push('missing title');
  if (!result.h1) issues.push('missing h1');
  if (result.horizontalOverflow) issues.push('horizontal overflow');
  for (const violation of result.cspViolations) {
    issues.push(`CSP ${violation.effectiveDirective || violation.violatedDirective} blocked ${violation.blockedURI || 'unknown'}`);
  }
  for (const error of consoleErrors) issues.push(`console error: ${error}`);
  for (const error of pageErrors) issues.push(`page error: ${error}`);
  return {
    name: item.name,
    checked: 1,
    violationCount: result.cspViolations.length,
    issues,
  };
}

async function main() {
  const playwright = await loadPlaywright();
  const browser = await playwright.chromium.launch(await browserLaunchOptions());
  const results = [];
  try {
    for (const item of CASES) {
      console.error(`[csp-runtime] ${item.name}`);
      results.push(await runCase(browser, item));
    }
  } finally {
    await browser.close();
  }

  const issues = results.flatMap((result) => result.issues.map((issue) => `${result.name}: ${issue}`));
  const checks = results.reduce((sum, result) => sum + result.checked, 0);
  const violations = results.reduce((sum, result) => sum + result.violationCount, 0);
  console.log(`csp_runtime_pages_checked=${checks}`);
  console.log(`csp_runtime_violations=${violations}`);
  console.log(`csp_runtime_issues=${issues.length}`);
  for (const issue of issues.slice(0, 100)) console.log(issue);
  process.exitCode = issues.length ? 1 : 0;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
