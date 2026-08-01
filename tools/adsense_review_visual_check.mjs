import { mkdir } from 'node:fs/promises';


async function loadPlaywright() {
  const candidates = [
    'playwright',
    process.env.PLAYWRIGHT_MODULE_PATH,
    '/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs',
  ].filter(Boolean);
  let lastError;
  for (const candidate of candidates) {
    try {
      const module = await import(candidate);
      return module.chromium ? module : module.default;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}


const base = (process.env.BASE_URL || 'http://127.0.0.1:4173').replace(/\/$/, '');
const output = 'output/playwright/adsense-review';
const viewports = [
  { name: 'mobile', width: 360, height: 800 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
];
const routes = [
  { name: 'home', path: '/' },
  { name: 'quiz', path: '/', quiz: true },
  { name: 'start', path: '/start/' },
  { name: 'garden-map', path: '/garden-map/' },
  { name: 'characters-index', path: '/characters/' },
  { name: 'guardian-iris', path: '/characters/iris/' },
  { name: 'guardian-noah', path: '/characters/noah/' },
  { name: 'guardian-vivian', path: '/characters/vivian/' },
  { name: 'guardian-claire', path: '/characters/claire/' },
  { name: 'guardian-dora', path: '/characters/dora/' },
  { name: 'guides', path: '/guides/' },
  { name: 'guide-share-result', path: '/guides/share-your-result/' },
  { name: 'guide-conflict-repair', path: '/guides/repair-after-conflict/' },
  { name: 'guide-touch-consent', path: '/guides/physical-touch-consent-safety/' },
  { name: 'lab', path: '/lab/' },
  { name: 'lab-scoring', path: '/lab/quiz-scoring-test/' },
  { name: 'lab-accessibility', path: '/lab/keyboard-accessibility-test/' },
  { name: 'compass', path: '/compass/', compass: true },
  { name: 'repair-plan', path: '/repair-plan/' },
  { name: 'about', path: '/about/' },
  { name: 'theory', path: '/theory/' },
  { name: 'contact', path: '/contact/' },
  { name: 'privacy', path: '/privacy/' },
  { name: 'terms', path: '/terms/' },
  { name: 'resources', path: '/resources/' },
];
const noScriptRoutes = [
  '/guides/share-your-result/',
  '/guides/repair-after-conflict/',
  '/lab/quiz-scoring-test/',
  '/about/',
  '/privacy/',
];


await mkdir(output, { recursive: true });
const { chromium } = await loadPlaywright();
const browser = await chromium.launch({ headless: true });
const issues = [];
let pagesChecked = 0;
let screenshots = 0;
let noScriptChecked = 0;

async function finishQuiz(page) {
  await page.locator('[data-quiz-start]').first().click();
  for (let index = 0; index < 15; index += 1) {
    await page.locator('.quiz-option').nth(index % 5).click();
    await page.locator('.quiz-next').click();
  }
  await page.locator('[data-quiz-result]').scrollIntoViewIfNeeded();
  if (!await page.locator('[data-quiz-result]').isVisible()) {
    throw new Error('quiz result did not become visible');
  }
}

for (const viewport of viewports) {
  for (const route of routes) {
    const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });
    const consoleErrors = [];
    const pageErrors = [];
    page.on('console', (message) => {
      const location = message.location()?.url || '';
      const localQuizPixel = location.includes('/go/quiz-started.gif') || location.includes('/go/quiz-completed.gif');
      if (message.type() === 'error' && !localQuizPixel) consoleErrors.push(`${message.text()} @ ${location}`);
    });
    page.on('pageerror', (error) => pageErrors.push(error.message));
    try {
      const response = await page.goto(`${base}${route.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      if (!response || response.status() >= 400) issues.push(`${route.name}-${viewport.name}: HTTP ${response?.status() || 'none'}`);
      if (route.quiz) await finishQuiz(page);
      if (route.compass) {
        await page.locator('[data-compass-form]').waitFor({ state: 'visible', timeout: 10000 });
        await page.locator('[name="self"]').selectOption('W');
        await page.locator('[name="partner"]').selectOption('T');
        await page.locator('[name="status"]').selectOption('dating');
        await page.locator('[name="issue"]').selectOption('feeling-unheard');
        await page.locator('[data-compass-form] button[type="submit"]').click();
        await page.locator('[data-compass-result]').waitFor({ state: 'visible', timeout: 10000 });
      }
      await page.waitForTimeout(100);
      const state = await page.evaluate((flags) => ({
        title: document.title.trim(),
        h1: document.querySelector('h1')?.textContent?.trim() || '',
        mainText: document.querySelector('main')?.innerText?.trim().length || 0,
        horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        brokenImages: [...document.images]
          .filter((image) => image.getBoundingClientRect().width > 0 && image.complete && image.naturalWidth === 0)
          .map((image) => image.currentSrc || image.src),
        quizResultText: flags.isQuiz ? document.querySelector('[data-quiz-result]')?.innerText || '' : '',
        quizResultHrefs: flags.isQuiz
          ? [...document.querySelectorAll('[data-quiz-result] a[href]')].map((anchor) => anchor.getAttribute('href') || '')
          : [],
        compassResultText: flags.isCompass ? document.querySelector('[data-compass-result]')?.innerText || '' : '',
        compassResultHrefs: flags.isCompass
          ? [...document.querySelectorAll('[data-compass-result] a[href]')].map((anchor) => anchor.getAttribute('href') || '')
          : [],
        compassDateInputs: flags.isCompass ? document.querySelectorAll('[data-compass-root] input[type="date"]').length : 0,
      }), { isQuiz: Boolean(route.quiz), isCompass: Boolean(route.compass) });
      if (!state.title) issues.push(`${route.name}-${viewport.name}: missing title`);
      if (!state.h1) issues.push(`${route.name}-${viewport.name}: missing H1`);
      if (state.mainText < 250) issues.push(`${route.name}-${viewport.name}: main text too short (${state.mainText})`);
      if (state.horizontalOverflow) issues.push(`${route.name}-${viewport.name}: horizontal overflow`);
      if (state.brokenImages.length) issues.push(`${route.name}-${viewport.name}: broken images ${state.brokenImages.join(', ')}`);
      if (route.quiz) {
        const salesPhrases = ['需要安靜時再買', 'Starter Pack', 'Luna', '博客來', 'Amazon', 'Gumroad', '聯盟行銷', '付費報告'];
        const leakedPhrase = salesPhrases.find((phrase) => state.quizResultText.includes(phrase));
        if (leakedPhrase) issues.push(`${route.name}-${viewport.name}: rendered result exposes sales phrase ${leakedPhrase}`);
        const noindexPaths = ['/resources/', '/luna-yoga-music/', '/keepsakes/', '/go/luna'];
        const leakedHref = state.quizResultHrefs.find((href) => noindexPaths.some((path) => href.includes(path)));
        if (leakedHref) issues.push(`${route.name}-${viewport.name}: rendered result links to noindex route ${leakedHref}`);
      }
      if (route.compass) {
        const forbiddenCompassPhrases = ['付費', '購買', '價格', '報告需求', '八字', '流年', 'Gumroad', '出生日期'];
        const leakedPhrase = forbiddenCompassPhrases.find((phrase) => state.compassResultText.includes(phrase));
        if (leakedPhrase) issues.push(`${route.name}-${viewport.name}: rendered compass exposes forbidden phrase ${leakedPhrase}`);
        const noindexPaths = ['/resources/', '/luna-yoga-music/', '/keepsakes/', '/go/luna'];
        const leakedHref = state.compassResultHrefs.find((href) => noindexPaths.some((path) => href.includes(path)));
        if (leakedHref) issues.push(`${route.name}-${viewport.name}: rendered compass links to noindex route ${leakedHref}`);
        if (state.compassDateInputs) issues.push(`${route.name}-${viewport.name}: compass still requests birth dates`);
      }
      if (consoleErrors.length) issues.push(`${route.name}-${viewport.name}: console errors ${consoleErrors.join(' | ')}`);
      if (pageErrors.length) issues.push(`${route.name}-${viewport.name}: page errors ${pageErrors.join(' | ')}`);
      await page.screenshot({ path: `${output}/${route.name}-${viewport.name}.png`, fullPage: false });
      screenshots += 1;
      pagesChecked += 1;
    } catch (error) {
      issues.push(`${route.name}-${viewport.name}: ${error.message}`);
    } finally {
      await page.close();
    }
  }
}

for (const path of noScriptRoutes) {
  const page = await browser.newPage({ viewport: { width: 360, height: 800 }, javaScriptEnabled: false });
  try {
    const response = await page.goto(`${base}${path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    const content = await page.locator('main').innerText().catch(() => '');
    const h1 = await page.locator('h1').first().innerText().catch(() => '');
    if (!response || response.status() >= 400 || !h1 || content.length < 500) {
      issues.push(`noscript ${path}: article or trust content is not readable`);
    }
    noScriptChecked += 1;
  } finally {
    await page.close();
  }
}

await browser.close();
console.log(`adsense_visual_pages_checked=${pagesChecked}`);
console.log(`adsense_visual_screenshots=${screenshots}`);
console.log(`adsense_visual_noscript_checked=${noScriptChecked}`);
console.log(`adsense_visual_issues=${issues.length}`);
for (const issue of issues) console.error(`- ${issue}`);
if (issues.length) process.exit(1);
