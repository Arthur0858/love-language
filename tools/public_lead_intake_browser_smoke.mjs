process.env.BASE_URL = process.env.BASE_URL || 'https://lovetypes.tw';
process.env.METRIC_PREFIX = 'public_lead_intake_browser';

await import('./lead_intake_browser_smoke.mjs');
