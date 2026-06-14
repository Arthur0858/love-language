import { createServer } from 'node:http';
import { access, readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CASES = [
  '/contact/',
  '/keepsakes/',
  '/en/contact/',
  '/en/keepsakes/',
  '/ja/contact/',
  '/ja/keepsakes/',
  '/ko/contact/',
  '/ko/keepsakes/',
  '/es/contact/',
  '/es/keepsakes/',
];

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

function contentType(filePath) {
  if (filePath.endsWith('.html')) return 'text/html; charset=utf-8';
  if (filePath.endsWith('.css')) return 'text/css; charset=utf-8';
  if (filePath.endsWith('.js')) return 'text/javascript; charset=utf-8';
  if (filePath.endsWith('.json')) return 'application/json; charset=utf-8';
  if (filePath.endsWith('.webp')) return 'image/webp';
  if (filePath.endsWith('.png')) return 'image/png';
  if (filePath.endsWith('.svg')) return 'image/svg+xml';
  if (filePath.endsWith('.xml')) return 'application/xml; charset=utf-8';
  return 'application/octet-stream';
}

async function resolveFile(urlPath) {
  const decoded = decodeURIComponent(urlPath.split('?')[0] || '/');
  const safePath = path.normalize(decoded).replace(/^(\.\.[/\\])+/, '');
  let filePath = path.join(ROOT, safePath);
  if (!filePath.startsWith(ROOT)) return null;
  try {
    const info = await stat(filePath);
    if (info.isDirectory()) filePath = path.join(filePath, 'index.html');
  } catch {
    if (safePath.endsWith('/')) filePath = path.join(ROOT, safePath, 'index.html');
  }
  try {
    const info = await stat(filePath);
    return info.isFile() ? filePath : null;
  } catch {
    return null;
  }
}

async function startServer() {
  const server = createServer(async (request, response) => {
    const filePath = await resolveFile(request.url || '/');
    if (!filePath) {
      response.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' });
      response.end('Not found');
      return;
    }
    response.writeHead(200, { 'content-type': contentType(filePath) });
    response.end(await readFile(filePath));
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  const port = typeof address === 'object' && address ? address.port : 0;
  return {
    baseUrl: `http://127.0.0.1:${port}`,
    close: () => new Promise((resolve) => server.close(resolve)),
  };
}

function pageUrl(baseUrl, urlPath) {
  return new URL(urlPath, baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`).toString();
}

async function checkCase(browser, baseUrl, urlPath) {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();
  const issues = [];
  page.on('console', (message) => {
    if (message.type() === 'error') issues.push(`console error: ${message.text()}`);
  });
  page.on('pageerror', (error) => issues.push(`page error: ${error.message}`));

  const response = await page.goto(pageUrl(baseUrl, urlPath), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);

  const form = page.locator('[data-lead-intake-form]').first();
  await form.waitFor({ state: 'visible', timeout: 10000 }).catch(() => issues.push('lead intake form missing'));
  if (issues.length) {
    await context.close();
    return { urlPath, invalidRejected: false, validAccepted: false, issues };
  }

  const placeholder = await form.locator('[name="reply_email"]').getAttribute('placeholder');
  if (placeholder === 'name@example.com' || !placeholder) issues.push(`unsafe email placeholder ${placeholder || '<empty>'}`);

  await form.locator('[name="reply_email"]').fill('name@example.com');
  await form.locator('[name="consent"]').check();
  await form.locator('[data-lead-intake-copy]').click();
  const invalidHidden = await form.locator('[data-lead-intake-error]').getAttribute('hidden');
  const invalidText = (await form.locator('[data-lead-intake-error]').textContent() || '').trim();
  const invalidRejected = invalidHidden === null && /example|test|placeholder|真實|実際|실제|real/i.test(invalidText);
  if (!invalidRejected) issues.push('reserved example email was not visibly rejected');

  await form.locator('[name="reply_email"]').fill('traveler@realmail.com');
  await form.locator('[data-lead-intake-copy]').click();
  const validHidden = await form.locator('[data-lead-intake-error]').getAttribute('hidden');
  const preview = await form.locator('[data-lead-intake-preview]').inputValue();
  const validAccepted = validHidden !== null && preview.includes('traveler@realmail.com') && preview.includes('consent_status: explicit_reply_ok');
  if (!validAccepted) issues.push('real-format email did not produce a valid structured request preview');

  await context.close();
  return { urlPath, invalidRejected, validAccepted, issues };
}

let ownedServer = null;
const baseUrl = process.env.BASE_URL || '';
try {
  const serverState = baseUrl ? { baseUrl, close: async () => {} } : await startServer();
  ownedServer = serverState;
  const playwright = await loadPlaywright();
  const browser = await playwright.chromium.launch(await browserLaunchOptions());
  const results = [];
  for (const urlPath of CASES) {
    results.push(await checkCase(browser, serverState.baseUrl, urlPath));
  }
  await browser.close();

  const invalidRejected = results.filter((result) => result.invalidRejected).length;
  const validAccepted = results.filter((result) => result.validAccepted).length;
  const issues = results.flatMap((result) => result.issues.map((issue) => `${result.urlPath}: ${issue}`));
  console.log(`lead_intake_browser_pages_checked=${results.length}`);
  console.log(`lead_intake_browser_invalid_email_rejected=${invalidRejected}`);
  console.log(`lead_intake_browser_valid_email_accepted=${validAccepted}`);
  console.log(`lead_intake_browser_issues=${issues.length}`);
  for (const issue of issues) console.log(issue);
  if (issues.length) process.exitCode = 1;
} finally {
  if (ownedServer) await ownedServer.close();
}
