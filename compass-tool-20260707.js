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
      resultOfferTitle: 'Turn this result into a saved report',
      resultOfferIntro: 'Want a printable compatibility report with scripts and a 7-day next step? Send us this pairing first, and we will prioritize the report format people actually request.',
      resultOfferCta: 'Request this report',
      resultOfferSubject: 'LoveTypes Compass report request',
      resultOfferBody: 'I want a saved Relationship Compass report for this pairing.',
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
    ja: {
      title: 'LoveTypes 関係コンパス',
      subtitle: 'あなたと相手の愛の言語がどこで交差しているかを見つけ、今日から始められる一歩を無料で手に入れましょう。',
      selfLabel: '私のLoveTypesガーディアン',
      partnerLabel: '相手のLoveTypesガーディアン',
      dobLabel: '生年月日（任意）',
      dobSelf: '私の誕生日',
      dobPartner: '相手の誕生日',
      dobHint: '月/日/年 — 任意。リズムの洞察に役立ちます',
      statusLabel: '現在の関係',
      issueLabel: '一番改善したいこと',
      submit: 'コンパスを取得',
      loading: '2つの言語を読み取り中…',
      resultTitle: 'あなたのコンパスリーディング',
      misfrequencyTitle: '主なクロスシグナル',
      misunderstoodTitle: '最も理解が必要なこと',
      sentenceTitle: '相手に伝えられる一言',
      actionTitle: '24時間以内にできる小さなアクション',
      paidTitle: '完全なマップが必要ですか？',
      paidIntro: '無料コンパスは最初の一歩を示します。これらのレポートは、スクリプト、スケジュール、そしてあなたのペアリングの深い理解を提供します。',
      pdfTitle: 'PDFコレクターズエディションを追加',
      pdfNote: '美しいデザイン、印刷可能、永久保存。',
      buy: '購入 ',
      whatInside: '含まれるもの',
      resultOfferTitle: 'この結果を保存版レポートにする',
      resultOfferIntro: '会話例と7日間の次の一歩を入れたPDF相性レポートが必要な場合は、この組み合わせを送ってください。実際に依頼が多い形式から優先します。',
      resultOfferCta: 'このレポートを依頼する',
      resultOfferSubject: 'LoveTypes コンパスレポート依頼',
      resultOfferBody: 'この組み合わせの保存版Relationship Compassレポートを希望します。',
      reportLabels: {
        'emotional-pattern': 'あなたの感情パターンレポート',
        'compatibility': 'LoveTypes 相性レポート',
        'bazi': '四柱推命 相性レポート',
        'timing-2026': '2026年 恋愛タイミング',
        'repair-plan': '7日間の関係修復プラン'
      },
      reportBuyLinks: {},
      resultFooter: 'このコンパスは判断ではなく、振り返りの出発点です。愛がないのではなく、届き方が違うだけかもしれません。マップは判決ではなく、関係を思い出すためのリマインダーです。',
      recalc: '再入力'
    },
    ko: {
      title: 'LoveTypes 관계 컴퍼스',
      subtitle: '두 사람의 사랑 언어가 어디에서 엇갈리는지 보고, 오늘 시작할 수 있는 첫걸음을 무료로 찾으세요.',
      selfLabel: '나의 LoveTypes 가디언',
      partnerLabel: '상대의 LoveTypes 가디언',
      dobLabel: '생년월일 (선택)',
      dobSelf: '내 생일',
      dobPartner: '상대 생일',
      dobHint: '월/일/년 — 선택 사항. 타이밍 인사이트에 도움',
      statusLabel: '현재 관계 상태',
      issueLabel: '가장 개선하고 싶은 것',
      submit: '컴퍼스 받기',
      loading: '두 언어를 읽는 중…',
      resultTitle: '컴퍼스 리딩',
      misfrequencyTitle: '주요 크로스 시그널',
      misunderstoodTitle: '가장 이해가 필요한 부분',
      sentenceTitle: '상대에게 할 수 있는 한마디',
      actionTitle: '24시간 안에 할 수 있는 작은 행동',
      paidTitle: '전체 지도가 필요하신가요?',
      paidIntro: '무료 컴퍼스는 첫걸음을 보여줍니다. 이 레포트들은 대화 스크립트, 일정, 그리고 두 분의 독특한 페어링에 대한 깊은 이해를 제공합니다.',
      pdfTitle: 'PDF 컬렉터 에디션 추가',
      pdfNote: '아름답게 디자인되어 인쇄 가능, 영구 보관.',
      buy: '구매 ',
      whatInside: '포함 내용',
      resultOfferTitle: '이 결과를 저장용 리포트로 만들기',
      resultOfferIntro: '대화 스크립트와 7일 다음 단계를 담은 PDF 궁합 리포트가 필요하다면 이 조합을 보내주세요. 실제 요청이 많은 형식부터 우선 제작합니다.',
      resultOfferCta: '이 리포트 요청하기',
      resultOfferSubject: 'LoveTypes 컴퍼스 리포트 요청',
      resultOfferBody: '이 조합의 저장용 Relationship Compass 리포트를 원합니다.',
      reportLabels: {
        'emotional-pattern': '감정 패턴 레포트',
        'compatibility': 'LoveTypes 궁합 레포트',
        'bazi': '사주 궁합 레포트',
        'timing-2026': '2026 연애 타이밍',
        'repair-plan': '7일 관계 회복 플랜'
      },
      reportBuyLinks: {},
      resultFooter: '이 컴퍼스는 판단이 아닌, 성찰의 출발점입니다. 사랑이 없는 것이 아니라, 도착하는 방식이 다를 수 있습니다. 지도는 판결이 아니라, 관계를 돌보는 길을 상기시켜 줍니다.',
      recalc: '다시 입력'
    },
    es: {
      title: 'LoveTypes Brújula de Relación',
      subtitle: 'Descubre dónde se cruzan sus lenguajes del amor y encuentra un punto de partida hoy, gratis.',
      selfLabel: 'Mi guardián LoveTypes',
      partnerLabel: 'Su guardián LoveTypes',
      dobLabel: 'Fechas de nacimiento (opcional)',
      dobSelf: 'Mi cumpleaños',
      dobPartner: 'Su cumpleaños',
      dobHint: 'DD/MM/AAAA — opcional, ayuda con insights de ritmo',
      statusLabel: 'Estado actual',
      issueLabel: 'Lo que más quiero mejorar',
      submit: 'Obtener mi Brújula',
      loading: 'Leyendo sus dos idiomas…',
      resultTitle: 'Tu Lectura de Brújula',
      misfrequencyTitle: 'Tu señal cruzada principal',
      misunderstoodTitle: 'Lo que más necesita ser comprendido',
      sentenceTitle: 'Una frase que puedes decir',
      actionTitle: 'Una pequeña acción en 24 horas',
      paidTitle: '¿Quieres el mapa completo?',
      paidIntro: 'La brújula gratuita te muestra el primer paso. Estos informes te dan el camino completo: guiones, horarios y una comprensión profunda de tu combinación única.',
      pdfTitle: 'Añadir Edición Coleccionable en PDF',
      pdfNote: 'Bellamente diseñado, imprimible, para conservar siempre.',
      buy: 'Comprar ',
      whatInside: 'Qué incluye',
      resultOfferTitle: 'Convertir este resultado en un informe guardable',
      resultOfferIntro: 'Si quieres un PDF de compatibilidad con guiones y un siguiente paso de 7 días, envíanos esta combinación. Priorizaremos los formatos que la gente realmente pida.',
      resultOfferCta: 'Solicitar este informe',
      resultOfferSubject: 'Solicitud de informe LoveTypes Compass',
      resultOfferBody: 'Quiero un informe guardable de Relationship Compass para esta combinación.',
      reportLabels: {
        'emotional-pattern': 'Tu Patrón Emocional de Amor',
        'compatibility': 'Informe de Compatibilidad LoveTypes',
        'bazi': 'Compatibilidad Amorosa BaZi',
        'timing-2026': 'Ritmo Amoroso 2026',
        'repair-plan': 'Plan de Reparación de 7 Días'
      },
      reportBuyLinks: {},
      resultFooter: 'Esta brújula es un punto de partida para la reflexión, no un veredicto. Tu amor puede no estar ausente — puede que simplemente llegue en idiomas diferentes. El mapa es un recordatorio, no un juicio.',
      recalc: 'Intentar de nuevo'
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
      resultOfferTitle: '把這份結果變成可保存報告',
      resultOfferIntro: '如果你想要含對話句型與 7 日下一步的 PDF 合盤報告，先把這組配對寄給我們。我們會優先製作真正有人需要的格式。',
      resultOfferCta: '需求這份報告',
      resultOfferSubject: 'LoveTypes 羅盤報告需求',
      resultOfferBody: '我想要這組配對的可保存 Relationship Compass 報告。',
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
  // Ponytail: fall back buy links to EN when locale reportBuyLinks is empty
  if (!l.reportBuyLinks || !Object.keys(l.reportBuyLinks).length) {
    l.reportBuyLinks = labels.en.reportBuyLinks;
  }
  // Fall back to EN commerce/deep data when a locale only ships UI labels.
  if (window.__COMPASS_DATA_EN) {
    if (!data.pairings || !Object.keys(data.pairings).length || Object.keys(data.pairings).length < 20) {
      data.pairings = window.__COMPASS_DATA_EN.pairings;
    }
    if (!data.reports || !Object.keys(data.reports).length) {
      data.reports = window.__COMPASS_DATA_EN.reports;
    }
    if (!data.pdfUpgrade) {
      data.pdfUpgrade = window.__COMPASS_DATA_EN.pdfUpgrade;
    }
  }

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
      '<h2>' + l.title + '</h2>',
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

  function selectedLabel(selector) {
    var field = form.querySelector(selector);
    if (!field) return '';
    var option = field.options && field.selectedIndex >= 0 ? field.options[field.selectedIndex] : null;
    return option ? option.textContent.trim() : field.value.trim();
  }

  function reportRequestHref(pairKey, selfG, partnerG, pairData, intake) {
    var subject = l.resultOfferSubject + ': ' + selfG.name + ' × ' + partnerG.name;
    var body = [
      l.resultOfferBody,
      '',
      'Pair: ' + pairKey,
      'Self: ' + selfG.name + ' / ' + selfG.type,
      'Partner: ' + partnerG.name + ' / ' + partnerG.type,
      'Status: ' + (intake.status || '-'),
      'Issue: ' + (intake.issue || '-'),
      'My birthday: ' + (intake.dobSelf || '-'),
      'Their birthday: ' + (intake.dobPartner || '-'),
      '',
      'Free compass result:',
      'Main cross-signal: ' + pairData.misfrequency,
      'Needs understanding: ' + pairData.misunderstood,
      'Sentence to say: ' + pairData.sentence,
      '24-hour action: ' + pairData.action,
      'Page: ' + window.location.href
    ].join('\n');
    return 'mailto:contact@lovetypes.tw?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  }

  function renderResult(pairKey, selfG, partnerG, intake) {
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
            '<span class="compass-guardian-tag" style="--tag-color:' + selfG.domainAccent + '">' + selfG.name + '<small>' + selfG.shortType + '</small></span>',
            '<span class="compass-cross">×</span>',
            '<span class="compass-guardian-tag" style="--tag-color:' + partnerG.domainAccent + '">' + partnerG.name + '<small>' + partnerG.shortType + '</small></span>',
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

        '<div class="compass-insight-card compass-result-offer" data-compass-result-offer>',
          '<span class="compass-insight-icon">◆</span>',
          '<h3>' + l.resultOfferTitle + '</h3>',
          '<p>' + l.resultOfferIntro + '</p>',
          '<a class="primary-btn compass-buy-btn" href="' + reportRequestHref(pairKey, selfG, partnerG, pairData, intake) + '" data-compass-result-report-request data-funnel-event="compass_result_report_request">' + l.resultOfferCta + '</a>',
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

    var requestBtn = resultBox.querySelector('[data-compass-result-report-request]');
    if (requestBtn) {
      requestBtn.addEventListener('click', function () {
        if (window.lovetypesRecordFunnelEvent) {
          window.lovetypesRecordFunnelEvent('compass_result_report_request', pairKey, requestBtn);
        }
      });
    }

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
    var intake = {
      status: selectedLabel('[name="status"]'),
      issue: selectedLabel('[name="issue"]'),
      dobSelf: form.querySelector('[name="dobSelf"]').value,
      dobPartner: form.querySelector('[name="dobPartner"]').value
    };

    // Funnel event
    if (window.lovetypesRecordFunnelEvent) {
      window.lovetypesRecordFunnelEvent('compass_result', pairKey, form);
    }

    renderResult(pairKey, selfG, partnerG, intake);
  });
})();
