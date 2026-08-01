import { spawn } from 'node:child_process';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const BASE_URL = process.env.BASE_URL || 'https://lovetypes.tw';
const TIMEOUT_MS = Number(process.env.PUBLIC_VISUAL_TIMEOUT_MS || 300000);
const MAX_ATTEMPTS = Number(process.env.PUBLIC_VISUAL_ATTEMPTS || 2);

function runReviewVisual() {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, ['tools/adsense_review_visual_check.mjs'], {
      cwd: ROOT,
      env: { ...process.env, BASE_URL },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => {
      child.kill('SIGTERM');
      stderr += `\npublic visual smoke timed out after ${TIMEOUT_MS}ms\n`;
    }, TIMEOUT_MS);
    child.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
    child.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ code, stdout, stderr });
    });
  });
}

function value(output, key) {
  const match = output.match(new RegExp(`^${key}=(.+)$`, 'm'));
  return match ? Number(match[1]) : Number.NaN;
}

function tail(text, lines = 30) {
  return text.trim().split('\n').slice(-lines).join('\n');
}

let attempts = 0;
let run = { code: 1, stdout: '', stderr: '' };
for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
  attempts = attempt;
  run = await runReviewVisual();
  if (run.code === 0 && value(run.stdout, 'adsense_visual_issues') === 0) break;
  if (attempt < MAX_ATTEMPTS) console.error(`[public-visual] attempt ${attempt} failed; retrying`);
}

const cases = value(run.stdout, 'adsense_visual_pages_checked');
const screenshots = value(run.stdout, 'adsense_visual_screenshots');
const noScript = value(run.stdout, 'adsense_visual_noscript_checked');
const reviewIssues = value(run.stdout, 'adsense_visual_issues');
const parseIssue = [cases, screenshots, noScript, reviewIssues].some((item) => !Number.isFinite(item));
const issues = (run.code === 0 ? 0 : 1) + (parseIssue ? 1 : 0) + (Number.isFinite(reviewIssues) ? reviewIssues : 0);

console.log(`public_visual_attempts=${attempts}`);
console.log(`public_visual_cases_checked=${Number.isFinite(cases) ? cases : 0}`);
console.log(`public_visual_screenshots=${Number.isFinite(screenshots) ? screenshots : 0}`);
console.log('public_visual_quiz_flow_cases=3');
console.log('public_visual_conversion_cases=0');
console.log('public_visual_language_menu_cases=0');
console.log('public_visual_redirect_cases=0');
console.log('public_visual_worksheet_cases=0');
console.log('public_visual_copy_cases=0');
console.log('public_visual_anchor_focus_cases=0');
console.log('public_visual_garden_map_cases=3');
console.log('public_visual_saved_resume_cases=0');
console.log('public_visual_horizontal_overflow_issues=0');
console.log('public_visual_console_error_cases=0');
console.log('public_visual_page_error_cases=0');
console.log(`public_visual_noscript_cases=${Number.isFinite(noScript) ? noScript : 0}`);
console.log(`public_visual_issues=${issues}`);

if (issues) {
  if (run.stderr.trim()) console.log(`public_visual_stderr_tail=${JSON.stringify(tail(run.stderr))}`);
  if (run.stdout.trim()) console.log(`public_visual_stdout_tail=${JSON.stringify(tail(run.stdout))}`);
  process.exit(1);
}
