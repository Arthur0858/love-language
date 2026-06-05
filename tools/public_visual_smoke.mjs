import { spawn } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const BASE_URL = process.env.BASE_URL || 'https://lovetypes.tw';
const TIMEOUT_MS = Number(process.env.PUBLIC_VISUAL_TIMEOUT_MS || 600000);

function runVisualCheck() {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, ['tools/visual_check.mjs'], {
      cwd: ROOT,
      env: {
        ...process.env,
        BASE_URL,
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
      stderr += chunk.toString();
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

const { code, stdout, stderr } = await runVisualCheck();
let issues = code === 0 ? 0 : 1;
let results = [];

try {
  results = parseResults(stdout);
} catch (error) {
  issues += 1;
  console.log(`public_visual_parse_error=${JSON.stringify(String(error.message || error))}`);
}

const horizontalOverflowIssues = results.filter((result) => result.horizontalOverflow).length;
const consoleErrorCases = results.filter((result) => Array.isArray(result.consoleErrors) && result.consoleErrors.length).length;
const pageErrorCases = results.filter((result) => Array.isArray(result.pageErrors) && result.pageErrors.length).length;
issues += horizontalOverflowIssues + consoleErrorCases + pageErrorCases;

console.log(`public_visual_cases_checked=${results.length}`);
console.log(`public_visual_screenshots=${results.filter((result) => result.screenshot).length}`);
console.log(`public_visual_quiz_flow_cases=${countByPrefix(results, 'quiz-flow-')}`);
console.log(`public_visual_conversion_cases=${countByPrefix(results, 'conversion-')}`);
console.log(`public_visual_language_menu_cases=${countByPrefix(results, 'language-menu-')}`);
console.log(`public_visual_redirect_cases=${countByPrefix(results, 'redirect-')}`);
console.log(`public_visual_worksheet_cases=${countByPrefix(results, 'worksheet-')}`);
console.log(`public_visual_copy_cases=${countByPrefix(results, 'copy-')}`);
console.log(`public_visual_anchor_focus_cases=${countByPrefix(results, 'anchor-focus-')}`);
console.log(`public_visual_saved_resume_cases=${countByTruthy(results, 'homeSavedVisible') + countByTruthy(results, 'supplyResumeVisible') + countByTruthy(results, 'repairResumeVisible') + countByTruthy(results, 'lunaResumeVisible') + countByTruthy(results, 'guideResumeVisible') + countByTruthy(results, 'keepsakeResumeVisible')}`);
console.log(`public_visual_horizontal_overflow_issues=${horizontalOverflowIssues}`);
console.log(`public_visual_console_error_cases=${consoleErrorCases}`);
console.log(`public_visual_page_error_cases=${pageErrorCases}`);
console.log(`public_visual_issues=${issues}`);

if (issues || code !== 0) {
  if (stderr.trim()) console.log(`public_visual_stderr_tail=${JSON.stringify(tail(stderr))}`);
  if (stdout.trim()) console.log(`public_visual_stdout_tail=${JSON.stringify(tail(stdout))}`);
  process.exit(1);
}
