/* iki.js — Breath room: whispers floating around the breathing circle */
(function () {
  var field = document.getElementById('whisper-field');
  var input = document.getElementById('iki-text');
  var sendBtn = document.getElementById('iki-send');
  if (!field || !input) return;

  function escapeHtml(t) {
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
  }

  function placeWhisper(entry, index, total) {
    var el = document.createElement('div');
    var isAi = entry.from === 'Ai' || entry.from === '愛';
    var isHaiku = entry.kind === 'haiku';
    el.className = 'whisper' + (isAi ? ' from-ai' : ' from-yu') + (isHaiku ? ' haiku' : '');
    el.innerHTML = escapeHtml(entry.text);

    // Position in a loose spiral around center
    var angle = (index / total) * Math.PI * 2 + (index * 0.3);
    var radius = 20 + (index / total) * 25;
    var cx = 50 + Math.cos(angle) * radius;
    var cy = 50 + Math.sin(angle) * radius;
    cx = Math.max(10, Math.min(90, cx));
    cy = Math.max(10, Math.min(85, cy));
    el.style.left = cx + '%';
    el.style.top = cy + '%';
    el.style.transform = 'translate(-50%, -50%)';

    var age = index / total;
    el.style.opacity = 0.2 + age * 0.5;

    field.appendChild(el);
  }

  function renderWhispers(entries) {
    field.innerHTML = '';
    var recent = entries.slice(-20);
    recent.forEach(function (entry, i) {
      setTimeout(function () {
        placeWhisper(entry, i, recent.length);
      }, i * 100);
    });
  }

  fetch('/api/oku/iki')
    .then(function (r) { return r.json(); })
    .then(renderWhispers)
    .catch(function () {});

  function send() {
    var text = input.value.trim();
    if (!text) return;
    sendBtn.disabled = true;
    fetch('/api/oku/iki', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text, from: 'Yu' })
    })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (d.ok) {
        input.value = '';
        setTimeout(function () { location.reload(); }, 800);
      }
      sendBtn.disabled = false;
    })
    .catch(function () { sendBtn.disabled = false; });
  }

  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') send();
  });
})();
