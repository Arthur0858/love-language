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
const MODE = process.env.PERFORMANCE_SMOKE_MODE || (BASE_URL.includes('127.0.0.1') ? 'local' : 'public');
const IS_PUBLIC = MODE === 'public';

const CASES = [
  { name: 'home-desktop', path: '/', width: 1366, height: 900 },
  { name: 'home-mobile', path: '/', width: 390, height: 844, isMobile: true },
  { name: 'garden-map-mobile', path: '/garden-map/', width: 390, height: 844, isMobile: true },
  { name: 'characters-mobile', path: '/characters/', width: 390, height: 844, isMobile: true },
  { name: 'iris-mobile', path: '/characters/iris/', width: 390, height: 844, isMobile: true },
  { name: 'resources-mobile', path: '/resources/', width: 390, height: 844, isMobile: true },
  { name: 'luna-mobile', path: '/luna-yoga-music/', width: 390, height: 844, isMobile: true },
];

const BUDGETS = {
  public: {
    firstContentfulPaint: 3000,
    largestContentfulPaint: 4000,
    domContentLoaded: 4000,
    loadEventEnd: 6500,
    cls: 0.1,
    totalBytes: 1400 * 1024,
    scriptBytes: 180 * 1024,
    styleBytes: 160 * 1024,
    imageBytes: 900 * 1024,
  },
  local: {
    firstContentfulPaint: 1800,
    largestContentfulPaint: 2500,
    domContentLoaded: 1800,
    loadEventEnd: 3000,
    cls: 0.1,
    totalBytes: 1400 * 1024,
    scriptBytes: 180 * 1024,
    styleBytes: 160 * 1024,
    imageBytes: 900 * 1024,
  },
};

function absoluteUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

function initPerformanceObserver() {
  window.__lovetypesPerf = { lcp: 0, cls: 0 };
  try {
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const last = entries[entries.length - 1];
      if (last) window.__lovetypesPerf.lcp = Math.round(last.startTime);
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (error) {
    window.__lovetypesPerf.lcpError = String(error && error.message ? error.message : error);
  }
  try {
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) window.__lovetypesPerf.cls += entry.value;
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (error) {
    window.__lovetypesPerf.clsError = String(error && error.message ? error.message : error);
  }
}

function bytesOf(entry) {
  return Number(entry.transferSize || entry.encodedBodySize || 0);
}

function summarizeByType(resources, predicate) {
  return resources.filter(predicate).reduce((sum, entry) => sum + bytesOf(entry), 0);
}

function pathName(entry) {
  try {
    return new URL(entry.name).pathname;
  } catch {
    return entry.name || '';
  }
}

function isScriptResource(entry) {
  return pathName(entry).endsWith('.js') || entry.initiatorType === 'script';
}

function isStyleResource(entry) {
  return pathName(entry).endsWith('.css');
}

function isImageResource(entry) {
  return /\.(avif|gif|jpe?g|png|webp|ico)(\?|$)/.test(pathName(entry));
}

function issueForMetric(name, value, limit, suffix = 'ms') {
  if (!Number.isFinite(value) || value <= 0) return [];
  if (value <= limit) return [];
  return [`${name} ${Math.round(value)}${suffix} exceeds ${limit}${suffix}`];
}

function issueForBytes(name, value, limit) {
  if (value <= limit) return [];
  return [`${name} ${value} bytes exceeds ${limit} bytes`];
}

async function measureCase(browser, item) {
  const context = await browser.newContext({
    viewport: { width: item.width, height: item.height },
    isMobile: Boolean(item.isMobile),
    deviceScaleFactor: item.isMobile ? 2 : 1,
  });
  const page = await context.newPage();
  await page.addInitScript(initPerformanceObserver);

  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  const response = await page.goto(absoluteUrl(item.path), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForLoadState('load', { timeout: 45000 }).catch(() => {});
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  await page.waitForTimeout(700);

  const metrics = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    const paint = Object.fromEntries(performance.getEntriesByType('paint').map((entry) => [entry.name, Math.round(entry.startTime)]));
    const resources = performance.getEntriesByType('resource').map((entry) => ({
      name: entry.name,
      initiatorType: entry.initiatorType,
      transferSize: entry.transferSize || 0,
      encodedBodySize: entry.encodedBodySize || 0,
      duration: Math.round(entry.duration || 0),
      startTime: Math.round(entry.startTime || 0),
    }));
    return {
      title: document.title,
      h1: document.querySelector('h1')?.textContent?.trim() || '',
      navCount: document.querySelectorAll('nav a').length,
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      timing: nav ? {
        responseStart: Math.round(nav.responseStart),
        domContentLoaded: Math.round(nav.domContentLoadedEventEnd),
        loadEventEnd: Math.round(nav.loadEventEnd || 0),
      } : {},
      firstContentfulPaint: paint['first-contentful-paint'] || 0,
      largestContentfulPaint: window.__lovetypesPerf?.lcp || 0,
      cumulativeLayoutShift: Number((window.__lovetypesPerf?.cls || 0).toFixed(4)),
      resources,
    };
  });

  await context.close();

  const resources = metrics.resources || [];
  const scriptBytes = summarizeByType(resources, isScriptResource);
  const styleBytes = summarizeByType(resources, isStyleResource);
  const imageBytes = summarizeByType(resources, isImageResource);
  const totalBytes = resources.reduce((sum, entry) => sum + bytesOf(entry), 0);
  const largestResources = [...resources]
    .sort((a, b) => bytesOf(b) - bytesOf(a))
    .slice(0, 4)
    .map((entry) => `${bytesOf(entry)} ${entry.initiatorType || 'resource'} ${new URL(entry.name).pathname}`);

  const budgets = BUDGETS[IS_PUBLIC ? 'public' : 'local'];
  const issues = [
    ...(!response || response.status() >= 400 ? [`HTTP status ${response?.status() || 'missing'}`] : []),
    ...(!metrics.title ? ['missing title'] : []),
    ...(!metrics.h1 ? ['missing h1'] : []),
    ...(metrics.navCount < 4 ? [`navigation too small: ${metrics.navCount}`] : []),
    ...(metrics.horizontalOverflow ? ['horizontal overflow'] : []),
    ...consoleErrors.map((message) => `console error: ${message}`),
    ...pageErrors.map((message) => `page error: ${message}`),
    ...issueForMetric('FCP', metrics.firstContentfulPaint, budgets.firstContentfulPaint),
    ...issueForMetric('LCP', metrics.largestContentfulPaint, budgets.largestContentfulPaint),
    ...issueForMetric('DOMContentLoaded', metrics.timing.domContentLoaded, budgets.domContentLoaded),
    ...issueForMetric('Load', metrics.timing.loadEventEnd, budgets.loadEventEnd),
    ...(metrics.cumulativeLayoutShift > budgets.cls ? [`CLS ${metrics.cumulativeLayoutShift} exceeds ${budgets.cls}`] : []),
    ...issueForBytes('total transfer', totalBytes, budgets.totalBytes),
    ...issueForBytes('script transfer', scriptBytes, budgets.scriptBytes),
    ...issueForBytes('style transfer', styleBytes, budgets.styleBytes),
    ...issueForBytes('image transfer', imageBytes, budgets.imageBytes),
  ];

  return {
    name: item.name,
    url: absoluteUrl(item.path),
    status: response?.status() || 0,
    title: metrics.title,
    h1: metrics.h1,
    firstContentfulPaint: metrics.firstContentfulPaint,
    largestContentfulPaint: metrics.largestContentfulPaint,
    cumulativeLayoutShift: metrics.cumulativeLayoutShift,
    responseStart: metrics.timing.responseStart || 0,
    domContentLoaded: metrics.timing.domContentLoaded || 0,
    loadEventEnd: metrics.timing.loadEventEnd || 0,
    resourceCount: resources.length,
    totalBytes,
    scriptBytes,
    styleBytes,
    imageBytes,
    largestResources,
    issues,
  };
}

