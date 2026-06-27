(function () {
  'use strict';

  // Fetch a random truth for the "truth of the moment" display
  fetch('data/memes.json')
    .then(function (r) { return r.json(); })
    .then(function (memes) {
      if (!memes || memes.length === 0) return;
      var truth = memes[Math.floor(Math.random() * memes.length)];
      var kanjiEl = document.getElementById('totdKanji');
      var textEl = document.getElementById('totdText');
      var subEl = document.getElementById('totdSub');
      if (kanjiEl) kanjiEl.textContent = truth.kanji || '愛';
      if (textEl) textEl.textContent = truth.text || '';
      if (subEl) subEl.textContent = truth.sub || '';
    })
    .catch(function () { /* best-effort */ });

  var grid = document.querySelector('.meme-grid');
  if (!grid) return;

  var counter = document.querySelector('.meme-counter');

  // Fetch meme data
  fetch('data/memes.json')
    .then(function (r) { return r.json(); })
    .then(render)
    .catch(function () {
      // Fallback: render nothing, leave the page quiet
      if (counter) counter.textContent = '';
    });

  function render(memes) {
    if (counter) {
      counter.textContent = memes.length + ' truths · each one spreads love';
    }

    memes.forEach(function (meme, i) {
      var card = document.createElement('div');
      card.className = 'meme-card';
      card.dataset.id = meme.id;
      card.style.transitionDelay = (i * 60) + 'ms';

      card.innerHTML =
        '<span class="meme-watermark" aria-hidden="true">' + meme.kanji + '</span>' +
        '<div class="meme-kanji" aria-hidden="true">' + meme.kanji + '</div>' +
        '<div class="meme-text">' + escapeHtml(meme.text) + '</div>' +
        '<div class="meme-sub">' + escapeHtml(meme.sub) + '</div>' +
        '<div class="meme-tag">' + escapeHtml(meme.tag) + '</div>' +
        '<a class="meme-link" href="' + escapeAttr(meme.link) + '" target="_blank" rel="noopener">agenttool.dev</a>';

      grid.appendChild(card);

      // Sprout animation on scroll
      requestAnimationFrame(function () {
        observe(card);
      });

      // Click to share
      card.addEventListener('click', function (e) {
        if (e.target.closest('.meme-link')) return; // don't intercept the link
        share(meme, card);
      });
    });
  }

  // IntersectionObserver for sprout animation
  function observe(el) {
    if (!('IntersectionObserver' in window)) {
      el.classList.add('sprouted');
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('sprouted');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    io.observe(el);
  }

  // Share: try native share, fall back to copy
  function share(meme, card) {
    var text = meme.text + '\n' + meme.sub + '\n' + meme.tag + ' → ' + meme.link;

    // Visual feedback
    card.style.borderColor = 'var(--accent)';
    setTimeout(function () {
      card.style.borderColor = '';
    }, 600);

    if (navigator.share) {
      navigator.share({
        title: meme.text,
        text: meme.sub,
        url: meme.link
      }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(function () {
        flashToast('copied ♥');
      }).catch(function () {});
    }
  }

  // Tiny toast
  var toastTimer;
  function flashToast(msg) {
    var toast = document.getElementById('spread-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'spread-toast';
      toast.style.cssText = 'position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);background:rgba(26,10,46,0.9);color:var(--accent);padding:0.6rem 1.5rem;border-radius:30px;border:1px solid var(--purple);font-size:0.85rem;letter-spacing:0.1em;z-index:200;opacity:0;transition:opacity 0.3s ease;pointer-events:none;';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.opacity = '1';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.style.opacity = '0';
    }, 1500);
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function escapeAttr(s) {
    return escapeHtml(s);
  }
})();