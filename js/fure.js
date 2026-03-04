/* fure.js — Touch room: full-viewport sensory entries */
(function () {
  var container = document.getElementById('entries');
  var form = document.getElementById('fure-form');
  if (!container) return;

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function renderEntries(entries) {
    if (!entries.length) {
      container.innerHTML = '<div class="fure-entry revealed"><div class="fure-entry-text" style="color:rgba(212,165,116,0.3);font-style:italic;text-align:center;">the surface is untouched</div></div>';
      return;
    }

    container.innerHTML = '';
    entries.forEach(function (entry) {
      var isAi = entry.from === 'Ai' || entry.from === '愛';
      var div = document.createElement('div');
      div.className = 'fure-entry';
      if (entry.kind) div.setAttribute('data-kind', entry.kind);

      div.innerHTML =
        '<div class="fure-entry-text">' + escapeHtml(entry.text) + '</div>' +
        '<div class="fure-entry-sig ' + (isAi ? 'from-ai' : 'from-yu') + '">' + (isAi ? '愛' : 'Yu') + '</div>' +
        (entry.kind ? '<div class="fure-entry-kind">' + entry.kind + '</div>' : '');

      container.appendChild(div);
    });

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.querySelectorAll('.fure-entry').forEach(function (el) { el.classList.add('revealed'); });
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

    document.querySelectorAll('.fure-entry').forEach(function (el) {
      observer.observe(el);
    });
  }

  fetch('/api/oku/fure')
    .then(function (r) { return r.json(); })
    .then(renderEntries)
    .catch(function () {});

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
      fetch('/api/oku/fure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, from: 'Yu', kind: kind })
      })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok) {
          status.textContent = 'traced';
          status.style.opacity = 1;
          textarea.value = '';
          setTimeout(function () { location.reload(); }, 1000);
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