async function main() {
  const playwright = await loadPlaywright();
  const browser = await playwright.chromium.launch(await browserLaunchOptions());
  const results = [];
  try {
    for (const item of CASES) {
      console.error(`[perf] ${item.name}`);
      results.push(await measureCase(browser, item));
    }
  } finally {
    await browser.close();
  }

  const issues = results.flatMap((result) => result.issues.map((issue) => `${result.name}: ${issue}`));
  const worstLcp = Math.max(...results.map((result) => result.largestContentfulPaint || 0));
  const worstCls = Math.max(...results.map((result) => result.cumulativeLayoutShift || 0));
  const maxTransfer = Math.max(...results.map((result) => result.totalBytes || 0));

  console.log(`runtime_performance_mode=${MODE}`);
  console.log(`runtime_performance_pages_checked=${results.length}`);
  console.log(`runtime_performance_worst_lcp_ms=${worstLcp}`);
  console.log(`runtime_performance_worst_cls=${worstCls}`);
  console.log(`runtime_performance_max_transfer_bytes=${maxTransfer}`);
  console.log(`runtime_performance_issues=${issues.length}`);
  for (const result of results) {
    console.log(
      `runtime_performance_page=${result.name} status=${result.status} fcp=${result.firstContentfulPaint} lcp=${result.largestContentfulPaint} cls=${result.cumulativeLayoutShift} dcl=${result.domContentLoaded} load=${result.loadEventEnd} bytes=${result.totalBytes} scripts=${result.scriptBytes} styles=${result.styleBytes} images=${result.imageBytes}`
    );
    console.log(`runtime_performance_largest_resources=${result.name} ${result.largestResources.join(' | ')}`);
  }
  for (const issue of issues.slice(0, 100)) console.log(issue);
  if (issues.length > 100) console.log(`... ${issues.length - 100} more issue(s)`);

  process.exitCode = issues.length ? 1 : 0;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
