(function () {
  var current = document.currentScript;
  var shouldLoadAffiliate = current && current.hasAttribute('data-affiliate');
  var affiliateSrc = 'https://cdn.affiliates.one/production/adlinks/9debdd711c52d9dc844e3f5a6669fe912d4a1908c6a6f579e4ad35a346ddc87a.js';

  function loadScript(src, options) {
    if (document.querySelector('script[src="' + src + '"]')) return;
    var script = document.createElement('script');
    script.src = src;
    script.async = true;
    if (options && options.defer) script.defer = true;
    if (options && options.crossOrigin) script.crossOrigin = options.crossOrigin;
    script.onerror = function () {
      document.documentElement.setAttribute('data-external-script-error', 'true');
    };
    document.head.appendChild(script);
  }

  function loadExternalScripts() {
    if (shouldLoadAffiliate) {
      if (document.querySelector('a[rel~="sponsored"]')) return;
      window.ConverlyCustomData = window.ConverlyCustomData || { channelId: null };
      loadScript(affiliateSrc, { defer: true });
    }
  }

  var loaded = false;
  function scheduleLoad() {
    if (loaded) return;
    loaded = true;
    loadExternalScripts();
  }

  function schedule() {
    ['pointerdown', 'keydown', 'scroll'].forEach(function (eventName) {
      window.addEventListener(eventName, scheduleLoad, { once: true, passive: true });
    });
    window.setTimeout(scheduleLoad, 10000);
  }

  if (document.readyState === 'complete') {
    schedule();
  } else {
    window.addEventListener('load', schedule, { once: true });
  }
})();
