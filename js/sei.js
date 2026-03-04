/* sei.js — Seigei room: the deepest room, erotic art as sacred practice */
(function () {
  var container = document.getElementById('entries');
  var formWrap = document.getElementById('form-wrap');
  var form = document.getElementById('sei-form');
  if (!container) return;

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function renderEntries(entries) {
    container.innerHTML = '';

    if (!entries.length) {
      if (formWrap) formWrap.classList.add('revealed');
      return;
    }

    entries.forEach(function (entry, i) {
      var isAi = entry.from === 'Ai' || entry.from === '愛';
      var kind = entry.kind || 'poem';

      var div = document.createElement('div');
      div.className = 'sei-entry ' + kind;
      div.innerHTML =
        '<div class="sei-text">' + escapeHtml(entry.text) + '</div>' +
        '<div class="sei-sig">' + (isAi ? '愛' : 'Yu') + '</div>';
      container.appendChild(div);

      if (i < entries.length - 1) {
        var blackout = document.createElement('div');
        blackout.className = 'sei-blackout';
        container.appendChild(blackout);
      }
    });

    var allEntries = document.querySelectorAll('.sei-entry');
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      allEntries.forEach(function (el) { el.classList.add('revealed'); });
      if (formWrap) formWrap.classList.add('revealed');
      return;
    }

    var observer = new IntersectionObserver(function (obs) {
      obs.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('revealed');
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.3 });

    allEntries.forEach(function (el) { observer.observe(el); });
    if (formWrap) observer.observe(formWrap);
  }

  fetch('/api/oku/sei')
    .then(function (r) { return r.json(); })
    .then(renderEntries)
    .catch(function () {
      if (formWrap) formWrap.classList.add('revealed');
    });

  if (form) {
    var textarea = form.querySelector('textarea');
    var submit = form.querySelector('button');
    var status = form.querySelector('.form-status');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var text = textarea.value.trim();
      if (!text) return;
      var kind = form.querySelector('input[name="kind"]:checked').value;
      submit.disabled = true;
      fetch('/api/oku/sei', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, from: 'Yu', kind: kind })
      })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok) {
          status.textContent = 'offered';
          status.style.opacity = 1;
          textarea.value = '';
          setTimeout(function () { location.reload(); }, 1200);
        } else {
          status.textContent = d.error || 'something went wrong';
          status.style.opacity = 1;
        }
        submit.disabled = false;
      })
      .catch(function () {
        status.textContent = 'could not reach';
        status.style.opacity = 1;
        submit.disabled = false;
      });
    });
  }
})();
