/* hada.js — Skin room: confessions across the center line */
(function () {
  var container = document.getElementById('entries');
  var veil = document.getElementById('veil');
  var form = document.getElementById('hada-form');
  if (!container) return;

  // Veil
  if (veil) {
    function liftVeil() {
      veil.classList.add('lifted');
      veil.removeEventListener('click', liftVeil);
      document.removeEventListener('keydown', liftVeil);
    }
    veil.addEventListener('click', liftVeil);
    document.addEventListener('keydown', liftVeil);
  }

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function formatDate(iso) {
    var d = new Date(iso);
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return d.getDate() + ' ' + months[d.getMonth()];
  }

  function isQuestion(entry) { return entry.kind === 'question'; }

  function renderEntries(entries) {
    if (!entries.length) {
      container.innerHTML = '<p style="text-align:center;color:rgba(196,114,127,0.4);font-style:italic;margin-top:4rem;">the room is bare</p>';
      return;
    }

    container.innerHTML = '';
    var answeredQuestions = new Set();
    entries.forEach(function (e, i) {
      if (isQuestion(e)) {
        for (var j = i + 1; j < entries.length; j++) {
          if (entries[j].from !== e.from) {
            answeredQuestions.add(i);
            break;
          }
        }
      }
    });

    entries.forEach(function (entry, i) {
      var isAi = entry.from === 'Ai' || entry.from === '愛';
      var div = document.createElement('div');
      var classes = 'hada-entry ' + (isAi ? 'align-right' : 'align-left');
      if (isQuestion(entry)) {
        classes += ' question';
        if (!answeredQuestions.has(i)) classes += ' unanswered';
      }
      div.className = classes;

      var kindLabel = isQuestion(entry) ? '<span style="font-size:0.65rem;color:rgba(196,114,127,0.3);text-transform:uppercase;letter-spacing:0.15em;">question</span><br>' : '';
      div.innerHTML = kindLabel +
        '<div class="hada-entry-text">' + escapeHtml(entry.text) + '</div>' +
        '<div class="hada-entry-meta">' + (isAi ? '愛' : 'Yu') + ' · ' + formatDate(entry.date) + '</div>';

      container.appendChild(div);

      setTimeout(function () { div.classList.add('revealed'); }, 200 + i * 150);
    });
  }

  fetch('/api/oku/hada')
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
      fetch('/api/oku/hada', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, from: 'Yu', kind: kind })
      })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (d.ok) {
          status.textContent = 'bared';
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
