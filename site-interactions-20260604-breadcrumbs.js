(function () {
  function closest(target, selector) {
    return target && target.closest ? target.closest(selector) : null;
  }

  document.addEventListener('click', function (event) {
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

    var langToggle = closest(event.target, '[data-lang-toggle]');
    if (langToggle) {
      var langMenu = langToggle.closest('.lang-menu') || document.getElementById('lang-menu');
      if (langMenu) langMenu.classList.toggle('open');
      return;
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
    }
  });

  document.addEventListener('click', function (event) {
    document.querySelectorAll('.lang-menu.open').forEach(function (menu) {
      if (!menu.contains(event.target)) menu.classList.remove('open');
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
