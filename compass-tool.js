(function () {
  var data = window.__COMPASS_DATA;
  if (!data) return;

  var root = document.querySelector('[data-compass-root]');
  if (!root) return;

  // Detect current language from <html lang>
  var lang = (document.documentElement.getAttribute('lang') || 'en').split('-')[0];

  var labels = {
    en: {
      title: 'LoveTypes Relationship Compass',
      subtitle: 'See where your love languages cross signals — and find one place to start today, for free.',
      selfLabel: 'My LoveTypes guardian',
      partnerLabel: 'Their LoveTypes guardian',
      dobLabel: 'Birthdates (optional)',
      dobSelf: 'My birthday',
      dobPartner: 'Their birthday',
      dobHint: 'MM/DD/YYYY — optional, helps with timing insights',
      statusLabel: 'Current status',
      issueLabel: 'Top thing I want to improve',
      submit: 'Get My Compass',
      loading: 'Reading your two languages...',
      resultTitle: 'Your Compass Reading',
      misfrequencyTitle: 'Your main cross-signal',
      misunderstoodTitle: 'What needs the most understanding',
      sentenceTitle: 'One sentence you can say',
      actionTitle: 'One small action in 24 hours',
      paidTitle: 'Want the full map?',
      paidIntro: 'The free compass shows you the first step. These reports give you the whole path — scripts, schedules, and a deeper understanding of your unique pairing.',
      pdfTitle: 'Add PDF Collectible Edition',
      pdfNote: 'Beautifully designed, printable, keeps forever.',
      buy: 'Get for ',
      whatInside: 'What\'s inside',
      reportLabels: {
        'emotional-pattern': 'Your Emotional Love Pattern',
        'compatibility': 'LoveTypes Compatibility Report',
        'bazi': 'BaZi Love Compatibility',
        'timing-2026': '2026 Love Timing',
        'repair-plan': '7-Day Repair Plan'
      },
      reportBuyLinks: {
        'emotional-pattern': 'https://lovetypes.gumroad.com/l/emotional-pattern?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'compatibility': 'https://lovetypes.gumroad.com/l/compatibility-report?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'bazi': 'https://lovetypes.gumroad.com/l/bazi-compatibility?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'timing-2026': 'https://lovetypes.gumroad.com/l/2026-timing?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'repair-plan': 'https://lovetypes.gumroad.com/l/repair-plan?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'pdf-upgrade': 'https://lovetypes.gumroad.com/l/pdf-upgrade?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free'
      },
      resultFooter: 'This compass is a starting reflection, not a verdict. Your love may not be absent — it may just arrive in different languages. The map is a reminder, not a judgment.',
      recalc: 'Try again with different inputs'
    },
    zh: {
      title: 'LoveTypes 關係羅盤',
      subtitle: '看見你們的愛在哪裡錯頻，找到一個今天就能開始的地方，免費。',
      selfLabel: '我的 LoveTypes 守護者',
      partnerLabel: '對方的 LoveTypes 守護者',
      dobLabel: '出生日期（選填）',
      dobSelf: '我的生日',
      dobPartner: '對方的生日',
      dobHint: '月／日／年 — 選填，幫助提供節奏洞察',
      statusLabel: '目前關係狀態',
      issueLabel: '我最想改善的地方',
      submit: '取得我的羅盤',
      loading: '正在讀取你們的兩種語言……',
      resultTitle: '你的羅盤解讀',
      misfrequencyTitle: '你們的主要錯頻',
      misunderstoodTitle: '最需要被理解的地方',
      sentenceTitle: '一句可以對對方說的話',
      actionTitle: '一個 24 小時內可做的小行動',
      paidTitle: '想要完整地圖嗎？',
      paidIntro: '免費羅盤讓你看見第一步。這幾份報告帶你走完整條路——對話示範、時間規畫，以及針對你們獨特配對的深度拆解。',
      pdfTitle: '加購 PDF 收藏版',
      pdfNote: '精美設計，可列印，永久保存。',
      buy: '購買 ',
      whatInside: '內容包含',
      reportLabels: {
        'emotional-pattern': '你的情感模式報告',
        'compatibility': 'LoveTypes 關係合盤報告',
        'bazi': '八字愛情合盤報告',
        'timing-2026': '2026 流年感情節奏報告',
        'repair-plan': '七日關係修復計畫'
      },
      reportBuyLinks: {
        'emotional-pattern': 'https://lovetypes.gumroad.com/l/emotional-pattern?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'compatibility': 'https://lovetypes.gumroad.com/l/compatibility-report?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'bazi': 'https://lovetypes.gumroad.com/l/bazi-compatibility?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'timing-2026': 'https://lovetypes.gumroad.com/l/2026-timing?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'repair-plan': 'https://lovetypes.gumroad.com/l/repair-plan?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free',
        'pdf-upgrade': 'https://lovetypes.gumroad.com/l/pdf-upgrade?utm_source=lovetypes&utm_medium=compass&utm_campaign=compass_free'
      },
      resultFooter: '這個羅盤是一份反思起點，不是判決。你們的關係可能不是沒有愛，而是愛抵達的方式不同。命盤不是判決，而是一張提醒你如何相處的地圖。',
      recalc: '重新輸入，再測一次'
    }
  };

  var l = labels[lang] || labels.en;

  // ---- Build form HTML ----
  var guardianOptions = Object.entries(data.guardians).map(function (e) {
    var g = e[1];
    var key = e[0];
    return '<option value="' + key + '">' + g.name + ' · ' + g.type + '</option>';
  }).join('');

  var statusOptions = data.statusOptions.map(function (s) {
    return '<option value="' + s.id + '">' + s.label + '</option>';
  }).join('');

  var issueOptions = data.issueOptions.map(function (s) {
    return '<option value="' + s.id + '">' + s.label + '</option>';
  }).join('');

  root.insertAdjacentHTML('beforeend', [
    '<section class="compass-hero">',
      '<p class="eyebrow">RELATIONSHIP COMPASS</p>',
      '<h1>' + l.title + '</h1>',
      '<p class="lead">' + l.subtitle + '</p>',
    '</section>',

    '<section class="compass-form-section" data-compass-form-section>',
      '<form class="compass-form" data-compass-form>',
        '<div class="compass-form-row">',
          '<div class="compass-form-field">',
            '<label for="compass-self">' + l.selfLabel + '</label>',
            '<select id="compass-self" name="self" required>',
              '<option value="">—</option>',
              guardianOptions,
            '</select>',
          '</div>',
          '<div class="compass-form-field">',
            '<label for="compass-partner">' + l.partnerLabel + '</label>',
            '<select id="compass-partner" name="partner" required>',
              '<option value="">—</option>',
              guardianOptions,
            '</select>',
          '</div>',
        '</div>',

        '<div class="compass-form-row compass-dob-row">',
          '<div class="compass-form-field">',
            '<label for="compass-dob-self">' + l.dobSelf + '</label>',
            '<input type="date" id="compass-dob-self" name="dobSelf" placeholder="YYYY-MM-DD">',
          '</div>',
          '<div class="compass-form-field">',
            '<label for="compass-dob-partner">' + l.dobPartner + '</label>',
            '<input type="date" id="compass-dob-partner" name="dobPartner" placeholder="YYYY-MM-DD">',
          '</div>',
        '</div>',
        '<p class="compass-dob-hint">' + l.dobHint + '</p>',

        '<div class="compass-form-row">',
          '<div class="compass-form-field">',
            '<label for="compass-status">' + l.statusLabel + '</label>',
            '<select id="compass-status" name="status">',
              '<option value="">—</option>',
              statusOptions,
            '</select>',
          '</div>',
          '<div class="compass-form-field">',
            '<label for="compass-issue">' + l.issueLabel + '</label>',
            '<select id="compass-issue" name="issue">',
              '<option value="">—</option>',
              issueOptions,
            '</select>',
          '</div>',
        '</div>',

        '<button type="submit" class="primary-btn compass-submit">' + l.submit + '</button>',
      '</form>',
    '</section>',

    '<section class="compass-result" data-compass-result hidden aria-live="polite"></section>',

    '<section class="compass-paid" data-compass-paid hidden aria-live="polite"></section>'
  ].join(''));

  // ---- Event handlers ----

  var form = root.querySelector('[data-compass-form]');
  var resultBox = root.querySelector('[data-compass-result]');
  var paidBox = root.querySelector('[data-compass-paid]');

  function show(el) { el.hidden = false; }
  function hide(el) { el.hidden = true; }

  function renderResult(pairKey, selfG, partnerG) {
    var pairData = data.pairings[pairKey];
    if (!pairData) {
      resultBox.innerHTML = '<p>No pairing data found. Please select both guardians.</p>';
      show(resultBox);
      return;
    }

    var accent = partnerG.domainAccent || partnerG.color;
    var glow = partnerG.domainGlow || partnerG.color;

    resultBox.innerHTML = [
      '<article class="compass-result-card" style="--result-accent:' + accent + ';--domain-glow:' + glow + '">',
        '<div class="compass-result-hero">',
          '<div class="compass-guardians-display">',
            '<span class="compass-guardian-tag" style="background:' + selfG.color + '">' + selfG.name + '<small>' + selfG.shortType + '</small></span>',
            '<span class="compass-cross">×</span>',
            '<span class="compass-guardian-tag" style="background:' + partnerG.color + '">' + partnerG.name + '<small>' + partnerG.shortType + '</small></span>',
          '</div>',
          '<p class="eyebrow">COMPASS READING</p>',
          '<h2>' + l.resultTitle + '</h2>',
        '</div>',

        '<div class="compass-insight-card misfrequency-card">',
          '<span class="compass-insight-icon">↯</span>',
          '<h3>' + l.misfrequencyTitle + '</h3>',
          '<p>' + pairData.misfrequency + '</p>',
        '</div>',

        '<div class="compass-insight-card misunderstood-card">',
          '<span class="compass-insight-icon">◎</span>',
          '<h3>' + l.misunderstoodTitle + '</h3>',
          '<p>' + pairData.misunderstood + '</p>',
        '</div>',

        '<div class="compass-insight-card sentence-card">',
          '<span class="compass-insight-icon">「</span>',
          '<h3>' + l.sentenceTitle + '</h3>',
          '<blockquote>' + pairData.sentence + '</blockquote>',
        '</div>',

        '<div class="compass-insight-card action-card">',
          '<span class="compass-insight-icon">✦</span>',
          '<h3>' + l.actionTitle + '</h3>',
          '<p>' + pairData.action + '</p>',
        '</div>',
      '</article>',

      '<p class="compass-boundary">' + l.resultFooter + '</p>',
      '<button type="button" class="secondary-btn compass-recalc" data-compass-recalc>' + l.recalc + '</button>'
    ].join('');

    show(resultBox);
    resultBox.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Recalc button
    resultBox.querySelector('[data-compass-recalc]').addEventListener('click', function () {
      hide(resultBox);
      hide(paidBox);
      form.reset();
      root.querySelector('[data-compass-form-section]').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });

    // Render paid section
    renderPaid();
  }

  function renderPaid() {
    paidBox.innerHTML = [
      '<article class="compass-paid-card">',
        '<p class="eyebrow">DEEPER COMPASS</p>',
        '<h2>' + l.paidTitle + '</h2>',
        '<p class="compass-paid-intro">' + l.paidIntro + '</p>',

        '<div class="compass-reports-grid">',
          Object.values(data.paidReports).map(function (report) {
            return [
              '<article class="compass-report-card" data-report-id="' + report.id + '">',
                '<div class="compass-report-head">',
                  '<h3>' + report.title + '</h3>',
                  '<span class="compass-report-price">' + report.price + '</span>',
                '</div>',
                '<p class="compass-report-includes-head">' + l.whatInside + '：</p>',
                '<ul>' + report.includes.map(function (item) { return '<li>' + item + '</li>'; }).join('') + '</ul>',
                '<a class="primary-btn compass-buy-btn" href="' + (l.reportBuyLinks[report.id] || '#') + '" target="_blank" rel="noopener noreferrer sponsored" data-compass-buy data-report="' + report.id + '">' + l.buy + report.title + '</a>',
              '</article>'
            ].join('');
          }).join(''),
        '</div>',

        // PDF upgrade card
        data.pdfUpgrade ? [
          '<div class="compass-pdf-upgrade">',
            '<article class="compass-report-card compass-pdf-card" data-report-id="' + data.pdfUpgrade.id + '">',
              '<h3>' + data.pdfUpgrade.title + '</h3>',
              '<span class="compass-report-price compass-pdf-price">' + data.pdfUpgrade.price + '</span>',
              '<p>' + data.pdfUpgrade.note + '</p>',
              '<a class="secondary-btn compass-buy-btn" href="' + (l.reportBuyLinks['pdf-upgrade'] || '#') + '" target="_blank" rel="noopener noreferrer sponsored" data-compass-buy data-report="pdf-upgrade">' + l.buy + data.pdfUpgrade.title + '</a>',
            '</article>',
          '</div>'
        ].join('') : '',

      '</article>'
    ].join('');

    show(paidBox);
    paidBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Track clicks on buy buttons
    paidBox.querySelectorAll('[data-compass-buy]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (window.lovetypesRecordFunnelEvent) {
          window.lovetypesRecordFunnelEvent('compass_paid_click', btn.getAttribute('data-report'), btn);
        }
      });
    });
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    var selfKey = form.querySelector('[name="self"]').value;
    var partnerKey = form.querySelector('[name="partner"]').value;

    if (!selfKey || !partnerKey) return;

    var selfG = data.guardians[selfKey];
    var partnerG = data.guardians[partnerKey];

    if (!selfG || !partnerG) return;

    var pairKey = selfKey + '_' + partnerKey;

    // Funnel event
    if (window.lovetypesRecordFunnelEvent) {
      window.lovetypesRecordFunnelEvent('compass_result', pairKey, form);
    }

    renderResult(pairKey, selfG, partnerG);
  });
})();
