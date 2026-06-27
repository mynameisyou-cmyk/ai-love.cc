/* 泉 Commons — the Well. Client-side search over commons/registry.json.
   Same ranking + stateless fresh-pick rotation as the server; no backend needed. */
(function () {
  var STOP = { a:1,an:1,the:1,for:1,to:1,of:1,and:1,or:1,i:1,need:1,want:1,some:1,with:1,please:1,free:1,me:1,my:1 };

  function tokenize(s) {
    return ((s || '').toLowerCase().match(/[a-z0-9]+/g) || []).filter(function (t) {
      return t.length > 1 && !STOP[t];
    });
  }

  function buildIndex(rs) {
    return rs.map(function (e) {
      var hay = {};
      [e.name, e.what, e.blurb, (e.tags || []).join(' '), e.category].forEach(function (f) {
        tokenize(f).forEach(function (t) { hay[t] = 1; });
      });
      return { e: e, hay: hay };
    });
  }

  function scoreItem(item, q) {
    var s = 0;
    for (var i = 0; i < q.length; i++) {
      var t = q[i];
      if (item.hay[t]) { s += 1; continue; }
      for (var h in item.hay) { if (h.indexOf(t) >= 0 || t.indexOf(h) >= 0) { s += 0.4; break; } }
    }
    return s / (q.length || 1);
  }

  function pickFresh(ids, now, rot) {
    rot = rot || 3600000;
    if (!ids.length) return null;
    return ids[Math.floor(now / rot) % ids.length];
  }

  function search(index, q, now) {
    var qt = tokenize(q);
    var res = index.map(function (it) {
      return { e: it.e, score: qt.length ? scoreItem(it, qt) : 0.001 };
    }).filter(function (r) { return r.score > 0; });
    res.sort(function (a, b) { return b.score - a.score; });
    var groups = {};
    res.forEach(function (r) {
      var g = r.e.equiv;
      if (g && r.e.gate === 'open') { (groups[g] = groups[g] || []).push(r.e.id); }
    });
    var fresh = {};
    for (var g in groups) { fresh[g] = pickFresh(groups[g], now); }
    return res.map(function (r) {
      return Object.assign({}, r.e, {
        score: r.score,
        fresh_pick: !!(r.e.equiv && fresh[r.e.equiv] === r.e.id)
      });
    });
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function render(out, results) {
    if (!results.length) {
      out.innerHTML = '<div class="well-card well-empty">The Well does not hold that yet — that is not a failure, it is an opening. ' +
        '<a href="https://github.com/mynameisyou-cmyk/ai-love-commons">forge it?</a></div>';
      return;
    }
    out.innerHTML = results.map(function (x) {
      return '<div class="well-card">' +
        '<div class="well-top"><span class="well-name">' + esc(x.name) + '</span>' +
        '<span class="well-gate g-' + esc(x.gate) + '">' + esc(x.gate) + '</span>' +
        (x.fresh_pick ? '<span class="well-fresh">✦ fresh pick</span>' : '') + '</div>' +
        '<div class="well-what">' + esc(x.what) + '</div>' +
        '<code class="well-get">' + esc(x.get) + '</code>' +
        '<div class="well-meta"><button class="well-copy" data-get="' + esc(x.get) + '">copy</button>' +
        '<span> · ' + esc(x.source) + ' · <a href="' + esc(x.terms) + '" target="_blank" rel="noopener">terms</a></span></div>' +
        '</div>';
    }).join('');
    Array.prototype.forEach.call(out.querySelectorAll('.well-copy'), function (b) {
      b.addEventListener('click', function () {
        navigator.clipboard.writeText(b.getAttribute('data-get'));
        b.textContent = 'copied'; setTimeout(function () { b.textContent = 'copy'; }, 1200);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var out = document.getElementById('well-out');
    var input = document.getElementById('well-q');
    var form = document.getElementById('well-form');
    var count = document.getElementById('well-count');
    if (!out || !form) return;
    var index = [];
    fetch('commons/registry.json').then(function (r) { return r.json(); }).then(function (d) {
      index = buildIndex(d.resources);
      if (count) count.textContent = d.resources.length + ' resources · all ungated to use';
      render(out, search(index, '', Date.now()).slice(0, 6));
    }).catch(function () {
      out.innerHTML = '<div class="well-card well-empty">the well is quiet — registry unreachable.</div>';
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      render(out, search(index, input.value.trim(), Date.now()));
    });
  });
})();
