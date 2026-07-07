(function () {
  function closest(target, selector) {
    return target && target.closest ? target.closest(selector) : null;
  }

  var funnelAttributeMap = [
    ['data-conversion-route', 'quiz_result_supply_route'],
    ['data-conversion-plan', 'quiz_result_repair_plan'],
    ['data-conversion-luna', 'quiz_result_luna'],
    ['data-conversion-keepsake', 'quiz_result_keepsake'],
    ['data-conversion-contact', 'quiz_result_contact'],
    ['data-conversion-guide', 'quiz_result_guide'],
    ['data-conversion-book', 'quiz_result_affiliate_book'],
    ['data-home-resume-route', 'home_resume_supply_route'],
    ['data-home-resume-plan', 'home_resume_repair_plan'],
    ['data-home-resume-luna', 'home_resume_luna'],
    ['data-home-resume-keepsake', 'home_resume_keepsake'],
    ['data-home-resume-contact', 'home_resume_contact'],
    ['data-home-resume-guardian', 'home_resume_guardian'],
    ['data-garden-map-contact', 'garden_map_resume_contact'],
    ['data-guardian-resume-contact', 'guardian_resume_contact'],
    ['data-guide-resume-contact', 'guide_resume_contact'],
    ['data-supply-resume-contact', 'supply_resume_contact'],
    ['data-keepsake-contact', 'keepsake_resume_contact'],
    ['data-repair-resume-contact', 'repair_resume_contact'],
    ['data-luna-resume-contact', 'luna_resume_contact'],
    ['data-contact-resume-send', 'contact_resume_send'],
    ['data-contact-resume-copy', 'contact_resume_copy'],
    ['data-contact-resume-route', 'contact_resume_supply_route'],
    ['data-contact-resume-luna', 'contact_resume_luna'],
    ['data-contact-resume-keepsake', 'contact_resume_keepsake'],
    ['data-contact-resume-plan', 'contact_resume_repair_plan']
  ];

  function funnelEventName(element) {
    if (!element || !element.hasAttribute) return '';
    var explicit = element.getAttribute('data-funnel-event');
    if (explicit) return explicit;
    for (var index = 0; index < funnelAttributeMap.length; index += 1) {
      if (element.hasAttribute(funnelAttributeMap[index][0])) return funnelAttributeMap[index][1];
    }
    return '';
  }

  function normalizeToken(value) {
    return String(value || '').trim().toLowerCase();
  }

  function funnelCategory(name) {
    return normalizeToken(name).split('_')[0] || 'unknown';
  }

  function guardianFromValue(value) {
    var match = normalizeToken(value).match(/(?:^|[^a-z])(iris|noah|vivian|claire|dora)(?:[^a-z]|$)/);
    return match ? match[1] : '';
  }

  function guardianFromElement(element, target) {
    var guardianNode = closest(element, '[data-guardian-domain], [data-result-guardian], [data-story-slug]');
    var explicit = guardianNode && (
      guardianNode.getAttribute('data-guardian-domain') ||
      guardianNode.getAttribute('data-result-guardian') ||
      guardianNode.getAttribute('data-story-slug')
    );
    return guardianFromValue(explicit) || guardianFromValue(target) || guardianFromValue(window.location.pathname);
  }

  function funnelSource(element) {
    var sourceNode = closest(element, '[data-funnel-source], section, article, nav');
    if (!sourceNode) return '';
    if (sourceNode.getAttribute('data-funnel-source')) return sourceNode.getAttribute('data-funnel-source');
    if (sourceNode.id) return sourceNode.id;
    var className = String(sourceNode.className || '').split(/\s+/).filter(Boolean)[0];
    return className || sourceNode.tagName.toLowerCase();
  }

  function funnelDataValue(element, attribute) {
    var node = closest(element, '[' + attribute + ']');
    return node ? String(node.getAttribute(attribute) || '').slice(0, 160) : '';
  }

  function targetType(target) {
    if (!target) return 'button';
    if (target.indexOf('mailto:') === 0) return 'email';
    if (target.indexOf('#') === 0) return 'anchor';
    try {
      var url = new URL(target, window.location.href);
      if (url.origin !== window.location.origin) return 'external';
      if (url.hash && url.pathname === window.location.pathname) return 'anchor';
      return 'internal';
    } catch (error) {
      return 'unknown';
    }
  }

  function campaignAttributionFromUrl() {
    var params;
    try {
      params = new URLSearchParams(window.location.search || '');
    } catch (error) {
      return null;
    }
    var fields = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
    var attribution = {};
    fields.forEach(function (field) {
      var value = String(params.get(field) || '').trim();
      if (value) attribution[field] = value.slice(0, 120);
    });
    if (!Object.keys(attribution).length) return null;
    attribution.landingPath = window.location.pathname;
    attribution.firstSeenAt = new Date().toISOString();
    return attribution;
  }

  function storedCampaignAttribution() {
    try {
      var attribution = JSON.parse(localStorage.getItem('lovetypes:campaign-attribution:v1') || '{}');
      return attribution && typeof attribution === 'object' ? attribution : {};
    } catch (error) {
      return {};
    }
  }

  function captureCampaignAttribution() {
    var attribution = campaignAttributionFromUrl();
    if (!attribution) return storedCampaignAttribution();
    try {
      var previous = storedCampaignAttribution();
      attribution.firstSeenAt = previous.firstSeenAt || attribution.firstSeenAt;
      attribution.lastSeenAt = new Date().toISOString();
      localStorage.setItem('lovetypes:campaign-attribution:v1', JSON.stringify(attribution));
      return attribution;
    } catch (error) {
      return attribution;
    }
  }

  function recordFunnelPayload(name, target, element) {
    if (!name) return;
    var campaign = storedCampaignAttribution();
    var payload = {
      name: name,
      path: window.location.pathname,
      target: target || '',
      targetType: targetType(target || ''),
      lang: document.documentElement.getAttribute('lang') || '',
      category: funnelCategory(name),
      guardian: guardianFromElement(element, target || ''),
      source: funnelSource(element),
      route: funnelDataValue(element, 'data-funnel-route'),
      intent: funnelDataValue(element, 'data-funnel-intent'),
      campaign: campaign,
      at: new Date().toISOString()
    };
    window.dispatchEvent(new CustomEvent('lovetypes:funnel', { detail: payload }));
    try {
      var key = 'lovetypes:funnel-events:v1';
      var events = JSON.parse(localStorage.getItem(key) || '[]');
      if (!Array.isArray(events)) events = [];
      events.push(payload);
      localStorage.setItem(key, JSON.stringify(events.slice(-40)));
    } catch (error) {}
  }

  function recordFunnelEvent(element) {
    var name = funnelEventName(element);
    if (!name) return;
    recordFunnelPayload(name, element.getAttribute('href') || element.getAttribute('data-result-action') || '', element);
  }

  window.lovetypesRecordFunnelEvent = function (name, target, element) {
    recordFunnelPayload(name, target || '', element || null);
  };

  function hashTarget(hash) {
    if (!hash || hash === '#') return null;
    var id = '';
    try {
      id = decodeURIComponent(hash.slice(1));
    } catch (error) {
      id = hash.slice(1);
    }
    return id ? document.getElementById(id) : null;
  }

  function focusHashTarget(hash) {
    var target = hashTarget(hash);
    if (!target) return false;
    if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
    try {
      target.focus({ preventScroll: true });
    } catch (error) {
      target.focus();
    }
    return true;
  }

  function scrollToHashTarget(hash, behavior) {
    var target = hashTarget(hash);
    if (!target) return false;
    target.scrollIntoView({ behavior: behavior || 'auto', block: 'start' });
    focusHashTarget(hash);
    return true;
  }

  function samePageHash(link) {
    var href = link && link.getAttribute ? link.getAttribute('href') : '';
    if (!href || href === '#') return '';
    var url;
    try {
      url = new URL(href, window.location.href);
    } catch (error) {
      return '';
    }
    if (
      url.origin !== window.location.origin ||
      url.pathname !== window.location.pathname ||
      url.search !== window.location.search ||
      !url.hash
    ) {
      return '';
    }
    return url.hash;
  }

  document.addEventListener('click', function (event) {
    var funnelTarget = closest(event.target, '[data-funnel-event], [data-conversion-route], [data-conversion-plan], [data-conversion-luna], [data-conversion-keepsake], [data-conversion-contact], [data-conversion-guide], [data-conversion-book], [data-home-resume-route], [data-home-resume-plan], [data-home-resume-luna], [data-home-resume-keepsake], [data-home-resume-contact], [data-home-resume-guardian], [data-garden-map-contact], [data-guardian-resume-contact], [data-guide-resume-contact], [data-supply-resume-contact], [data-keepsake-contact], [data-repair-resume-contact], [data-luna-resume-contact], [data-contact-resume-send], [data-contact-resume-copy], [data-contact-resume-route], [data-contact-resume-luna], [data-contact-resume-keepsake], [data-contact-resume-plan]');
    if (funnelTarget) recordFunnelEvent(funnelTarget);

    var menuToggle = closest(event.target, '[data-menu-toggle]');
    if (menuToggle) {
      var menuId = menuToggle.getAttribute('aria-controls') || 'mobile-menu';
      var menu = document.getElementById(menuId);
      if (menu) {
        var isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
        menuToggle.setAttribute('aria-expanded', String(!isOpen));
        menu.hidden = isOpen;
      }
      return;
    }

    var mobileLink = closest(event.target, '.mobile-menu a');
    if (mobileLink) {
      var mobileMenu = mobileLink.closest('.mobile-menu');
      var linkedToggle = mobileMenu && document.querySelector('[aria-controls="' + mobileMenu.id + '"]');
      if (mobileMenu && linkedToggle && linkedToggle.hasAttribute('data-menu-toggle')) {
        linkedToggle.setAttribute('aria-expanded', 'false');
        mobileMenu.hidden = true;
      }
    }

    var startQuizButton = closest(event.target, '[data-start-quiz]');
    if (startQuizButton && typeof window.startQuiz === 'function') {
      window.startQuiz();
      return;
    }

    var faqButton = closest(event.target, '[data-faq-toggle]');
    if (faqButton && typeof window.toggleFaq === 'function') {
      window.toggleFaq(faqButton);
      return;
    }

    var optionButton = closest(event.target, '[data-option-type]');
    if (optionButton && typeof window.selectOption === 'function') {
      window.selectOption(optionButton.getAttribute('data-option-type'), optionButton);
      return;
    }

    var nextButton = closest(event.target, '[data-next-question]');
    if (nextButton && typeof window.nextQuestion === 'function') {
      window.nextQuestion();
      return;
    }

    var resultAction = closest(event.target, '[data-result-action]');
    if (resultAction) {
      var action = resultAction.getAttribute('data-result-action');
      if (action === 'copy' && typeof window.copyResult === 'function') window.copyResult();
      if (action === 'story' && typeof window.downloadStoryCard === 'function') window.downloadStoryCard(resultAction);
      if (action === 'retake' && typeof window.retakeQuiz === 'function') window.retakeQuiz();
      return;
    }

    var cookieAction = closest(event.target, '[data-cookie-action]');
    if (cookieAction) {
      var cookie = cookieAction.getAttribute('data-cookie-action');
      if (cookie === 'accept' && typeof window.acceptCookies === 'function') window.acceptCookies();
      if (cookie === 'decline' && typeof window.declineCookies === 'function') window.declineCookies();
      return;
    }

    var anchorLink = closest(event.target, 'a[href]');
    var hash = anchorLink ? samePageHash(anchorLink) : '';
    var target = hash ? hashTarget(hash) : null;
    if (target) {
      event.preventDefault();
      var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (window.history && window.history.pushState) window.history.pushState(null, '', hash);
      scrollToHashTarget(hash, reduceMotion ? 'auto' : 'smooth');
    }
  });

  document.addEventListener('click', function (event) {
    document.querySelectorAll('.language-menu[open]').forEach(function (menu) {
      if (!menu.contains(event.target)) menu.removeAttribute('open');
    });
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;

    document.querySelectorAll('.language-menu[open]').forEach(function (menu) {
      menu.removeAttribute('open');
      var summary = menu.querySelector('summary');
      if (summary && menu.contains(document.activeElement)) summary.focus();
    });
  });

  window.addEventListener('DOMContentLoaded', function () {
    var landingAttribution = campaignAttributionFromUrl();
    captureCampaignAttribution();
    if (landingAttribution) recordFunnelPayload('campaign_landing', window.location.href, document.documentElement);
    if (!window.location.hash) return;
    window.requestAnimationFrame(function () {
      scrollToHashTarget(window.location.hash, 'auto');
    });
  });
})();

