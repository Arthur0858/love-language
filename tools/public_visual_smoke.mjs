import { spawn } from 'node:child_process';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const BASE_URL = process.env.BASE_URL || 'https://lovetypes.tw';
const TIMEOUT_MS = Number(process.env.PUBLIC_VISUAL_TIMEOUT_MS || 720000);
const MAX_ATTEMPTS = Number(process.env.PUBLIC_VISUAL_ATTEMPTS || 2);

function runVisualCheck() {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, ['tools/visual_check.mjs'], {
      cwd: ROOT,
      env: {
        ...process.env,
        BASE_URL,
        VISUAL_CHECK_TOTAL_TIMEOUT_MS: process.env.VISUAL_CHECK_TOTAL_TIMEOUT_MS || '660000',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => {
      child.kill('SIGTERM');
      stderr += `\npublic visual smoke timed out after ${TIMEOUT_MS}ms\n`;
    }, TIMEOUT_MS);

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on('data', (chunk) => {
      const text = chunk.toString();
      stderr += text;
      process.stderr.write(text);
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ code, stdout, stderr });
    });
  });
}

function parseResults(stdout) {
  const lines = stdout.split('\n');
  const start = lines.findIndex((line) => line.trim() === '[');
  if (start === -1) {
    throw new Error('visual_check output did not include a JSON result array');
  }
  return JSON.parse(lines.slice(start).join('\n'));
}

function countByPrefix(results, prefix) {
  return results.filter((result) => result.name?.startsWith(prefix)).length;
}

function countByTruthy(results, key) {
  return results.filter((result) => Boolean(result[key])).length;
}

function tail(text, lines = 40) {
  return text.trim().split('\n').slice(-lines).join('\n');
}

let lastRun = { code: 1, stdout: '', stderr: '' };
let results = [];
let parseError = '';
let attempts = 0;

for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
  attempts = attempt;
  lastRun = await runVisualCheck();
  parseError = '';
  try {
    results = parseResults(lastRun.stdout);
  } catch (error) {
    results = [];
    parseError = String(error.message || error);
  }

  if (lastRun.code === 0 && results.length) break;
  if (attempt < MAX_ATTEMPTS) {
    console.error(`[public-visual] attempt ${attempt} produced no usable result; retrying`);
  }
}

let issues = lastRun.code === 0 ? 0 : 1;
if (!results.length) issues += 1;
if (parseError) console.log(`public_visual_parse_error=${JSON.stringify(parseError)}`);

const horizontalOverflowIssues = results.filter((result) => result.horizontalOverflow).length;
const consoleErrorCases = results.filter((result) => Array.isArray(result.consoleErrors) && result.consoleErrors.length).length;
const pageErrorCases = results.filter((result) => Array.isArray(result.pageErrors) && result.pageErrors.length).length;
issues += horizontalOverflowIssues + consoleErrorCases + pageErrorCases;

console.log(`public_visual_attempts=${attempts}`);
console.log(`public_visual_cases_checked=${results.length}`);
console.log(`public_visual_screenshots=${results.filter((result) => result.screenshot).length}`);
console.log(`public_visual_quiz_flow_cases=${countByPrefix(results, 'quiz-flow-')}`);
console.log(`public_visual_conversion_cases=${countByPrefix(results, 'conversion-')}`);
console.log(`public_visual_language_menu_cases=${countByPrefix(results, 'language-menu-')}`);
console.log(`public_visual_redirect_cases=${countByPrefix(results, 'redirect-')}`);
console.log(`public_visual_worksheet_cases=${countByPrefix(results, 'worksheet-')}`);
console.log(`public_visual_copy_cases=${countByPrefix(results, 'copy-')}`);
console.log(`public_visual_anchor_focus_cases=${countByPrefix(results, 'anchor-focus-')}`);
console.log(`public_visual_garden_map_cases=${countByPrefix(results, 'garden-map-')}`);
console.log(`public_visual_saved_resume_cases=${countByTruthy(results, 'homeSavedVisible') + countByTruthy(results, 'gardenMapResumeVisible') + countByTruthy(results, 'supplyResumeVisible') + countByTruthy(results, 'repairResumeVisible') + countByTruthy(results, 'lunaResumeVisible') + countByTruthy(results, 'guideResumeVisible') + countByTruthy(results, 'keepsakeResumeVisible')}`);
console.log(`public_visual_horizontal_overflow_issues=${horizontalOverflowIssues}`);
console.log(`public_visual_console_error_cases=${consoleErrorCases}`);
console.log(`public_visual_page_error_cases=${pageErrorCases}`);
console.log(`public_visual_issues=${issues}`);

if (issues || lastRun.code !== 0) {
  if (lastRun.stderr.trim()) console.log(`public_visual_stderr_tail=${JSON.stringify(tail(lastRun.stderr))}`);
  if (lastRun.stdout.trim()) console.log(`public_visual_stdout_tail=${JSON.stringify(tail(lastRun.stdout))}`);
  process.exit(1);
}
