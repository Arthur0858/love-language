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
    if (result.name.startsWith('home-') && result.universeGateCount !== 5) failures.push('missing five universe gates');
    if (result.name.startsWith('characters-') && result.universeMapCount !== 1) failures.push('missing universe map');
    if (result.name.startsWith('characters-') && result.guardianCardCount !== 5) failures.push('missing guardian universe cards');
    if (result.name.startsWith('characters-') && result.guardianCardHeightSpread > 120) failures.push('guardian cards have unstable heights');
    if (result.name.startsWith('guardian-') && result.domainMarkerCount < 1) failures.push('missing guardian domain marker');
    if (result.name.startsWith('guardian-') && result.supplyCtaCount < 1) failures.push('missing guardian supply CTA');
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
  { name: 'resources-desktop', path: '/resources/', viewport: { width: 1280, height: 900 } },
  { name: 'resources-mobile', path: '/resources/', viewport: { width: 390, height: 844 } },
  { name: 'repair-plan-mobile', path: '/repair-plan/', viewport: { width: 390, height: 844 } },
  { name: 'keepsakes-mobile', path: '/keepsakes/', viewport: { width: 390, height: 844 } },
  { name: 'luna-mobile', path: '/luna/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-iris-mobile', path: '/characters/iris/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-noah-mobile', path: '/characters/noah/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-vivian-mobile', path: '/characters/vivian/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-claire-mobile', path: '/characters/claire/', viewport: { width: 390, height: 844 } },
  { name: 'guardian-dora-mobile', path: '/characters/dora/', viewport: { width: 390, height: 844 } },
  { name: 'en-home-mobile', path: '/en/', viewport: { width: 390, height: 844 } },
  { name: 'ja-repair-plan-mobile', path: '/ja/repair-plan/', viewport: { width: 390, height: 844 } },
  { name: 'es-guides-desktop', path: '/es/guides/', viewport: { width: 1280, height: 900 } },
];

const quizCases = [
  { name: 'quiz-flow-desktop', path: '/', viewport: { width: 1280, height: 900 } },
  { name: 'quiz-flow-mobile', path: '/', viewport: { width: 390, height: 844 } },
];

const conversionCases = [
  { name: 'conversion-supply-mobile', target: 'route', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-repair-mobile', target: 'plan', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-luna-mobile', target: 'luna', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-guide-mobile', target: 'guide', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-keepsake-mobile', target: 'keepsake', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-keepsake-to-repair-mobile', target: 'keepsake-plan', path: '/', viewport: { width: 390, height: 844 } },
  { name: 'conversion-home-saved-to-repair-mobile', target: 'home-saved-plan', path: '/', viewport: { width: 390, height: 844 } },
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
  const universeGateCount = await page.locator('[data-universe-gates] .universe-gate-card').count();
  const universeMapCount = await page.locator('[data-universe-map]').count();
  const guardianCardCount = await page.locator('[data-universe-map] .guardian-card').count();
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
    status: response?.status(),
    title,
    h1,
    navCount,
    textLength: bodyText.length,
    universeGateCount,
    universeMapCount,
    guardianCardCount,
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

for (const item of quizCases) {
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
  await page.evaluate(() => localStorage.clear());
  await page.locator('[data-quiz-start]').first().click();

  for (let index = 0; index < 15; index += 1) {
    await page.locator('.quiz-option').first().click();
    await page.locator('.quiz-next').click();
  }

  await page.locator('.quiz-result-card').waitFor({ state: 'visible' });
  await page.waitForFunction(() => {
    const image = document.querySelector('.quiz-result-card img');
    return image && image.complete && image.naturalWidth > 0;
  });
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
    status: response?.status(),
    title: await page.title(),
    h1: await page.locator('h1').first().innerText().catch(() => ''),
    navCount: await page.locator('.nav-links a').count(),
    textLength: (await page.locator('body').innerText()).length,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    resultName,
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
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.locator('[data-quiz-saved]:not([hidden])').waitFor({ state: 'visible' });
    homeSavedVisible = true;
    homeSavedKeepsakeHref = await page.locator('[data-home-saved-keepsake]').first().getAttribute('href').catch(() => '');
    await page.locator('[data-home-saved-plan]').click();
  } else if (item.target === 'keepsake') {
    await page.locator('[data-conversion-keepsake]').click();
  } else {
    await page.locator('[data-conversion-route]').click();
  }
  await page.waitForLoadState('networkidle');
  let keepsakePrimaryHref = '';
  if (item.target === 'keepsake-plan') {
    await page.locator('[data-keepsake-saved]:not([hidden])').waitFor({ state: 'visible' });
    keepsakePrimaryHref = await page.locator('[data-keepsake-saved] .primary-btn').first().getAttribute('href').catch(() => '');
    await page.locator('[data-keepsake-plan]').click();
    await page.waitForLoadState('networkidle');
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
  const horizontalOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  );
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    target: item.target,
    url: `${new URL(page.url()).pathname}${new URL(page.url()).hash}`,
    status: response?.status(),
    title: await page.title(),
    h1: await page.locator('h1').first().innerText().catch(() => ''),
    navCount: await page.locator('.nav-links a').count(),
    textLength: (await page.locator('body').innerText()).length,
    horizontalOverflow,
    consoleErrors,
    pageErrors,
    supplyResumeVisible: await page.locator('[data-supply-saved]:not([hidden])').isVisible().catch(() => false),
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

await browser.close();
console.log(JSON.stringify(results, null, 2));

const failures = [
  ...summarizeFailures(results.filter((result) => !result.name.startsWith('quiz-flow-') && !result.name.startsWith('conversion-'))),
  ...summarizeQuizFailures(results.filter((result) => result.name.startsWith('quiz-flow-'))),
  ...summarizeConversionFailures(results.filter((result) => result.name.startsWith('conversion-'))),
];
if (failures.length) {
  console.error(`Visual check failed:\n${failures.join('\n')}`);
  process.exit(1);
}
