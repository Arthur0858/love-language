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
  { name: 'guides', path: '/guides/' },
  { name: 'guide-share-result', path: '/guides/share-your-result/' },
  { name: 'guide-conflict-repair', path: '/guides/repair-after-conflict/' },
  { name: 'guide-touch-consent', path: '/guides/physical-touch-consent-safety/' },
  { name: 'lab', path: '/lab/' },
  { name: 'lab-scoring', path: '/lab/quiz-scoring-test/' },
  { name: 'lab-accessibility', path: '/lab/keyboard-accessibility-test/' },
  { name: 'compatibility', path: '/tools/love-compatibility/' },
  { name: 'about', path: '/about/' },
  { name: 'resources', path: '/resources/' },
];
const noScriptRoutes = [
  '/guides/share-your-result/',
  '/guides/repair-after-conflict/',
  '/lab/quiz-scoring-test/',
  '/about/',
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
      await page.waitForTimeout(100);
      const state = await page.evaluate(() => ({
        title: document.title.trim(),
        h1: document.querySelector('h1')?.textContent?.trim() || '',
        mainText: document.querySelector('main')?.innerText?.trim().length || 0,
        horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        brokenImages: [...document.images]
          .filter((image) => image.getBoundingClientRect().width > 0 && image.complete && image.naturalWidth === 0)
          .map((image) => image.currentSrc || image.src),
      }));
      if (!state.title) issues.push(`${route.name}-${viewport.name}: missing title`);
      if (!state.h1) issues.push(`${route.name}-${viewport.name}: missing H1`);
      if (state.mainText < 250) issues.push(`${route.name}-${viewport.name}: main text too short (${state.mainText})`);
      if (state.horizontalOverflow) issues.push(`${route.name}-${viewport.name}: horizontal overflow`);
      if (state.brokenImages.length) issues.push(`${route.name}-${viewport.name}: broken images ${state.brokenImages.join(', ')}`);
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
