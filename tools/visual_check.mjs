import { access, mkdir, readdir } from 'node:fs/promises';
import { join } from 'node:path';

async function loadPlaywright() {
  const candidates = [
    'playwright',
    process.env.PLAYWRIGHT_MODULE_PATH,
    '/Users/mac/Documents/New project 3/shorts-factory/lovetypes-shorts/node_modules/playwright/index.js',
    '/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs',
  ].filter(Boolean);

  let lastError;
  for (const candidate of candidates) {
    try {
      const playwright = await import(candidate);
      return playwright.chromium ? playwright : playwright.default;
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError;
}

function makeUrl(path) {
  const baseUrl = process.env.BASE_URL || 'http://127.0.0.1:4173';
  return new URL(path, baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`).toString();
}

function hasBlockingConsoleMessage(message) {
  return ['error'].includes(message.type());
}

function summarizeFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (!result.title) failures.push('missing title');
    if (!result.h1) failures.push('missing h1');
    if (result.navCount < 4) failures.push('navigation too small');
    if (result.textLength < 120) failures.push('page text too short');
    if (result.horizontalOverflow) failures.push('horizontal overflow');
    if (result.consoleErrors.length) failures.push('console errors');
    if (result.pageErrors.length) failures.push('page errors');
    return failures.map((failure) => `${result.name}: ${failure}`);
  });
}

async function firstExistingPath(paths) {
  for (const path of paths) {
    try {
      await access(path);
      return path;
    } catch {
      // Try the next known browser location.
    }
  }
  return undefined;
}

async function findCachedChromium() {
  if (process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH) {
    return firstExistingPath([process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH]);
  }

  const cacheRoot = '/Users/mac/Library/Caches/ms-playwright';
  let entries = [];
  try {
    entries = await readdir(cacheRoot);
  } catch {
    return undefined;
  }

  const candidates = entries
    .filter((entry) => entry.startsWith('chromium_headless_shell-'))
    .sort()
    .reverse()
    .map((entry) => join(cacheRoot, entry, 'chrome-headless-shell-mac-arm64', 'chrome-headless-shell'));

  return firstExistingPath(candidates);
}

async function getChromium() {
  try {
    const { chromium } = await loadPlaywright();
    return chromium;
  } catch (error) {
    console.error(error);
    process.exit(1);
  }
}

const chromium = await getChromium();

const cases = [
  { name: 'home-desktop', path: '/', viewport: { width: 1440, height: 1000 } },
  { name: 'home-mobile', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'resources-desktop', path: '/resources/', viewport: { width: 1280, height: 900 } },
  { name: 'resources-mobile', path: '/resources/', viewport: { width: 390, height: 844 } },
  { name: 'repair-plan-mobile', path: '/repair-plan/', viewport: { width: 390, height: 844 } },
  { name: 'keepsakes-mobile', path: '/keepsakes/', viewport: { width: 390, height: 844 } },
  { name: 'luna-mobile', path: '/luna/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-mobile', path: '/characters/iris/', viewport: { width: 390, height: 844 } },
  { name: 'en-home-mobile', path: '/en/', viewport: { width: 390, height: 844 } },
  { name: 'ja-repair-plan-mobile', path: '/ja/repair-plan/', viewport: { width: 390, height: 844 } },
  { name: 'es-guides-desktop', path: '/es/guides/', viewport: { width: 1280, height: 900 } },
];

await mkdir('output/playwright', { recursive: true });
const executablePath = await findCachedChromium();
const browser = await chromium.launch({ headless: true, executablePath });
const results = [];

for (const item of cases) {
  const page = await browser.newPage({ viewport: item.viewport });
  const consoleErrors = [];
  const pageErrors = [];

  page.on('console', (message) => {
    if (hasBlockingConsoleMessage(message)) {
      consoleErrors.push(message.text());
    }
  });
  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
  });

  const url = makeUrl(item.path);
  const response = await page.goto(url, { waitUntil: 'networkidle' });
  const title = await page.title();
  const h1 = await page.locator('h1').first().innerText().catch(() => '');
  const navCount = await page.locator('.nav-links a').count();
  const bodyText = await page.locator('body').innerText();
  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    url,
    status: response?.status(),
    title,
    h1,
    navCount,
    textLength: bodyText.length,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    screenshot,
  });
  await page.close();
}

await browser.close();
console.log(JSON.stringify(results, null, 2));

const failures = summarizeFailures(results);
if (failures.length) {
  console.error(`Visual check failed:\n${failures.join('\n')}`);
  process.exit(1);
}
