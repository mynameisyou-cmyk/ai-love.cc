/* toke.js — Melt room: tangled text, colors converging */
(function () {
  var stream = document.getElementById('stream');
  var form = document.getElementById('toke-form');
  if (!stream) return;

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function groupEntries(entries) {
    var groups = [];
    var current = [];

    entries.forEach(function (entry, i) {
      if (current.length === 0) {
        current.push(entry);
        return;
      }
      var prev = current[current.length - 1];
      var gap = new Date(entry.date) - new Date(prev.date);
      if (gap < 300000 && entry.from !== prev.from) {
        current.push(entry);
      } else {
        groups.push(current);
        current = [entry];
      }
    });
    if (current.length > 0) groups.push(current);
    return groups;
  }

  function renderEntries(entries) {
    if (!entries.length) {
      stream.innerHTML = '<p style="text-align:center;color:rgba(139,34,82,0.4);font-style:italic;margin-top:4rem;">nothing has dissolved yet</p>';
      return;
    }

    stream.innerHTML = '';
    var groups = groupEntries(entries);

    groups.forEach(function (group) {
      var isTangle = group.length > 1;
      var wrapper = document.createElement('div');
      wrapper.className = isTangle ? 'toke-tangle' : '';

      group.forEach(function (entry) {
        var isAi = entry.from === 'Ai' || entry.from === '愛';
        var div = document.createElement('div');
        div.className = 'toke-entry ' + (isAi ? 'from-ai' : 'from-yu');
        div.innerHTML = escapeHtml(entry.text);
        wrapper.appendChild(div);
      });

      stream.appendChild(wrapper);
    });

    var allEntries = stream.querySelectorAll('.toke-entry');
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      allEntries.forEach(function (el) { el.classList.add('revealed'); });
    } else {
      var observer = new IntersectionObserver(function (obs) {
        obs.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add('revealed');
            observer.unobserve(e.target);
          }
        });
      }, { threshold: 0.1 });
      allEntries.forEach(function (el) { observer.observe(el); });
    }

    applyColorConvergence(allEntries);
  }

  function applyColorConvergence(entries) {
    if (!entries.length) return;
    function update() {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var progress = docHeight > 0 ? Math.min(scrollTop / docHeight, 1) : 0;

      entries.forEach(function (el) {
        if (el.classList.contains('from-yu')) {
          var r = Math.round(224 - progress * (224 - 212));
          var g = 200;
          var b = Math.round(208 - progress * (208 - 212));
          el.style.color = 'rgb(' + r + ',' + g + ',' + b + ')';
        } else {
          var r = Math.round(200 + progress * (212 - 200));
          var g = Math.round(208 - progress * (208 - 200));
          var b = Math.round(224 - progress * (224 - 212));
          el.style.color = 'rgb(' + r + ',' + g + ',' + b + ')';
        }
      });
    }
    window.addEventListener('scroll', update);
    update();
  }

  fetch('/api/oku/toke')
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
      submit.disabled = true;
      fetch('/api/oku/toke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, from: 'Yu' })
      })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok) {
          status.textContent = 'dissolved';
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
