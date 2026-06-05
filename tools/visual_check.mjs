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

function finalPath(page) {
  const current = new URL(page.url());
  return `${current.pathname}${current.hash}`;
}

function shouldCheckCloudflareRedirects() {
  if (process.env.CHECK_REDIRECTS === '1') return true;
  const hostname = new URL(makeUrl('/')).hostname;
  return hostname === 'lovetypes.tw' || hostname.endsWith('.lovetypes.pages.dev');
}

function hasBlockingConsoleMessage(message) {
  return ['error'].includes(message.type());
}

function isRetriableNavigationError(error) {
  const message = String(error?.message || error || '');
  return [
    'ERR_TIMED_OUT',
    'ERR_CONNECTION_RESET',
    'ERR_CONNECTION_CLOSED',
    'ERR_HTTP2_PROTOCOL_ERROR',
    'Timeout',
  ].some((token) => message.includes(token));
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function networkIdleTimeout() {
  return Number(process.env.VISUAL_CHECK_NETWORKIDLE_TIMEOUT_MS || 1000);
}

function actionTimeout() {
  return Number(process.env.VISUAL_CHECK_ACTION_TIMEOUT_MS || 10000);
}

function navigationTimeout() {
  return Number(process.env.VISUAL_CHECK_NAVIGATION_TIMEOUT_MS || 45000);
}

function totalTimeout() {
  return Number(process.env.VISUAL_CHECK_TOTAL_TIMEOUT_MS || 540000);
}

function logCase(name) {
  console.error(`[visual] ${name}`);
}

function summarizeFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (!result.title) failures.push('missing title');
    if (!result.h1) failures.push('missing h1');
    if (result.navCount < 4) failures.push('navigation too small');
    if (result.textLength < 120) failures.push('page text too short');
    if (result.name.startsWith('home-') && result.universeGateCount !== 5) failures.push('missing five universe gates');
    if (result.name.startsWith('characters-') && result.universeMapCount !== 1) failures.push('missing universe map');
    if (result.name.startsWith('characters-') && result.guardianCardCount !== 5) failures.push('missing guardian universe cards');
    if (result.name.startsWith('characters-') && result.guardianNeedCardCount !== 5) failures.push('missing guardian need router cards');
    if (result.name.startsWith('characters-') && result.guardianCardHeightSpread > 120) failures.push('guardian cards have unstable heights');
    if (result.name.startsWith('guides-') && result.guideDomainRouteCount !== 5) failures.push('missing guide guardian reading routes');
    if (result.name.startsWith('guide-detail-') && result.guideActionCardCount !== 4) failures.push('missing guide action bridge cards');
    if (result.name.startsWith('guide-detail-') && !result.guideActionLunaHref?.includes('/luna-yoga-music/#luna-')) failures.push('missing guide Luna bridge');
    if (result.name.startsWith('resources-') && result.supplyDomainRouteCount !== 5) failures.push('missing five supply domain routes');
    if (result.name.startsWith('keepsakes-') && result.keepsakeShelfCount !== 5) failures.push('missing five keepsake shelf cards');
    if (result.name.startsWith('keepsakes-') && result.keepsakeRitualCount !== 4) failures.push('missing keepsake ritual route');
    if (result.name.startsWith('about-') && result.aboutTrustCardCount !== 4) failures.push('missing about trust charter cards');
    if ((result.name.startsWith('contact-') || result.name.startsWith('privacy-') || result.name.startsWith('terms-')) && result.policyCompassCardCount !== 3) failures.push('missing policy compass cards');
    if ((result.name.startsWith('contact-') || result.name.startsWith('privacy-') || result.name.startsWith('terms-')) && result.policyDetailCardCount !== 3) failures.push('missing policy detail cards');
    if (result.name.startsWith('guardian-') && result.domainMarkerCount < 1) failures.push('missing guardian domain marker');
    if (result.name.startsWith('guardian-') && result.supplyCtaCount < 1) failures.push('missing guardian supply CTA');
    if (result.expectedFinalPath && result.finalUrl !== result.expectedFinalPath) {
      failures.push(`expected final path ${result.expectedFinalPath}, got ${result.finalUrl}`);
    }
    if (result.horizontalOverflow) failures.push('horizontal overflow');
    if (result.consoleErrors.length) failures.push('console errors');
    if (result.pageErrors.length) failures.push('page errors');
    return failures.map((failure) => `${result.name}: ${failure}`);
  });
}

function summarizeQuizFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (!result.resultName) failures.push('missing result name');
    if (!result.progressbarOk) failures.push('quiz progressbar ARIA did not initialize');
    if (!result.optionGroupOk) failures.push('quiz options are not labelled by the question');
    if (!result.optionPressedOk) failures.push('quiz option aria-pressed did not update');
    if (!result.nextDisabledOk) failures.push('quiz next button was not disabled before selecting');
    if (!result.nextEnabledOk) failures.push('quiz next button did not enable after selecting');
    if (!result.primaryRouteHref?.includes('/resources/#supply-')) failures.push('missing primary supply route');
    if (!result.planHref?.includes('/repair-plan/#plan-')) failures.push('missing repair plan route');
    if (!result.lunaHref?.includes('/luna-yoga-music/#luna-')) failures.push('missing personalized Luna route');
    if (!result.guideHref?.includes('/guides/') || !result.guideHref?.includes('#guide-')) failures.push('missing personalized guide route');
    if (!result.keepsakeHref?.includes('/keepsakes/#keepsake-')) failures.push('missing personalized keepsake route');
    if (!result.bookHref?.startsWith('https://')) failures.push('missing affiliate book route');
    if (!result.bookRel?.includes('sponsored')) failures.push('missing sponsored rel');
    if (result.dynamicImageIssues?.length) failures.push(`dynamic image issues: ${result.dynamicImageIssues.join('; ')}`);
    if (result.horizontalOverflow) failures.push('horizontal overflow');
    if (result.consoleErrors.length) failures.push('console errors');
    if (result.pageErrors.length) failures.push('page errors');
    return failures.map((failure) => `${result.name}: ${failure}`);
  });
}

function summarizeConversionFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    const target = result.target || '';
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (target === 'route' && !result.url?.includes('/resources/#supply-')) failures.push('did not land on supply route');
    if (['plan', 'keepsake-plan', 'home-saved-plan'].includes(target) && !result.url?.includes('/repair-plan/#plan-')) failures.push('did not land on repair plan');
    if (target === 'luna' && !result.url?.includes('/luna-yoga-music/#luna-')) failures.push('did not land on Luna route');
    if (target === 'guide' && (!result.url?.includes('/guides/') || !result.url?.includes('#guide-'))) failures.push('did not land on guide route');
    if (target === 'keepsake' && !result.url?.includes('/keepsakes/#keepsake-')) failures.push('did not land on keepsake route');
    if (target === 'route' && !result.supplyResumeVisible) failures.push('missing personalized supply resume');
    if (target === 'route' && !result.supplyResumeImageHiddenOk) failures.push('personalized supply resume image is visible on mobile');
    if (target === 'route' && result.supplyResumeActionCount < 3) failures.push('personalized supply resume is missing next-step actions');
    if (target === 'route' && !result.supplyResumeFirstActionInViewport) failures.push('personalized supply resume first action is below the mobile viewport');
    if (['plan', 'keepsake-plan', 'home-saved-plan'].includes(target) && !result.repairResumeVisible) failures.push('missing personalized repair resume');
    if (target === 'luna' && !result.lunaResumeVisible) failures.push('missing personalized Luna resume');
    if (target === 'guide' && !result.guideResumeVisible) failures.push('missing personalized guide resume');
    if (target === 'keepsake' && !result.keepsakeResumeVisible) failures.push('missing personalized keepsake resume');
    if (['plan', 'keepsake-plan', 'home-saved-plan'].includes(target) && !result.repairFillPrimary) failures.push('repair fill is not the primary action');
    if (['plan', 'keepsake-plan', 'home-saved-plan'].includes(target) && !result.repairFilled) failures.push('repair worksheet was not filled from result');
    if (target === 'luna' && !result.lunaPrimaryHref?.includes('/repair-plan/#plan-')) failures.push('Luna primary action does not continue repair plan');
    if (target === 'guide' && !result.guidePlanHref?.includes('/repair-plan/#plan-')) failures.push('guide resume does not continue repair plan');
    if (['keepsake', 'keepsake-plan'].includes(target) && !result.keepsakePrimaryHref?.includes('/repair-plan/#plan-')) failures.push('keepsake primary action does not continue repair plan');
    if (target === 'home-saved-plan' && !result.homeSavedVisible) failures.push('missing returning visitor saved result');
    if (target === 'home-saved-plan' && !result.homeSavedKeepsakeHref?.includes('/keepsakes/#keepsake-')) failures.push('home saved card does not continue keepsake hall');
    if (result.dynamicImageIssues?.length) failures.push(`dynamic image issues: ${result.dynamicImageIssues.join('; ')}`);
    if (result.scrollY > 1200) failures.push('resume scrolled too far');
    if (result.horizontalOverflow) failures.push('horizontal overflow');
    if (result.consoleErrors.length) failures.push('console errors');
    if (result.pageErrors.length) failures.push('page errors');
    return failures.map((failure) => `${result.name}: ${failure}`);
  });
}

function summarizeRedirectFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (!result.redirected) failures.push('did not redirect');
    if (result.finalUrl !== result.expectedFinalPath) {
      failures.push(`expected final path ${result.expectedFinalPath}, got ${result.finalUrl}`);
    }
    if (result.consoleErrors.length) failures.push('console errors');
    if (result.pageErrors.length) failures.push('page errors');
    return failures.map((failure) => `${result.name}: ${failure}`);
  });
}

function summarizeLanguageMenuFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (!result.menuOpened) failures.push('language menu did not open');
    if (!result.outsideCloseOk) failures.push('language menu did not close on outside click');
    if (!result.escapeCloseOk) failures.push('language menu did not close on Escape');
    if (result.linkCount !== 5) failures.push(`expected 5 language links, got ${result.linkCount}`);
    if (!result.activeLangOk) failures.push('active language was not marked');
    if (result.finalUrl !== result.expectedFinalPath) {
      failures.push(`expected final path ${result.expectedFinalPath}, got ${result.finalUrl}`);
    }
    if (result.horizontalOverflow) failures.push('horizontal overflow');
    if (result.consoleErrors.length) failures.push('console errors');
    if (result.pageErrors.length) failures.push('page errors');
    return failures.map((failure) => `${result.name}: ${failure}`);
  });
}

function summarizeWorksheetFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (result.fieldCount !== 4) failures.push(`expected 4 worksheet fields, got ${result.fieldCount}`);
    if (!result.statusLiveRegionOk) failures.push('worksheet status live region is not configured');
    if (!result.autosaveOk) failures.push('worksheet autosave did not persist all fields');
    if (!result.reloadRestoreOk) failures.push('worksheet values did not restore after reload');
    if (!result.clearOk) failures.push('worksheet clear did not empty fields and storage');
    if (result.horizontalOverflow) failures.push('horizontal overflow');
    if (result.consoleErrors.length) failures.push('console errors');
    if (result.pageErrors.length) failures.push('page errors');
    return failures.map((failure) => `${result.name}: ${failure}`);
  });
}

function summarizeCopyFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (!result.copyOk) failures.push('copy action did not write expected text');
    if (!result.feedbackOk) failures.push('copy action did not show feedback');
    if (result.horizontalOverflow) failures.push('horizontal overflow');
    if (result.consoleErrors.length) failures.push('console errors');
    if (result.pageErrors.length) failures.push('page errors');
    return failures.map((failure) => `${result.name}: ${failure}`);
  });
}

function summarizeAnchorFocusFailures(results) {
  return results.flatMap((result) => {
    const failures = [];
    if (!result.status || result.status >= 400) failures.push('bad status');
    if (!result.focusOk) failures.push(`expected focus on ${result.expectedFocusId}, got ${result.activeId || 'none'}`);
    if (!result.scrollOk) failures.push('anchor did not move viewport near the target');
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
  { name: 'characters-desktop', path: '/characters/', viewport: { width: 1280, height: 900 } },
  { name: 'characters-mobile', path: '/characters/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-iris-desktop', path: '/characters/iris/', viewport: { width: 1280, height: 900 } },
  { name: 'guardian-noah-desktop', path: '/characters/noah/', viewport: { width: 1280, height: 900 } },
  { name: 'guardian-vivian-desktop', path: '/characters/vivian/', viewport: { width: 1280, height: 900 } },
  { name: 'guardian-claire-desktop', path: '/characters/claire/', viewport: { width: 1280, height: 900 } },
  { name: 'guardian-dora-desktop', path: '/characters/dora/', viewport: { width: 1280, height: 900 } },
  { name: 'resources-desktop', path: '/resources/', viewport: { width: 1280, height: 900 } },
  { name: 'resources-mobile', path: '/resources/', viewport: { width: 390, height: 844 } },
  { name: 'repair-plan-mobile', path: '/repair-plan/', viewport: { width: 390, height: 844 } },
  { name: 'keepsakes-mobile', path: '/keepsakes/', viewport: { width: 390, height: 844 } },
  { name: 'luna-mobile', path: '/luna/', viewport: { width: 390, height: 844 } },
  { name: 'theory-desktop', path: '/theory/', viewport: { width: 1280, height: 900 } },
  { name: 'theory-mobile', path: '/theory/', viewport: { width: 390, height: 844 } },
  { name: 'about-desktop', path: '/about/', viewport: { width: 1280, height: 900 } },
  { name: 'about-mobile', path: '/about/', viewport: { width: 390, height: 844 } },
  { name: 'contact-desktop', path: '/contact/', viewport: { width: 1280, height: 900 } },
  { name: 'contact-mobile', path: '/contact/', viewport: { width: 390, height: 844 } },
  { name: 'privacy-mobile', path: '/privacy/', viewport: { width: 390, height: 844 } },
  { name: 'terms-mobile', path: '/terms/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-iris-mobile', path: '/characters/iris/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-noah-mobile', path: '/characters/noah/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-vivian-mobile', path: '/characters/vivian/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-claire-mobile', path: '/characters/claire/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-dora-mobile', path: '/characters/dora/', viewport: { width: 390, height: 844 } },
  { name: 'guides-mobile', path: '/guides/', viewport: { width: 390, height: 844 } },
  { name: 'guide-detail-mobile', path: '/guides/words-of-affirmation-scripts/', viewport: { width: 390, height: 844 } },
  { name: 'guide-detail-en-desktop', path: '/en/guides/quality-time-long-distance/', viewport: { width: 1280, height: 900 } },
  { name: 'en-home-mobile', path: '/en/', viewport: { width: 390, height: 844 } },
  { name: 'ja-repair-plan-mobile', path: '/ja/repair-plan/', viewport: { width: 390, height: 844 } },
  { name: 'es-guides-desktop', path: '/es/guides/', viewport: { width: 1280, height: 900 } },
];

const redirectCases = shouldCheckCloudflareRedirects()
  ? [
      { name: 'redirect-luna-zh', path: '/luna/', expectedFinalPath: '/luna-yoga-music/' },
      { name: 'redirect-luna-en', path: '/en/luna/', expectedFinalPath: '/en/luna-yoga-music/' },
      { name: 'redirect-luna-ja', path: '/ja/luna/', expectedFinalPath: '/ja/luna-yoga-music/' },
      { name: 'redirect-luna-ko', path: '/ko/luna/', expectedFinalPath: '/ko/luna-yoga-music/' },
      { name: 'redirect-luna-es', path: '/es/luna/', expectedFinalPath: '/es/luna-yoga-music/' },
    ]
  : [];

const languageMenuCases = [
  { name: 'language-menu-home-mobile', path: '/', currentLang: 'zh-TW', targetLang: 'en', expectedFinalPath: '/en/' },
  { name: 'language-menu-resources-mobile', path: '/resources/', currentLang: 'zh-TW', targetLang: 'ja', expectedFinalPath: '/ja/resources/' },
  { name: 'language-menu-guide-mobile', path: '/es/guides/words-of-affirmation-scripts/', currentLang: 'es', targetLang: 'ko', expectedFinalPath: '/ko/guides/words-of-affirmation-scripts/' },
];

const quizCases = [
  { name: 'quiz-flow-desktop', path: '/', viewport: { width: 1280, height: 900 } },
  { name: 'quiz-flow-mobile', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'quiz-flow-en-mobile', path: '/en/', viewport: { width: 390, height: 844 } },
  { name: 'quiz-flow-ja-mobile', path: '/ja/', viewport: { width: 390, height: 844 } },
  { name: 'quiz-flow-ko-mobile', path: '/ko/', viewport: { width: 390, height: 844 } },
  { name: 'quiz-flow-es-mobile', path: '/es/', viewport: { width: 390, height: 844 } },
];

const conversionCases = [
  { name: 'conversion-supply-mobile', target: 'route', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-repair-mobile', target: 'plan', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-luna-mobile', target: 'luna', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-guide-mobile', target: 'guide', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-keepsake-mobile', target: 'keepsake', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-keepsake-to-repair-mobile', target: 'keepsake-plan', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-home-saved-to-repair-mobile', target: 'home-saved-plan', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-en-supply-mobile', target: 'route', path: '/en/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-ja-repair-mobile', target: 'plan', path: '/ja/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-ko-luna-mobile', target: 'luna', path: '/ko/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-es-guide-mobile', target: 'guide', path: '/es/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-en-keepsake-mobile', target: 'keepsake', path: '/en/', viewport: { width: 390, height: 844 } },
];

const worksheetCases = [
  { name: 'worksheet-autosave-mobile', path: '/repair-plan/', viewport: { width: 390, height: 844 } },
  { name: 'worksheet-autosave-en-desktop', path: '/en/repair-plan/', viewport: { width: 1280, height: 900 } },
];

const copyCases = [
  { name: 'copy-quiz-result-mobile', target: 'quiz-result', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'copy-supply-route-mobile', target: 'supply-route', path: '/resources/', viewport: { width: 390, height: 844 } },
  { name: 'copy-repair-summary-mobile', target: 'repair-summary', path: '/repair-plan/', viewport: { width: 390, height: 844 } },
];

const anchorFocusCases = [
  { name: 'anchor-focus-direct-quiz-mobile', mode: 'direct', path: '/#quiz-section', expectedFocusId: 'quiz-section', viewport: { width: 390, height: 844 } },
  { name: 'anchor-focus-click-quiz-mobile', mode: 'click', path: '/', selector: '.hero-actions .primary-btn[href="#quiz-section"]', expectedFocusId: 'quiz-section', viewport: { width: 390, height: 844 } },
];

await mkdir('output/playwright', { recursive: true });
const executablePath = await findCachedChromium();
const browser = await chromium.launch({ headless: true, executablePath });
const results = [];
const watchdog = setTimeout(() => {
  console.error(`Visual check exceeded ${totalTimeout()}ms.`);
  process.exit(124);
}, totalTimeout());
watchdog.unref?.();

async function createPage(viewport) {
  const page = await browser.newPage({ viewport });
  page.setDefaultTimeout(actionTimeout());
  page.setDefaultNavigationTimeout(navigationTimeout());
  return page;
}

async function openPage(page, url) {
  const maxAttempts = Number(process.env.VISUAL_CHECK_NAV_ATTEMPTS || 3);
  let lastError;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: navigationTimeout() });
      await page.waitForLoadState('load', { timeout: 10000 }).catch(() => {});
      await page.waitForLoadState('networkidle', { timeout: networkIdleTimeout() }).catch(() => {});
      return response;
    } catch (error) {
      lastError = error;
      if (attempt >= maxAttempts || !isRetriableNavigationError(error)) {
        throw error;
      }
      console.warn(`Retrying navigation ${attempt + 1}/${maxAttempts}: ${url}`);
      await delay(1000 * attempt);
    }
  }
  throw lastError;
}