(function () {
  function wrapText(ctx, text, x, y, maxWidth, lineHeight, maxLines) {
    var words = String(text || '').split(/(\s+)/).filter(Boolean);
    var line = '';
    var lines = [];
    words.forEach(function (word) {
      var test = line + word;
      if (ctx.measureText(test).width > maxWidth && line) {
        lines.push(line.trim());
        line = word.trimStart();
      } else {
        line = test;
      }
    });
    if (line.trim()) lines.push(line.trim());
    lines.slice(0, maxLines).forEach(function (item, index) {
      ctx.fillText(index === maxLines - 1 && lines.length > maxLines ? item.replace(/[。.!?…]*$/, '') + '…' : item, x, y + index * lineHeight);
    });
  }

  function loadImage(src) {
    return new Promise(function (resolve, reject) {
      var img = new Image();
      img.onload = function () { resolve(img); };
      img.onerror = reject;
      img.src = src;
    });
  }

  function roundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  window.downloadStoryCard = function (button) {
    var data = window.lovetypesLastResult || {};
    if (button && button.hasAttribute('data-story-name')) {
      data = {
        name: button.getAttribute('data-story-name'),
        title: button.getAttribute('data-story-title'),
        quote: button.getAttribute('data-story-quote'),
        image: button.getAttribute('data-story-image'),
        slug: button.getAttribute('data-story-slug')
      };
    }
    if (!data || !data.image) return;

    var labels = {
      kicker: button.getAttribute('data-story-kicker') || 'Emotion Guardian',
      cta: button.getAttribute('data-story-cta') || 'lovetypes.tw'
    };

    var canvas = document.createElement('canvas');
    canvas.width = 1080;
    canvas.height = 1920;
    var ctx = canvas.getContext('2d');

    var gradient = ctx.createLinearGradient(0, 0, 1080, 1920);
    gradient.addColorStop(0, '#fff8fb');
    gradient.addColorStop(.52, '#f2ebff');
    gradient.addColorStop(1, '#ffe9ee');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 1080, 1920);

    ctx.fillStyle = 'rgba(255,255,255,.72)';
    ctx.beginPath();
    ctx.arc(230, 220, 210, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'rgba(201,102,110,.13)';
    ctx.beginPath();
    ctx.arc(900, 260, 240, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'rgba(159,122,234,.15)';
    ctx.beginPath();
    ctx.arc(190, 1640, 260, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#C9666E';
    ctx.font = '800 34px Arial, sans-serif';
    ctx.letterSpacing = '3px';
    ctx.fillText(labels.kicker.toUpperCase(), 82, 124);

    ctx.letterSpacing = '0px';
    ctx.fillStyle = '#3A2828';
    ctx.font = '700 78px Georgia, "Times New Roman", serif';
    wrapText(ctx, data.name || '', 82, 230, 760, 86, 2);

    ctx.fillStyle = '#7A6060';
    ctx.font = '700 34px Arial, sans-serif';
    wrapText(ctx, data.title || data.tag || '', 84, 410, 780, 44, 2);

    loadImage(data.image).then(function (img) {
      var maxW = 760;
      var maxH = 840;
      var scale = Math.min(maxW / img.width, maxH / img.height);
      var w = img.width * scale;
      var h = img.height * scale;
      ctx.drawImage(img, (1080 - w) / 2, 560 + (maxH - h), w, h);

      ctx.fillStyle = 'rgba(255,255,255,.72)';
      roundedRect(ctx, 72, 1370, 936, 330, 42);
      ctx.fill();
      ctx.strokeStyle = 'rgba(255,255,255,.9)';
      ctx.lineWidth = 3;
      ctx.stroke();

      ctx.fillStyle = '#3A2828';
      ctx.font = '600 44px Arial, sans-serif';
      wrapText(ctx, '“' + (data.quote || '') + '”', 118, 1460, 844, 62, 3);

      ctx.fillStyle = '#C9666E';
      ctx.font = '800 34px Arial, sans-serif';
      ctx.fillText(labels.cta, 118, 1778);

      var link = document.createElement('a');
      link.download = 'lovetypes-' + (data.slug || 'guardian') + '-story.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
    }).catch(function () {
      if (button) button.textContent = button.getAttribute('data-story-error') || 'Image failed';
    });
  };
})();
