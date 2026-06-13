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
const ATTRIBUTION_QUERY = '?utm_source=youtube&utm_medium=shorts&utm_campaign=first_round_quiz_completion&utm_content=iris_silence';
const CASES = [
  {
    name: 'quiz-flow-zh-desktop',
    path: `/${ATTRIBUTION_QUERY}`,
    viewport: { width: 1280, height: 900 },
    expectedCampaign: {
      utm_source: 'youtube',
      utm_medium: 'shorts',
      utm_campaign: 'first_round_quiz_completion',
      utm_content: 'iris_silence',
    },
  },
  { name: 'quiz-flow-zh-mobile', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'quiz-flow-en-mobile', path: '/en/', viewport: { width: 390, height: 844 } },
  { name: 'quiz-flow-ja-mobile', path: '/ja/', viewport: { width: 390, height: 844 } },
  { name: 'quiz-flow-ko-mobile', path: '/ko/', viewport: { width: 390, height: 844 } },
  { name: 'quiz-flow-es-mobile', path: '/es/', viewport: { width: 390, height: 844 } },
];

function makeUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

function langForPath(path) {
  const match = path.match(/^\/(en|ja|ko|es)(?:\/|$)/);
  return match ? match[1] : 'zh';
}

function isExpectedAffiliateHref(path, href) {
  let url;
  try {
    url = new URL(href);
  } catch {
    return false;
  }
  if (langForPath(path) === 'zh') {
    return url.hostname === 'www.books.com.tw' && href.includes('arthur0858') && href.includes('utm_campaign=ap-202604');
  }
  return url.hostname === 'www.amazon.com' && url.pathname.startsWith('/dp/') && url.searchParams.get('tag') === 'parenttechche-20';
}

function hasBlockingConsoleMessage(message) {
  return message.type() === 'error';
}

async function completeQuiz(page) {
  await page.locator('[data-quiz-start]').first().click();
  for (let index = 0; index < 15; index += 1) {
    await page.locator('.quiz-option').first().click();
    await page.locator('.quiz-next').click();
  }
  await page.locator('.quiz-result-card').waitFor({ state: 'visible', timeout: 12000 });
}