async function waitForSoftIdle(page) {
  await page.waitForLoadState('domcontentloaded', { timeout: 10000 }).catch(() => {});
  await page.waitForLoadState('load', { timeout: 10000 }).catch(() => {});
  await page.waitForLoadState('networkidle', { timeout: networkIdleTimeout() }).catch(() => {});
}

for (const item of cases) {
  logCase(item.name);
  const page = await createPage(item.viewport);
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
  const response = await openPage(page, url);
  const title = await page.title();
  const h1 = await page.locator('h1').first().innerText().catch(() => '');
  const navCount = await page.locator('.nav-links a').count();
  const bodyText = await page.locator('body').innerText();
  const universeGateCount = await page.locator('[data-universe-gates] .universe-gate-card').count();
  const universeMapCount = await page.locator('[data-universe-map]').count();
  const guardianCardCount = await page.locator('[data-universe-map] .guardian-card').count();
  const guardianNeedCardCount = await page.locator('[data-guardian-need-router] .guardian-need-card').count();
  const guideDomainRouteCount = await page.locator('[data-guide-domain-routes] .guide-domain-card').count();
  const guideActionCardCount = await page.locator('[data-guide-action-bridge] .guide-action-card').count();
  const guideActionLunaHref = await page.locator('[data-guide-action-bridge] a[href*="/luna-yoga-music/#luna-"]').first().getAttribute('href').catch(() => '');
  const supplyDomainRouteCount = await page.locator('[data-supply-domain-strip] .supply-quick-card').count();
  const keepsakeShelfCount = await page.locator('[data-keepsake-shelf] .keepsake-shelf-card').count();
  const keepsakeRitualCount = await page.locator('[data-keepsake-ritual] .keepsake-ritual-card').count();
  const aboutTrustCardCount = await page.locator('[data-about-trust] .about-trust-card').count();
  const policyCompassCardCount = await page.locator('[data-policy-compass] .policy-compass-card').count();
  const policyDetailCardCount = await page.locator('[data-policy-detail] .policy-detail-card').count();
  const guardianCardHeightSpread = await page.locator('[data-universe-map] .guardian-card').evaluateAll((cards) => {
    if (!cards.length) return 0;
    const heights = cards.map((card) => card.getBoundingClientRect().height);
    return Math.round(Math.max(...heights) - Math.min(...heights));
  }).catch(() => 0);
  const domainMarkerCount = await page.locator('[data-domain-marker]').count();
  const supplyCtaCount = await page.locator('.guardian-domain-hero .primary-btn[href*="/resources/#supply-"]').count();
  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    url,
    finalUrl: finalPath(page),
    status: response?.status(),
    title,
    h1,
    navCount,
    textLength: bodyText.length,
    universeGateCount,
    universeMapCount,
    guardianCardCount,
    guardianNeedCardCount,
    guideDomainRouteCount,
    guideActionCardCount,
    guideActionLunaHref,
    supplyDomainRouteCount,
    keepsakeShelfCount,
    keepsakeRitualCount,
    aboutTrustCardCount,
    policyCompassCardCount,
    policyDetailCardCount,
    guardianCardHeightSpread,
    domainMarkerCount,
    supplyCtaCount,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    screenshot,
  });
  await page.close();
}

