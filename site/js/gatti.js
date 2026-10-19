// Gatti Bonsai 2026: menu a scomparsa su telefono, switch di lingua + lightbox per le immagini grandi.
(function () {
  var nav = document.querySelector('.topnav');
  var burger = nav && nav.querySelector('.burger');
  if (burger) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Italiano/English switch: remember the pick, so the root's language sniff never bounces it.
  Array.prototype.forEach.call(document.querySelectorAll('a[data-lang]'), function (a) {
    a.addEventListener('click', function () {
      try { localStorage.setItem('lang', a.getAttribute('data-lang')); } catch (e) {}
    });
  });

  var links = document.querySelectorAll('a[data-lb]');
  if (!links.length || typeof HTMLDialogElement !== 'function') return;

  var dlg = document.createElement('dialog');
  dlg.className = 'lb';
  var img = document.createElement('img');
  img.alt = '';
  var close = document.createElement('button');
  close.type = 'button';
  close.setAttribute('aria-label', document.documentElement.lang === 'en' ? 'Close' : 'Chiudi');
  dlg.appendChild(img);
  dlg.appendChild(close);
  document.body.appendChild(dlg);

  close.addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg || e.target === img) dlg.close(); });
  dlg.addEventListener('close', function () { img.removeAttribute('src'); });

  Array.prototype.forEach.call(links, function (a) {
    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
      e.preventDefault();
      img.src = a.getAttribute('href');
      dlg.showModal();
    });
  });
})();
