(function () {
  var data = window.__COMPASS_DATA;
  var root = document.querySelector('[data-compass-root]');
  if (!data || !root) return;

  var guardianSlugs = { W: 'iris', T: 'noah', G: 'vivian', S: 'claire', P: 'dora' };
  var guideSlugs = {
    W: 'words-of-affirmation-scripts',
    T: 'quality-time-long-distance',
    G: 'gifts-are-not-materialism',
    S: 'acts-of-service-boundaries',
    P: 'physical-touch-consent-safety'
  };
  var labels = {
    self: '我的情感守護者',
    partner: '對方的情感守護者',
    status: '目前關係狀態',
    issue: '最想整理的問題',
    submit: '取得免費羅盤',
    result: '你們的羅盤解讀',
    misfrequency: '主要錯頻',
    misunderstood: '最需要被理解的地方',
    sentence: '一句可以說出口的話',
    action: '24 小時內可做的小行動',
    copy: '複製解讀',
    copied: '已複製',
    copyLink: '複製這組設定',
    copiedLink: '已複製連結',
    retry: '重新選擇',
    boundary: '羅盤只根據兩個自填守護者與當下情境整理溝通選項，不評分相配程度，也不預測關係結果。任何一方都可以拒絕、改時間或提出替代做法；若有暴力、威脅、控制或強迫，請先尋求安全支援。'
  };

  function optionMarkup(items) {
    return items.map(function (item) {
      return '<option value="' + item.value + '">' + item.label + '</option>';
    }).join('');
  }

  var guardianOptions = Object.keys(data.guardians).map(function (key) {
    var guardian = data.guardians[key];
    return { value: key, label: guardian.name + ' · ' + guardian.type };
  });
  var statusOptions = (data.statusOptions || []).map(function (item) {
    return { value: item.id, label: item.label };
  });
  var issueOptions = (data.issueOptions || []).map(function (item) {
    return { value: item.id, label: item.label };
  });

  root.innerHTML = [
    '<section class="compass-form-section" data-compass-form-section>',
      '<form class="compass-form" data-compass-form>',
        '<div class="compass-form-row">',
          '<div class="compass-form-field"><label for="compass-self">' + labels.self + '</label><select id="compass-self" name="self" required><option value="">請選擇</option>' + optionMarkup(guardianOptions) + '</select></div>',
          '<div class="compass-form-field"><label for="compass-partner">' + labels.partner + '</label><select id="compass-partner" name="partner" required><option value="">請選擇</option>' + optionMarkup(guardianOptions) + '</select></div>',
        '</div>',
        '<div class="compass-form-row">',
          '<div class="compass-form-field"><label for="compass-status">' + labels.status + '</label><select id="compass-status" name="status"><option value="">不指定</option>' + optionMarkup(statusOptions) + '</select></div>',
          '<div class="compass-form-field"><label for="compass-issue">' + labels.issue + '</label><select id="compass-issue" name="issue"><option value="">不指定</option>' + optionMarkup(issueOptions) + '</select></div>',
        '</div>',
        '<button type="submit" class="primary-btn compass-submit">' + labels.submit + '</button>',
      '</form>',
    '</section>',
    '<section class="compass-result" data-compass-result hidden aria-live="polite"></section>'
  ].join('');

  var form = root.querySelector('[data-compass-form]');
  var resultBox = root.querySelector('[data-compass-result]');

  function selectedText(name) {
    var field = form.elements[name];
    var option = field && field.options[field.selectedIndex];
    return option ? option.textContent.trim() : '';
  }

  function resultUrl(values) {
    var url = new URL('/compass/', window.location.origin);
    ['self', 'partner', 'status', 'issue'].forEach(function (key) {
      if (values[key]) url.searchParams.set(key, values[key]);
    });
    url.hash = 'relationship-compass-tool';
    return url.toString();
  }

  async function copyText(text, button, doneLabel) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        var area = document.createElement('textarea');
        area.value = text;
        area.setAttribute('readonly', '');
        area.style.position = 'fixed';
        area.style.left = '-9999px';
        document.body.appendChild(area);
        area.select();
        document.execCommand('copy');
        area.remove();
      }
      var original = button.textContent;
      button.textContent = doneLabel;
      window.setTimeout(function () { button.textContent = original; }, 1800);
    } catch (_error) {
      window.prompt('請手動複製', text);
    }
  }

  function renderResult(values) {
    var selfGuardian = data.guardians[values.self];
    var partnerGuardian = data.guardians[values.partner];
    var pairing = data.pairings[values.self + '_' + values.partner];
    if (!selfGuardian || !partnerGuardian || !pairing) return;

    var selfSlug = guardianSlugs[values.self];
    var guideSlug = guideSlugs[values.self];
    var summary = [
      'LoveTypes 關係羅盤',
      labels.self + '：' + selfGuardian.name + ' · ' + selfGuardian.type,
      labels.partner + '：' + partnerGuardian.name + ' · ' + partnerGuardian.type,
      labels.status + '：' + (selectedText('status') || '未指定'),
      labels.issue + '：' + (selectedText('issue') || '未指定'),
      labels.misfrequency + '：' + pairing.misfrequency,
      labels.misunderstood + '：' + pairing.misunderstood,
      labels.sentence + '：' + pairing.sentence,
      labels.action + '：' + pairing.action,
      labels.boundary
    ].join('\n');

    resultBox.innerHTML = [
      '<article class="compass-result-card">',
        '<div class="compass-result-head"><p class="eyebrow">COMPASS READING</p><h2>' + labels.result + '</h2><p>' + selfGuardian.name + ' × ' + partnerGuardian.name + '</p></div>',
        '<div class="compass-insight-card misfrequency-card"><h3>' + labels.misfrequency + '</h3><p>' + pairing.misfrequency + '</p></div>',
        '<div class="compass-insight-card misunderstood-card"><h3>' + labels.misunderstood + '</h3><p>' + pairing.misunderstood + '</p></div>',
        '<div class="compass-insight-card sentence-card"><h3>' + labels.sentence + '</h3><blockquote>' + pairing.sentence + '</blockquote></div>',
        '<div class="compass-insight-card action-card"><h3>' + labels.action + '</h3><p>' + pairing.action + '</p></div>',
        '<div class="compass-insight-card compass-result-next-steps"><h3>免費下一步</h3><p>先選一個今天能完成的入口，不必一次處理完整段關係。</p><div class="compass-next-step-actions">',
          '<a class="secondary-btn" href="/characters/' + selfSlug + '/">閱讀我的守護者</a>',
          '<a class="secondary-btn" href="/guides/' + guideSlug + '/">閱讀對應指南</a>',
          '<a class="secondary-btn" href="/repair-plan/#plan-' + selfSlug + '">填寫 7 日修復表</a>',
        '</div></div>',
      '</article>',
      '<p class="compass-boundary">' + labels.boundary + '</p>',
      '<div class="compass-next-step-actions">',
        '<button type="button" class="secondary-btn" data-compass-copy>' + labels.copy + '</button>',
        '<button type="button" class="secondary-btn" data-compass-copy-link>' + labels.copyLink + '</button>',
        '<button type="button" class="secondary-btn" data-compass-retry>' + labels.retry + '</button>',
      '</div>'
    ].join('');
    resultBox.hidden = false;
    resultBox.querySelector('[data-compass-copy]').addEventListener('click', function (event) {
      copyText(summary, event.currentTarget, labels.copied);
    });
    resultBox.querySelector('[data-compass-copy-link]').addEventListener('click', function (event) {
      copyText(resultUrl(values), event.currentTarget, labels.copiedLink);
    });
    resultBox.querySelector('[data-compass-retry]').addEventListener('click', function () {
      resultBox.hidden = true;
      resultBox.innerHTML = '';
      form.reset();
      form.elements.self.focus();
    });
    resultBox.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var values = {
      self: form.elements.self.value,
      partner: form.elements.partner.value,
      status: form.elements.status.value,
      issue: form.elements.issue.value
    };
    if (!values.self || !values.partner) return;
    renderResult(values);
  });

  var params = new URLSearchParams(window.location.search);
  ['self', 'partner', 'status', 'issue'].forEach(function (key) {
    var field = form.elements[key];
    var value = params.get(key) || '';
    if (field && Array.from(field.options).some(function (option) { return option.value === value; })) field.value = value;
  });
})();