for (const item of redirectCases) {
  logCase(item.name);
  const page = await createPage({ width: 390, height: 844 });
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
  const response = await openPage(page, url);
  results.push({
    name: item.name,
    url,
    finalUrl: finalPath(page),
    expectedFinalPath: item.expectedFinalPath,
    redirected: Boolean(response?.request().redirectedFrom()),
    status: response?.status(),
    title: await page.title(),
    consoleErrors,
    pageErrors,
  });
  await page.close();
}

for (const item of languageMenuCases) {
  logCase(item.name);
  const page = await createPage({ width: 390, height: 844 });
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
  const response = await openPage(page, url);
  const menu = page.locator('.language-menu').first();
  await menu.locator('summary').click();
  const menuOpened = await menu.evaluate((node) => node.hasAttribute('open')).catch(() => false);
  await page.locator('main').click({ position: { x: 8, y: 8 } });
  const outsideCloseOk = await menu.evaluate((node) => !node.hasAttribute('open')).catch(() => false);
  await menu.locator('summary').click();
  await page.keyboard.press('Escape');
  const escapeCloseOk = await menu.evaluate((node) => !node.hasAttribute('open')).catch(() => false);
  await menu.locator('summary').click();
  const linkCount = await menu.locator('.language-switcher a').count();
  const activeLangOk = await menu
    .locator(`.language-switcher a[lang="${item.currentLang}"][aria-current="page"]`)
    .count()
    .then((count) => count === 1)
    .catch(() => false);
  await menu.locator(`.language-switcher a[lang="${item.targetLang}"]`).first().click();
  await waitForSoftIdle(page);
  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    url,
    finalUrl: finalPath(page),
    expectedFinalPath: item.expectedFinalPath,
    status: response?.status(),
    title: await page.title(),
    h1: await page.locator('h1').first().innerText().catch(() => ''),
    menuOpened,
    outsideCloseOk,
    escapeCloseOk,
    linkCount,
    activeLangOk,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    screenshot,
  });
  await page.close();
}

for (const item of quizCases) {
  logCase(item.name);
  const page = await createPage(item.viewport);
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
  const response = await openPage(page, url);
  await page.evaluate(() => localStorage.clear());
  await page.locator('[data-quiz-start]').first().click();

  const firstProgress = page.locator('.quiz-progress-bar[role="progressbar"]').first();
  const progressbarOk = await firstProgress.evaluate((node) =>
    node.getAttribute('aria-valuemin') === '0'
    && node.getAttribute('aria-valuemax') === '15'
    && node.getAttribute('aria-valuenow') === '1'
    && Boolean(node.getAttribute('aria-label'))
  ).catch(() => false);
  const optionGroupOk = await page.locator('.quiz-options').first().evaluate((node) => {
    const labelId = node.getAttribute('aria-labelledby');
    return node.getAttribute('role') === 'group'
      && Boolean(labelId)
      && Boolean(document.getElementById(labelId));
  }).catch(() => false);
  const firstOption = page.locator('.quiz-option').first();
  const nextButton = page.locator('.quiz-next').first();
  const nextDisabledOk = await nextButton.isDisabled().catch(() => false);
  const optionInitiallyFalse = await firstOption.getAttribute('aria-pressed').then((value) => value === 'false').catch(() => false);
  await firstOption.click();
  const optionPressedTrue = await firstOption.getAttribute('aria-pressed').then((value) => value === 'true').catch(() => false);
  const nextEnabledOk = await nextButton.isEnabled().catch(() => false);
  const optionPressedOk = optionInitiallyFalse && optionPressedTrue;
  await nextButton.click();

  for (let index = 1; index < 15; index += 1) {
    await page.locator('.quiz-option').first().click();
    await page.locator('.quiz-next').click();
  }

  await page.locator('.quiz-result-card').waitFor({ state: 'visible' });
  await page.waitForFunction(() => {
    const image = document.querySelector('.quiz-result-card img');
    return image && image.complete && image.naturalWidth > 0;
  });
  await page.evaluate(() => new Promise((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(resolve));
  }));
  const resultName = await page.locator('.quiz-result-card h3').first().innerText().catch(() => '');
  const primaryRouteHref = await page.locator('[data-conversion-route]').first().getAttribute('href');
  const planHref = await page.locator('[data-conversion-plan]').first().getAttribute('href');
  const lunaHref = await page.locator('[data-conversion-luna]').first().getAttribute('href');
  const guideHref = await page.locator('[data-conversion-guide]').first().getAttribute('href');
  const keepsakeHref = await page.locator('[data-conversion-keepsake]').first().getAttribute('href');
  const book = page.locator('[data-conversion-book]').first();
  const bookHref = await book.getAttribute('href');
  const bookRel = await book.getAttribute('rel');
  const dynamicImageIssues = await page.locator('.quiz-result-card img, .quiz-collector-card img').evaluateAll((images) => images.flatMap((image) => {
    const issues = [];
    const label = image.getAttribute('alt') || image.getAttribute('src') || 'dynamic image';
    if (!image.getAttribute('width') || !image.getAttribute('height')) issues.push(`${label} missing width/height`);
    if (image.getAttribute('decoding') !== 'async') issues.push(`${label} missing async decoding`);
    if (image.closest('.quiz-result-card') && image.getAttribute('fetchpriority') !== 'high') issues.push(`${label} result image not high priority`);
    if (image.closest('.quiz-collector-card') && image.getAttribute('fetchpriority') !== 'low') issues.push(`${label} collector image not low priority`);
    return issues;
  }));
  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    url,
    finalUrl: finalPath(page),
    status: response?.status(),
    title: await page.title(),
    h1: await page.locator('h1').first().innerText().catch(() => ''),
    navCount: await page.locator('.nav-links a').count(),
    textLength: (await page.locator('body').innerText()).length,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    resultName,
    progressbarOk,
    optionGroupOk,
    optionPressedOk,
    nextDisabledOk,
    nextEnabledOk,
    primaryRouteHref,
    planHref,
    lunaHref,
    guideHref,
    keepsakeHref,
    bookHref,
    bookRel,
    dynamicImageIssues,
    screenshot,
  });
  await page.close();
}

