import { mkdir } from 'node:fs/promises';

async function loadPlaywright() {
  try {
    return await import('playwright');
  } catch {
    const fallback = process.env.PLAYWRIGHT_MODULE_PATH ||
      '/Users/mac/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
    return await import(fallback);
  }
}

const { chromium } = await loadPlaywright();

const cases = [
  { name: 'home-desktop', url: 'http://localhost:4173/', viewport: { width: 1440, height: 1000 } },
  { name: 'home-mobile', url: 'http://localhost:4173/', viewport: { width: 390, height: 844 } },
  { name: 'en-guide-desktop', url: 'http://localhost:4173/en/guides/repair-after-conflict/', viewport: { width: 1280, height: 900 } },
  { name: 'ja-guardian-mobile', url: 'http://localhost:4173/ja/characters/iris/', viewport: { width: 390, height: 844 } },
  { name: 'es-guides-desktop', url: 'http://localhost:4173/es/guides/', viewport: { width: 1280, height: 900 } },
];

await mkdir('output/playwright', { recursive: true });
const browser = await chromium.launch({ headless: true });
const results = [];

for (const item of cases) {
  const page = await browser.newPage({ viewport: item.viewport });
  const response = await page.goto(item.url, { waitUntil: 'networkidle' });
  const title = await page.title();
  const h1 = await page.locator('h1').first().innerText();
  const navCount = await page.locator('.nav-links a').count();
  const bodyText = await page.locator('body').innerText();
  const screenshot = `output/playwright/${item.name}.png`;
  await page.screenshot({ path: screenshot, fullPage: false });
  results.push({
    name: item.name,
    status: response?.status(),
    title,
    h1,
    navCount,
    textLength: bodyText.length,
    screenshot,
  });
  await page.close();
}

await browser.close();
console.log(JSON.stringify(results, null, 2));
