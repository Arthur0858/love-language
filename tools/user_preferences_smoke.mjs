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

function makeUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

async function reducedMotionCheck(browser) {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  const response = await page.goto(makeUrl('/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  const result = await page.evaluate(() => {
    const rootStyle = window.getComputedStyle(document.documentElement);
    const card = document.querySelector('.universe-gate-card') || document.querySelector('.primary-btn');
    const cardStyle = card ? window.getComputedStyle(card) : null;
    const reveal = document.querySelector('.ritual-reveal-card');
    const revealStyle = reveal ? window.getComputedStyle(reveal) : null;
    return {
      mediaMatches: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
      htmlScrollBehavior: rootStyle.scrollBehavior,
      bodyScrollBehavior: window.getComputedStyle(document.body).scrollBehavior,
      transitionDuration: cardStyle ? cardStyle.transitionDuration : '',
      animationDuration: revealStyle ? revealStyle.animationDuration : '',
    };
  });
  await context.close();

  const issues = [];
  if (!response || response.status() >= 400) issues.push(`reduced-motion HTTP status ${response?.status() || 'missing'}`);
  if (!result.mediaMatches) issues.push('reduced-motion media query did not match');
  if (result.htmlScrollBehavior !== 'auto') issues.push(`html scroll-behavior should be auto, got ${result.htmlScrollBehavior}`);
  if (result.bodyScrollBehavior && result.bodyScrollBehavior !== 'auto') {
    issues.push(`body scroll-behavior should be auto, got ${result.bodyScrollBehavior}`);
  }
  const transitionMs = Math.max(...String(result.transitionDuration || '0s').split(',').map((value) => {
    const trimmed = value.trim();
    return trimmed.endsWith('ms') ? Number.parseFloat(trimmed) : Number.parseFloat(trimmed) * 1000;
  }));
  if (transitionMs > 1) issues.push(`reduced-motion transition duration too high: ${result.transitionDuration}`);
  return { name: 'reduced-motion-mobile', checked: 1, issues };
}

async function printCheck(browser) {
  const context = await browser.newContext({ viewport: { width: 960, height: 1200 } });
  const page = await context.newPage();
  const response = await page.goto(makeUrl('/repair-plan/'), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  await page.emulateMedia({ media: 'print' });
  const result = await page.evaluate(() => {
    const visible = (selector) => {
      const node = document.querySelector(selector);
      if (!node) return false;
      const style = window.getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
    };
    const bodyStyle = window.getComputedStyle(document.body);
    const worksheetStyle = window.getComputedStyle(document.querySelector('.repair-worksheet textarea') || document.body);
    return {
      navVisible: visible('.site-nav'),
      footerVisible: visible('.site-footer'),
      printButtonVisible: visible('.print-button'),
      worksheetVisible: visible('.repair-worksheet'),
      worksheetTextareaMinHeight: worksheetStyle.minHeight,
      bodyBackground: bodyStyle.backgroundColor,
    };
  });
  await context.close();

  const issues = [];
  if (!response || response.status() >= 400) issues.push(`print HTTP status ${response?.status() || 'missing'}`);
  if (result.navVisible) issues.push('site navigation should be hidden in print mode');
  if (result.footerVisible) issues.push('footer should be hidden in print mode');
  if (result.printButtonVisible) issues.push('print button should be hidden in print mode');
  if (!result.worksheetVisible) issues.push('repair worksheet should remain visible in print mode');
  if (Number.parseFloat(result.worksheetTextareaMinHeight) < 90) {
    issues.push(`worksheet textarea min-height too small in print mode: ${result.worksheetTextareaMinHeight}`);
  }
  if (!['rgb(255, 255, 255)', '#fff', 'white'].includes(result.bodyBackground)) {
    issues.push(`print body background should be white, got ${result.bodyBackground}`);
  }
  return { name: 'repair-plan-print', checked: 1, issues };
}

async function main() {
  const playwright = await loadPlaywright();
  const browser = await playwright.chromium.launch(await browserLaunchOptions());
  let results = [];
  try {
    console.error('[preferences] reduced-motion-mobile');
    results.push(await reducedMotionCheck(browser));
    console.error('[preferences] repair-plan-print');
    results.push(await printCheck(browser));
  } finally {
    await browser.close();
  }

  const issues = results.flatMap((result) => result.issues.map((issue) => `${result.name}: ${issue}`));
  const checks = results.reduce((sum, result) => sum + result.checked, 0);
  console.log(`user_preference_checks=${checks}`);
  console.log(`user_preference_issues=${issues.length}`);
  for (const issue of issues.slice(0, 100)) console.log(issue);
  process.exitCode = issues.length ? 1 : 0;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