for (const item of conversionCases) {
  logCase(item.name);
  const page = await createPage(item.viewport);
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
  const response = await openPage(page, url);
  await page.evaluate(() => localStorage.clear());
  await page.locator('[data-quiz-start]').first().click();

  for (let index = 0; index < 15; index += 1) {
    await page.locator('.quiz-option').first().click();
    await page.locator('.quiz-next').click();
  }

  let homeSavedVisible = false;
  let homeSavedKeepsakeHref = '';
  if (item.target === 'plan') {
    await page.locator('[data-conversion-plan]').click();
  } else if (item.target === 'luna') {
    await page.locator('[data-conversion-luna]').click();
  } else if (item.target === 'guide') {
    await page.locator('[data-conversion-guide]').click();
  } else if (item.target === 'keepsake-plan') {
    await page.locator('[data-conversion-keepsake]').click();
  } else if (item.target === 'home-saved-plan') {
    await openPage(page, url);
    await page.locator('[data-quiz-saved]:not([hidden])').waitFor({ state: 'visible' });
    homeSavedVisible = true;
    homeSavedKeepsakeHref = await page.locator('[data-home-saved-keepsake]').first().getAttribute('href').catch(() => '');
    await page.locator('[data-home-saved-plan]').click();
  } else if (item.target === 'keepsake') {
    await page.locator('[data-conversion-keepsake]').click();
  } else {
    await page.locator('[data-conversion-route]').click();
  }
  await waitForSoftIdle(page);
  let keepsakePrimaryHref = '';
  if (item.target === 'keepsake-plan') {
    await page.locator('[data-keepsake-saved]:not([hidden])').waitFor({ state: 'visible' });
    keepsakePrimaryHref = await page.locator('[data-keepsake-saved] .primary-btn').first().getAttribute('href').catch(() => '');
    await page.locator('[data-keepsake-plan]').click();
    await waitForSoftIdle(page);
  }
  const finalTarget = ['keepsake-plan', 'home-saved-plan'].includes(item.target) ? 'plan' : item.target;
  const resumeSelector = finalTarget === 'plan'
    ? '[data-repair-saved]:not([hidden])'
    : finalTarget === 'luna'
      ? '[data-luna-saved]:not([hidden])'
      : finalTarget === 'guide'
        ? '[data-guide-saved]:not([hidden])'
        : finalTarget === 'keepsake'
          ? '[data-keepsake-saved]:not([hidden])'
      : '[data-supply-saved]:not([hidden])';
  await page.locator(resumeSelector).waitFor({ state: 'visible' });
  await page.waitForFunction(() => window.scrollY < 1200);
  const resumeScrollY = await page.evaluate(() => window.scrollY);
  let repairFillPrimary = false;
  let repairFilled = false;
  let lunaPrimaryHref = '';
  let guidePlanHref = '';
  if (finalTarget === 'plan') {
    repairFillPrimary = await page.locator('[data-repair-saved] .primary-btn[data-fill-repair]').isVisible().catch(() => false);
    await page.locator('[data-repair-saved] [data-fill-repair]').click();
    await page.waitForFunction(() => {
      const fields = [...document.querySelectorAll('[data-repair-worksheet] textarea[data-field]')];
      return fields.length >= 4 && fields.every((field) => field.value.trim().length > 0);
    });
    repairFilled = true;
  } else if (finalTarget === 'luna') {
    lunaPrimaryHref = await page.locator('[data-luna-saved] .primary-btn').first().getAttribute('href').catch(() => '');
  } else if (finalTarget === 'guide') {
    guidePlanHref = await page.locator('[data-guide-saved] a').first().getAttribute('href').catch(() => '');
  } else if (finalTarget === 'keepsake') {
    keepsakePrimaryHref = await page.locator('[data-keepsake-saved] .primary-btn').first().getAttribute('href').catch(() => '');
  }

  const dynamicImageIssues = await page.locator(`${resumeSelector} img`).evaluateAll((images) => images.flatMap((image) => {
    const issues = [];
    const label = image.getAttribute('alt') || image.getAttribute('src') || 'resume image';
    if (!image.getAttribute('width') || !image.getAttribute('height')) issues.push(`${label} missing width/height`);
    if (image.getAttribute('decoding') !== 'async') issues.push(`${label} missing async decoding`);
    return issues;
  }));
  const supplyResumeImageHiddenOk = finalTarget !== 'route'
    ? true
    : await page.locator(`${resumeSelector} img`).evaluateAll((images) => images.length === 0 || images.every((image) => {
      const style = window.getComputedStyle(image);
      const rect = image.getBoundingClientRect();
      return style.display === 'none' || style.visibility === 'hidden' || rect.width === 0 || rect.height === 0;
    }));
  const supplyResumeActionCount = finalTarget === 'route'
    ? await page.locator(`${resumeSelector} .supply-resume-next a`).count()
    : 0;
  const supplyResumeFirstActionInViewport = finalTarget !== 'route'
    ? true
    : await page.locator(`${resumeSelector} .supply-resume-next a`).first().evaluate((link) => {
      const rect = link.getBoundingClientRect();
      return rect.top >= 0 && rect.top < window.innerHeight && rect.left >= 0 && rect.right <= window.innerWidth;
    }).catch(() => false);
  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    target: item.target,
    url: finalPath(page),
    finalUrl: finalPath(page),
    status: response?.status(),
    title: await page.title(),
    h1: await page.locator('h1').first().innerText().catch(() => ''),
    navCount: await page.locator('.nav-links a').count(),
    textLength: (await page.locator('body').innerText()).length,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    supplyResumeVisible: await page.locator('[data-supply-saved]:not([hidden])').isVisible().catch(() => false),
    supplyResumeImageHiddenOk,
    supplyResumeActionCount,
    supplyResumeFirstActionInViewport,
    repairResumeVisible: await page.locator('[data-repair-saved]:not([hidden])').isVisible().catch(() => false),
    lunaResumeVisible: await page.locator('[data-luna-saved]:not([hidden])').isVisible().catch(() => false),
    guideResumeVisible: await page.locator('[data-guide-saved]:not([hidden])').isVisible().catch(() => false),
    keepsakeResumeVisible: await page.locator('[data-keepsake-saved]:not([hidden])').isVisible().catch(() => false),
    repairFillPrimary,
    repairFilled,
    lunaPrimaryHref,
    guidePlanHref,
    keepsakePrimaryHref,
    homeSavedVisible,
    homeSavedKeepsakeHref,
    dynamicImageIssues,
    scrollY: resumeScrollY,
    finalScrollY: await page.evaluate(() => window.scrollY),
    screenshot,
  });
  await page.close();
}

