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
const CASES = [
  { name: 'home-mobile', path: '/', width: 390, height: 844 },
  { name: 'home-desktop', path: '/', width: 1366, height: 900 },
  { name: 'garden-map-mobile', path: '/garden-map/', width: 390, height: 844 },
  { name: 'characters-mobile', path: '/characters/', width: 390, height: 844 },
  { name: 'resources-mobile', path: '/resources/', width: 390, height: 844 },
  { name: 'repair-plan-mobile', path: '/repair-plan/', width: 390, height: 844 },
  { name: 'luna-mobile', path: '/luna-yoga-music/', width: 390, height: 844 },
  { name: 'theory-mobile', path: '/theory/', width: 390, height: 844 },
  { name: 'about-mobile', path: '/about/', width: 390, height: 844 },
];

function makeUrl(path) {
  return new URL(path, BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`).toString();
}

function luminance(rgb) {
  const [r, g, b] = rgb.map((value) => {
    const channel = value / 255;
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
}

function contrastRatio(foreground, background) {
  const light = Math.max(luminance(foreground), luminance(background));
  const dark = Math.min(luminance(foreground), luminance(background));
  return (light + 0.05) / (dark + 0.05);
}

async function inspectCase(browser, item) {
  const context = await browser.newContext({
    viewport: { width: item.width, height: item.height },
    isMobile: item.width <= 720,
    deviceScaleFactor: item.width <= 720 ? 2 : 1,
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(error.message));

  const response = await page.goto(makeUrl(item.path), { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});

  const textNodes = await page.evaluate(() => {
    function parseRgb(value) {
      const match = value.match(/rgba?\(([^)]+)\)/);
      if (!match) return null;
      const parts = match[1].split(',').map((part) => Number.parseFloat(part));
      return {
        rgb: parts.slice(0, 3),
        alpha: parts[3] === undefined ? 1 : parts[3],
      };
    }

    function mix(foreground, background, alpha) {
      return foreground.map((value, index) => Math.round((value * alpha) + (background[index] * (1 - alpha))));
    }

    function visible(node) {
      const style = window.getComputedStyle(node);
      const rect = node.getBoundingClientRect();
      return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
    }

    function imageColor(value) {
      if (!value || value === 'none') return null;
      const match = value.match(/rgba?\(([^)]+)\)/);
      if (!match) return null;
      const parts = match[1].split(',').map((part) => Number.parseFloat(part));
      return {
        rgb: parts.slice(0, 3),
        alpha: parts[3] === undefined ? 1 : parts[3],
      };
    }

    function backgroundFor(node) {
      const chain = [];
      let current = node;
      while (current) {
        chain.push(current);
        current = current.parentElement;
      }

      let background = [255, 248, 242];
      let hasComplexBackground = false;
      chain.reverse().forEach((item) => {
        const style = window.getComputedStyle(item);
        if (style.backgroundImage && style.backgroundImage !== 'none') {
          hasComplexBackground = true;
        }
        const solidColor = parseRgb(style.backgroundColor);
        const color = solidColor && solidColor.alpha > 0 ? solidColor : imageColor(style.backgroundImage);
        if (!color || color.alpha <= 0) return;
        background = color.alpha >= 1 ? color.rgb : mix(color.rgb, background, color.alpha);
      });
      return { background, hasComplexBackground };
    }

    function directText(node) {
      return [...node.childNodes]
        .filter((child) => child.nodeType === Node.TEXT_NODE)
        .map((child) => child.textContent.trim())
        .filter(Boolean)
        .join(' ')
        .replace(/\s+/g, ' ')
        .trim();
    }

    return [...document.querySelectorAll('body *')]
      .filter(visible)
      .map((node) => {
        const text = directText(node);
        if (!text || text.length < 2) return null;
        const style = window.getComputedStyle(node);
        const color = parseRgb(style.color);
        if (!color || color.alpha < 0.85) return null;
        const background = backgroundFor(node);
        return {
          tag: node.tagName.toLowerCase(),
          className: String(node.className || '').slice(0, 80),
          text: text.slice(0, 96),
          color: color.rgb,
          background: background.background,
          hasComplexBackground: background.hasComplexBackground,
          fontSize: Number.parseFloat(style.fontSize),
          fontWeight: Number.parseInt(style.fontWeight, 10) || 400,
        };
      })
      .filter(Boolean);
  });

  await context.close();

  const issues = [];
  if (!response || response.status() >= 400) issues.push(`HTTP status ${response?.status() || 'missing'}`);
  for (const message of consoleErrors) issues.push(`console error: ${message}`);
  for (const message of pageErrors) issues.push(`page error: ${message}`);

  for (const node of textNodes) {
    if (node.hasComplexBackground) continue;
    const ratio = contrastRatio(node.color, node.background);
    const largeText = node.fontSize >= 24 || (node.fontSize >= 18.66 && node.fontWeight >= 700);
    const required = largeText ? 3 : 4.5;
    if (ratio < required) {
      issues.push(`${node.tag}.${node.className} "${node.text}" contrast ${ratio.toFixed(2)} < ${required}`);
    }
  }

  return { name: item.name, textNodesChecked: textNodes.length, issues };
}

async function main() {
  const playwright = await loadPlaywright();
  const browser = await playwright.chromium.launch(await browserLaunchOptions());
  const results = [];
  try {
    for (const item of CASES) {
      console.error(`[contrast] ${item.name}`);
      results.push(await inspectCase(browser, item));
    }
  } finally {
    await browser.close();
  }

  const issues = results.flatMap((result) => result.issues.map((issue) => `${result.name}: ${issue}`));
  const textNodesChecked = results.reduce((sum, result) => sum + result.textNodesChecked, 0);
  console.log(`contrast_pages_checked=${results.length}`);
  console.log(`contrast_text_nodes_checked=${textNodesChecked}`);
  console.log(`contrast_issues=${issues.length}`);
  for (const issue of issues.slice(0, 100)) console.log(issue);
  if (issues.length > 100) console.log(`... ${issues.length - 100} more issue(s)`);
  process.exitCode = issues.length ? 1 : 0;
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
