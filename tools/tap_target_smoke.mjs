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
  { name: 'home-mobile', path: '/' },
  { name: 'garden-map-mobile', path: '/garden-map/' },
  { name: 'characters-mobile', path: '/characters/' },
  { name: 'resources-mobile', path: '/resources/' },
  { name: 'repair-plan-mobile', path: '/repair-plan/' },
  { name: 'luna-mobile', path: '/luna-yoga-music/' },
];

const SELECTORS = [
  'summary',
  '.primary-btn',
  '.secondary-btn',
  '.language-switcher a',
  '.quiz-options button',
  '[data-copy-result]',
  '[data-copy-supply-route]',
  '[data-copy-worksheet-summary]',
  '[data-clear-worksheet]',
];

function makeUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

async function inspectCase(browser, item) {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    deviceScaleFactor: 2,
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
  await page.locator('.language-menu summary').click().catch(() => {});
  if (item.path === '/') {
    await page.locator('[data-quiz-start]').click().catch(() => {});
  }

  const targets = await page.evaluate((selectors) => {
    const visible = (node) => {
      const style = window.getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
    };
    const label = (node) =>
      node.getAttribute('aria-label') ||
      node.textContent?.trim().replace(/\s+/g, ' ').slice(0, 48) ||
      node.getAttribute('href') ||
      node.tagName.toLowerCase();
    const nodes = [...document.querySelectorAll(selectors.join(','))].filter(visible);
    return nodes.map((node) => {
      const rect = node.getBoundingClientRect();
      return {
        tag: node.tagName.toLowerCase(),
        selector: selectors.find((selector) => node.matches(selector)) || node.tagName.toLowerCase(),
        label: label(node),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      };
    });
  }, SELECTORS);

  await context.close();

  const issues = [];
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);
  for (const message of consoleErrors) issues.push(`console error: ${message}`);
  for (const message of pageErrors) issues.push(`page error: ${message}`);
  for (const target of targets) {
    if (target.width < 40 || target.height < 40) {
      issues.push(`${target.selector} "${target.label}" is ${target.width}x${target.height}`);
    }
  }
  return { name: item.name, targetsChecked: targets.length, issues };
}

async function main() {
  const playwright = await loadPlaywright();
  const browser = await playwright.chromium.launch(await browserLaunchOptions());
  const results = [];
  try {
    for (const item of CASES) {
      console.error(`[tap] ${item.name}`);
      results.push(await inspectCase(browser, item));
    }
  } finally {
    await browser.close();
  }

  const issues = results.flatMap((result) => result.issues.map((issue) => `${result.name}: ${issue}`));
  const targetsChecked = results.reduce((sum, result) => sum + result.targetsChecked, 0);
  console.log(`tap_target_pages_checked=${results.length}`);
  console.log(`tap_targets_checked=${targetsChecked}`);
  console.log(`tap_target_issues=${issues.length}`);
  for (const issue of issues.slice(0, 100)) console.log(issue);
  if (issues.length > 100) console.log(`... ${issues.length - 100} more issue(s)`);
  process.exitCode = issues.length ? 1 : 0;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