for (const item of worksheetCases) {
  logCase(item.name);
  const page = await createPage(item.viewport);
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
  const response = await openPage(page, url);
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'domcontentloaded' });
  await waitForSoftIdle(page);

  const fields = page.locator('[data-repair-worksheet] textarea[data-field]');
  const fieldCount = await fields.count();
  const statusLiveRegionOk = await page.locator('[data-worksheet-status]').evaluate((node) =>
    node.getAttribute('role') === 'status' && node.getAttribute('aria-live') === 'polite'
  ).catch(() => false);
  const values = [
    `${item.name} guardian`,
    `${item.name} wound`,
    `${item.name} request`,
    `${item.name} supply`,
  ];

  for (let index = 0; index < Math.min(fieldCount, values.length); index += 1) {
    await fields.nth(index).fill(values[index]);
  }

  const autosaveOk = await page.waitForFunction((expected) => {
    return Object.entries(localStorage).some(([key, value]) => {
      if (!key.includes('repair-worksheet')) return false;
      try {
        const parsed = JSON.parse(value);
        return expected.every((item, index) => parsed[index] === item);
      } catch (_error) {
        return false;
      }
    });
  }, values, { timeout: 5000 }).then(() => true).catch(() => false);

  await page.reload({ waitUntil: 'domcontentloaded' });
  await waitForSoftIdle(page);
  const restoredValues = await page.locator('[data-repair-worksheet] textarea[data-field]').evaluateAll((nodes) =>
    nodes.map((node) => node.value)
  ).catch(() => []);
  const reloadRestoreOk = values.every((value, index) => restoredValues[index] === value);

  await page.locator('[data-clear-worksheet]').click();
  const clearOk = await page.waitForFunction(() => {
    const fields = [...document.querySelectorAll('[data-repair-worksheet] textarea[data-field]')];
    const fieldsEmpty = fields.length === 4 && fields.every((field) => !field.value);
    const storageEmpty = !Object.keys(localStorage).some((key) => key.includes('repair-worksheet'));
    return fieldsEmpty && storageEmpty;
  }, undefined, { timeout: 5000 }).then(() => true).catch(() => false);

  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    url,
    finalUrl: finalPath(page),
    status: response?.status(),
    title: await page.title(),
    h1: await page.locator('h1').first().innerText().catch(() => ''),
    fieldCount,
    statusLiveRegionOk,
    autosaveOk,
    reloadRestoreOk,
    clearOk,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    screenshot,
  });
  await page.close();
}

