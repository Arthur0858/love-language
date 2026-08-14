const RETIRED_PATHS = new Set([
  "/guides/before-sharing-result/",
  "/guides/claire-acts-of-service/",
  "/guides/conflict-repair-worksheet/",
  "/guides/dialogue-scripts/",
  "/guides/dora-physical-touch/",
  "/guides/guardian-pairings/",
  "/guides/heart-garden/",
  "/guides/iris-words-of-affirmation/",
  "/guides/love-language-examples/",
  "/guides/misfrequency/",
  "/guides/noah-quality-time/",
  "/guides/relationship-review-questions/",
  "/guides/use-your-result/",
  "/guides/vivian-receiving-gifts/",
  "/tools/2026-love-timing/",
  "/tools/bazi-love-compatibility/",
  "/tools/breakup-signs-relationship/",
  "/tools/couples-communication-quiz/",
  "/tools/emotional-distance-relationship/",
  "/tools/feeling-misunderstood-relationship/",
  "/tools/insecure-in-relationship/",
  "/tools/lonely-in-relationship/",
  "/tools/long-distance-fight-repair/",
  "/tools/love-language-compatibility/",
  "/tools/one-sided-relationship/",
  "/tools/partner-doesnt-listen/",
  "/tools/partner-needs-space-relationship/",
  "/tools/partner-wont-communicate/",
  "/tools/relationship-compatibility-test/",
  "/tools/relationship-repair-after-fight/",
  "/tools/silent-treatment-relationship/",
  "/tools/taken-for-granted-relationship/",
  "/tools/trust-issues-relationship/",
  "/luna/",
  "/go/luna-starter-click/"
]);
const RETIRED_ASSETS = new Set([
  "/compass-data-en.js",
  "/compass-data-es.js",
  "/compass-data-ja.js",
  "/compass-data-ko.js",
  "/compass-tool-20260707.js",
  "/compass-tool-review-20260801.js",
  "/compass-tool.js",
  "/deferred-external-20260613-funnel-kpi-map.js",
  "/funnel-events.json",
  "/quiz-data-en-20260707-conversion-bridge.js",
  "/quiz-data-en-20260801-core.js",
  "/quiz-data-en-20260801-review-surface.js",
  "/quiz-data-es-20260707-conversion-bridge.js",
  "/quiz-data-es-20260801-core.js",
  "/quiz-data-es-20260801-review-surface.js",
  "/quiz-data-ja-20260707-conversion-bridge.js",
  "/quiz-data-ja-20260801-core.js",
  "/quiz-data-ja-20260801-review-surface.js",
  "/quiz-data-ko-20260707-conversion-bridge.js",
  "/quiz-data-ko-20260801-core.js",
  "/quiz-data-ko-20260801-review-surface.js",
  "/quiz-data-zh-20260707-conversion-bridge.js",
  "/quiz-data-zh-20260801-review-surface.js",
  "/shared-20260613-funnel-kpi-map.css",
  "/site-interactions-20260718-quiz-metrics.js"
]);

function normalizedPath(pathname) {
  return pathname.endsWith("/") ? pathname : `${pathname}/`;
}

function retiredResponse(message) {
  return new Response(message, {
    status: 410,
    headers: {
      "Cache-Control": "no-store",
      "Content-Type": "text/plain; charset=utf-8",
      "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
      "Referrer-Policy": "strict-origin-when-cross-origin",
      "Strict-Transport-Security": "max-age=31536000",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "SAMEORIGIN",
      "X-Robots-Tag": "noindex, nofollow",
    },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (RETIRED_ASSETS.has(url.pathname)) {
      return retiredResponse("This LoveTypes asset has been retired.");
    }
    const path = normalizedPath(url.pathname);

    if (path === "/tools/love-compatibility/") {
      return Response.redirect(new URL("/compass/", url), 301);
    }

    if (path.startsWith("/tools/") || RETIRED_PATHS.has(path)) {
      return retiredResponse("This LoveTypes page has been retired.");
    }

    return env.ASSETS.fetch(request);
  },
};