async function runCase(browser, item) {
  const context = await browser.newContext({
    viewport: item.viewport,
    isMobile: item.viewport.width <= 720,
    deviceScaleFactor: item.viewport.width <= 720 ? 2 : 1,
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const issues = [];
  page.on('console', (message) => {
    if (hasBlockingConsoleMessage(message)) consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  const response = await page.goto(makeUrl(item.path), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);

  await page.waitForFunction(() => (
    Boolean(window.__LOVETYPES_QUIZ_DATA)
    && Boolean(document.querySelector('[data-quiz-root] [data-quiz-start]'))
  ), undefined, { timeout: 10000 }).catch(() => {
    issues.push('quiz data or start button did not become ready');
  });

  await completeQuiz(page);
  const resultName = await page.locator('.quiz-result-card h3').first().innerText().catch(() => '');
  const resultImageReady = await page.locator('.quiz-result-card img').first().evaluate((image) => (
    image.complete && image.naturalWidth > 0 && image.naturalHeight > 0
  )).catch(() => false);
  const routeHref = await page.locator('[data-conversion-route]').first().getAttribute('href').catch(() => '');
  const planHref = await page.locator('[data-conversion-plan]').first().getAttribute('href').catch(() => '');
  const lunaHref = await page.locator('[data-conversion-luna]').first().getAttribute('href').catch(() => '');
  const guideHref = await page.locator('[data-conversion-guide]').first().getAttribute('href').catch(() => '');
  const keepsakeHref = await page.locator('[data-conversion-keepsake]').first().getAttribute('href').catch(() => '');
  const bookHref = await page.locator('[data-conversion-book]').first().getAttribute('href').catch(() => '');
  const bookRel = await page.locator('[data-conversion-book]').first().getAttribute('rel').catch(() => '');
  const savedResult = await page.evaluate(() => {
    const candidates = [
      'lovetypes:zh:quiz-result',
      `lovetypes:${location.pathname}:quiz-result`,
    ];
    for (const key of candidates) {
      try {
        const value = JSON.parse(localStorage.getItem(key) || 'null');
        if (value?.primaryKey) return value;
      } catch {
        // Continue checking the next key.
      }
    }
    return null;
  });
  const disclosureVisible = await page.locator('.quiz-supply-card .affiliate-disclosure').first().isVisible().catch(() => false);
  const supplyPassVisible = await page.locator('[data-supply-pass]').first().isVisible().catch(() => false);
  await page.evaluate(() => {
    const link = document.querySelector('[data-conversion-route]');
    link?.addEventListener('click', (event) => event.preventDefault(), { once: true });
  });
  await page.locator('[data-conversion-route]').first().click();
  const funnelEvent = await page.evaluate(() => {
    try {
      const events = JSON.parse(localStorage.getItem('lovetypes:funnel-events:v1') || '[]');
      return Array.isArray(events) ? events.at(-1) : null;
    } catch {
      return null;
    }
  });
  const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);

  if (!resultName) issues.push('missing result name');
  if (!resultImageReady) issues.push('result image did not load');
  if (!routeHref.includes('/resources/#supply-')) issues.push(`missing supply route CTA: ${routeHref}`);
  if (!planHref.includes('/repair-plan/#plan-')) issues.push(`missing repair plan CTA: ${planHref}`);
  if (!lunaHref.includes('/luna-yoga-music/#luna-')) issues.push(`missing Luna CTA: ${lunaHref}`);
  if (!guideHref.includes('/guides/') || !guideHref.includes('#guide-')) issues.push(`missing guide CTA: ${guideHref}`);
  if (!keepsakeHref.includes('/keepsakes/#keepsake-')) issues.push(`missing keepsake CTA: ${keepsakeHref}`);
  if (!isExpectedAffiliateHref(item.path, bookHref)) issues.push(`missing expected localized affiliate book CTA: ${bookHref}`);
  if (!bookRel.includes('sponsored')) issues.push(`affiliate book CTA missing sponsored rel: ${bookRel}`);
  if (!disclosureVisible) issues.push('affiliate disclosure is not visible in result');
  if (!supplyPassVisible) issues.push('guardian supply pass is not visible in result');
  if (funnelEvent?.name !== 'quiz_result_supply_route') issues.push(`funnel event missing quiz_result_supply_route: ${JSON.stringify(funnelEvent)}`);
  if (funnelEvent?.path !== new URL(makeUrl(item.path)).pathname) issues.push(`funnel event path mismatch: ${JSON.stringify(funnelEvent)}`);
  if (item.expectedCampaign) {
    for (const [key, value] of Object.entries(item.expectedCampaign)) {
      if (savedResult?.campaign?.[key] !== value) {
        issues.push(`saved quiz attribution missing ${key}=${value}: ${JSON.stringify(savedResult?.campaign || null)}`);
      }
      if (funnelEvent?.campaign?.[key] !== value) {
        issues.push(`funnel attribution missing ${key}=${value}: ${JSON.stringify(funnelEvent?.campaign || null)}`);
      }
    }
  }
  if (horizontalOverflow) issues.push('horizontal overflow');
  for (const message of consoleErrors) issues.push(`console error: ${message}`);
  for (const message of pageErrors) issues.push(`page error: ${message}`);
  await context.close();
  return {
    name: item.name,
    resultName,
    ctasChecked: 6,
    funnelEventsChecked: funnelEvent ? 1 : 0,
    attributionsChecked: item.expectedCampaign ? Object.keys(item.expectedCampaign).length * 2 : 0,
    affiliateLinksChecked: bookHref ? 1 : 0,
    disclosuresChecked: disclosureVisible ? 1 : 0,
    issues,
  };
}

const playwright = await loadPlaywright();
const browser = await playwright.chromium.launch(await browserLaunchOptions());
let results = [];
try {
  for (const item of CASES) {
    console.error(`[public-quiz-flow] ${item.name}`);
    results.push(await runCase(browser, item));
  }
} finally {
  await browser.close();
}

const issues = results.flatMap((result) => result.issues.map((issue) => `${result.name}: ${issue}`));
console.log(`public_quiz_flow_cases_checked=${results.length}`);
console.log(`public_quiz_flow_results_checked=${results.filter((result) => result.resultName).length}`);
console.log(`public_quiz_flow_ctas_checked=${results.reduce((sum, result) => sum + result.ctasChecked, 0)}`);
console.log(`public_quiz_flow_funnel_events_checked=${results.reduce((sum, result) => sum + result.funnelEventsChecked, 0)}`);
console.log(`public_quiz_flow_attributions_checked=${results.reduce((sum, result) => sum + result.attributionsChecked, 0)}`);
console.log(`public_quiz_flow_affiliate_links_checked=${results.reduce((sum, result) => sum + result.affiliateLinksChecked, 0)}`);
console.log(`public_quiz_flow_disclosures_checked=${results.reduce((sum, result) => sum + result.disclosuresChecked, 0)}`);
console.log(`public_quiz_flow_issues=${issues.length}`);
for (const issue of issues.slice(0, 100)) console.log(issue);
if (issues.length > 100) console.log(`... ${issues.length - 100} more issue(s)`);
process.exitCode = issues.length ? 1 : 0;