for (const item of copyCases) {
  logCase(item.name);
  const page = await createPage(item.viewport);
  const consoleErrors = [];
  const pageErrors = [];

  await page.addInitScript(() => {
    window.__lovetypesCopiedText = '';
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: async (text) => {
          window.__lovetypesCopiedText = String(text || '');
        },
      },
    });
  });
  page.on('console', (message) => {
    if (hasBlockingConsoleMessage(message)) {
      consoleErrors.push(message.text());
    }
  });
  page.on('pageerror', (error) => {
    pageErrors.push(error.message);
  });

  const url = makeUrl(item.path);
  const response = await openPage(page, url);
  await page.evaluate(() => localStorage.clear());
  let copyOk = false;
  let feedbackOk = false;

  if (item.target === 'quiz-result') {
    await page.locator('[data-quiz-start]').first().click();
    for (let index = 0; index < 15; index += 1) {
      await page.locator('.quiz-option').first().click();
      await page.locator('.quiz-next').click();
    }
    await page.locator('.quiz-result-card').waitFor({ state: 'visible' });
    const button = page.locator('[data-copy-result]').first();
    const original = await button.innerText();
    await button.click();
    await page.waitForFunction(() => Boolean(window.__lovetypesCopiedText), undefined, { timeout: 5000 });
    const copiedText = await page.evaluate(() => window.__lovetypesCopiedText);
    const updated = await button.innerText();
    copyOk = copiedText.includes('艾莉絲') && copiedText.includes('/assets/lovetypes/share/iris-story-zh.webp');
    feedbackOk = updated !== original;
  } else if (item.target === 'supply-route') {
    const button = page.locator('[data-copy-supply-route]').first();
    const original = await button.innerText();
    await button.click();
    await page.waitForFunction(() => Boolean(window.__lovetypesCopiedText), undefined, { timeout: 5000 });
    const copiedText = await page.evaluate(() => window.__lovetypesCopiedText);
    const updated = await button.innerText();
    copyOk = copiedText.includes('LoveTypes') || copiedText.includes('補給路線');
    feedbackOk = updated !== original;
  } else if (item.target === 'repair-summary') {
    const fields = page.locator('[data-repair-worksheet] textarea[data-field]');
    await fields.nth(0).fill('copy smoke guardian');
    await fields.nth(1).fill('copy smoke wound');
    const button = page.locator('[data-copy-worksheet-summary]').first();
    await button.click();
    await page.waitForFunction(() => Boolean(window.__lovetypesCopiedText), undefined, { timeout: 5000 });
    const copiedText = await page.evaluate(() => window.__lovetypesCopiedText);
    const statusText = await page.locator('[data-worksheet-status]').innerText().catch(() => '');
    copyOk = copiedText.includes('copy smoke guardian') && copiedText.includes('/repair-plan/');
    feedbackOk = statusText.trim().length > 0 && !statusText.includes('至少');
  }

  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    target: item.target,
    url,
    finalUrl: finalPath(page),
    status: response?.status(),
    title: await page.title(),
    h1: await page.locator('h1').first().innerText().catch(() => ''),
    copyOk,
    feedbackOk,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    screenshot,
  });
  await page.close();
}

for (const item of anchorFocusCases) {
  logCase(item.name);
  const page = await createPage(item.viewport);
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
  const response = await openPage(page, url);
  if (item.mode === 'click') {
    await page.locator(item.selector).first().click();
  }
  await page.waitForFunction((expectedId) => {
    const target = document.getElementById(expectedId);
    if (!target) return false;
    const top = target.getBoundingClientRect().top;
    return document.activeElement?.id === expectedId && top >= -120 && top <= 420;
  }, item.expectedFocusId, { timeout: 5000 }).catch(() => {});
  const activeId = await page.evaluate(() => document.activeElement?.id || '');
  const targetTop = await page.locator(`#${item.expectedFocusId}`).evaluate((node) => Math.round(node.getBoundingClientRect().top)).catch(() => 9999);
  const scrollOk = targetTop >= -120 && targetTop <= 420;
  const focusOk = activeId === item.expectedFocusId;
  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    url,
    finalUrl: finalPath(page),
    status: response?.status(),
    title: await page.title(),
    h1: await page.locator('h1').first().innerText().catch(() => ''),
    expectedFocusId: item.expectedFocusId,
    activeId,
    focusOk,
    targetTop,
    scrollOk,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    screenshot,
  });
  await page.close();
}

await browser.close();
clearTimeout(watchdog);
console.log(JSON.stringify(results, null, 2));

const failures = [
  ...summarizeFailures(results.filter((result) => !result.name.startsWith('quiz-flow-') && !result.name.startsWith('conversion-') && !result.name.startsWith('redirect-') && !result.name.startsWith('language-menu-') && !result.name.startsWith('worksheet-') && !result.name.startsWith('copy-') && !result.name.startsWith('anchor-focus-'))),
  ...summarizeRedirectFailures(results.filter((result) => result.name.startsWith('redirect-'))),
  ...summarizeLanguageMenuFailures(results.filter((result) => result.name.startsWith('language-menu-'))),
  ...summarizeQuizFailures(results.filter((result) => result.name.startsWith('quiz-flow-'))),
  ...summarizeConversionFailures(results.filter((result) => result.name.startsWith('conversion-'))),
  ...summarizeWorksheetFailures(results.filter((result) => result.name.startsWith('worksheet-'))),
  ...summarizeCopyFailures(results.filter((result) => result.name.startsWith('copy-'))),
  ...summarizeAnchorFocusFailures(results.filter((result) => result.name.startsWith('anchor-focus-'))),
];
if (failures.length) {
  console.error(`Visual check failed:\n${failures.join('\n')}`);
  process.exit(1);
}
