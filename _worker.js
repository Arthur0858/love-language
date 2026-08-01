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
  "/tools/trust-issues-relationship/"
]);

function normalizedPath(pathname) {
  return pathname.endsWith("/") ? pathname : `${pathname}/`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = normalizedPath(url.pathname);

    if (path === "/tools/love-compatibility/") {
      return Response.redirect(new URL("/compass/", url), 301);
    }

    if (path.startsWith("/tools/") || RETIRED_PATHS.has(path)) {
      return new Response("This LoveTypes page has been retired.", {
        status: 410,
        headers: {
          "Cache-Control": "no-store",
          "Content-Type": "text/plain; charset=utf-8",
          "X-Robots-Tag": "noindex, nofollow",
        },
      });
    }

    return env.ASSETS.fetch(request);
  },
};
