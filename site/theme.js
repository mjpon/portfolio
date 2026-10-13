// Light and dark switch in the header.
// Until someone uses it, the site follows the device's setting. Using it saves the choice in
// this browser, and the small script in each page's head applies it before the page paints.
(function () {
  var root = document.documentElement;
  var button = document.querySelector('.theme');
  if (!button) return;
  var systemDark = window.matchMedia('(prefers-color-scheme: dark)');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

  function current() {
    return root.getAttribute('data-theme') || (systemDark.matches ? 'dark' : 'light');
  }

  function sync() {
    button.setAttribute('aria-checked', current() === 'dark' ? 'true' : 'false');
  }

  function apply(theme) {
    root.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('theme', theme);
    } catch (e) {
      // Storage can be blocked. The switch still works for this visit.
    }
    sync();
  }

  button.addEventListener('click', function () {
    var next = current() === 'dark' ? 'light' : 'dark';
    // Where the browser can, the new colors roll down the page from the header,
    // like a departure board refreshing. Otherwise they change at once.
    if (!document.startViewTransition || reduced.matches) {
      apply(next);
      return;
    }
    root.classList.add('theme-switching');
    var transition = document.startViewTransition(function () {
      apply(next);
    });
    transition.finished.finally(function () {
      root.classList.remove('theme-switching');
    });
  });

  systemDark.addEventListener('change', sync);
  sync();
})();
