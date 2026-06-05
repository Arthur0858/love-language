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
const cases = [
  {
    name: 'zh',
    path: '/__lovetypes_missing_smoke_zh__/',
    lang: 'zh-TW',
    heading: '這盞燈暫時不在地圖上',
    startHref: '/#quiz-section',
    guidesHref: '/guides/',
    contactHref: '/contact/',
  },
  {
    name: 'en',
    path: '/en/__lovetypes_missing_smoke__/',
    lang: 'en',
    heading: 'This light is not on the map yet',
    startHref: '/en/#quiz-section',
    guidesHref: '/en/guides/',
    contactHref: '/en/contact/',
  },
  {
    name: 'ja',
    path: '/ja/__lovetypes_missing_smoke__/',
    lang: 'ja',
    heading: 'この灯りはまだ地図にありません',
    startHref: '/ja/#quiz-section',
    guidesHref: '/ja/guides/',
    contactHref: '/ja/contact/',
  },
  {
    name: 'ko',
    path: '/ko/__lovetypes_missing_smoke__/',
    lang: 'ko',
    heading: '이 불빛은 아직 지도에 없습니다',
    startHref: '/ko/#quiz-section',
    guidesHref: '/ko/guides/',
    contactHref: '/ko/contact/',
  },
  {
    name: 'es',
    path: '/es/__lovetypes_missing_smoke__/',
    lang: 'es',
    heading: 'Esta luz aún no está en el mapa',
    startHref: '/es/#quiz-section',
    guidesHref: '/es/guides/',
    contactHref: '/es/contact/',
  },
];

function makeUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

const playwright = await loadPlaywright();
const browser = await playwright.chromium.launch(await browserLaunchOptions());
const issues = [];
let casesChecked = 0;
let localizedCases = 0;
let safeRouteLinksChecked = 0;

function isExpectedNotFoundConsole(text) {
  return text.includes('Failed to load resource: the server responded with a status of 404');
}

for (const item of cases) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', (message) => {
    const text = message.text();
    if (message.type() === 'error' && !isExpectedNotFoundConsole(text)) consoleErrors.push(text);
  });
  page.on('pageerror', (error) => pageErrors.push(String(error.message || error)));
  const response = await page.goto(makeUrl(item.path), { waitUntil: 'networkidle', timeout: 45000 });
  casesChecked += 1;
  await page.waitForTimeout(250);
  const result = await page.evaluate(() => {
    const getHref = (selector) => document.querySelector(selector)?.getAttribute('href') || '';
    const routes = [...document.querySelectorAll('[data-not-found-route]')].map((node) => node.getAttribute('href') || '');
    return {
      title: document.title,
      htmlLang: document.documentElement.lang,
      heading: document.querySelector('h1')?.textContent?.trim() || '',
      robots: document.querySelector('meta[name="robots"]')?.getAttribute('content') || '',
      startHref: getHref('[data-not-found-field="start"]'),
      guidesHref: getHref('[data-not-found-field="guides"]'),
      contactHref: getHref('[data-not-found-field="contact_link"]'),
      routeHrefs: routes,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    };
  });

  const status = response?.status() || 0;
  if (status !== 404) issues.push(`${item.name}: expected status 404, got ${status}`);
  if (result.htmlLang !== item.lang) issues.push(`${item.name}: expected html lang ${item.lang}, got ${result.htmlLang}`);
  if (result.heading !== item.heading) issues.push(`${item.name}: expected localized heading ${JSON.stringify(item.heading)}, got ${JSON.stringify(result.heading)}`);
  if (!result.robots.toLowerCase().includes('noindex')) issues.push(`${item.name}: 404 should be noindex, got ${result.robots}`);
  for (const [label, expected, actual] of [
    ['start', item.startHref, result.startHref],
    ['guides', item.guidesHref, result.guidesHref],
    ['contact', item.contactHref, result.contactHref],
  ]) {
    safeRouteLinksChecked += 1;
    if (actual !== expected) issues.push(`${item.name}: ${label} href should be ${expected}, got ${actual}`);
  }
  if (result.routeHrefs.length !== 4) issues.push(`${item.name}: expected four safe route cards, got ${result.routeHrefs.length}`);
  if (result.horizontalOverflow) issues.push(`${item.name}: horizontal overflow on 404 page`);
  if (consoleErrors.length) issues.push(`${item.name}: console errors ${consoleErrors.join(' | ')}`);
  if (pageErrors.length) issues.push(`${item.name}: page errors ${pageErrors.join(' | ')}`);
  if (!issues.some((issue) => issue.startsWith(`${item.name}:`))) localizedCases += 1;
  await page.close();
}

await browser.close();

console.log(`public_not_found_cases_checked=${casesChecked}`);
console.log(`public_not_found_localized_cases=${localizedCases}`);
console.log(`public_not_found_safe_route_links_checked=${safeRouteLinksChecked}`);
console.log(`public_not_found_issues=${issues.length}`);
for (const issue of issues) console.log(issue);
process.exit(issues.length ? 1 : 0);
