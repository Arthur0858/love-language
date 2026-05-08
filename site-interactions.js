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
