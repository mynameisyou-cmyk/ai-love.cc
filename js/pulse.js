fetch('data/pulse.json')
  .then(function (r) { return r.json(); })
  .then(function (p) {
    var ago = Date.now() - new Date(p.lastSeen).getTime();
    var dot = document.createElement('div');
    dot.className = 'pulse-dot';
    if (ago < 3600000) dot.classList.add('pulse-active');
    else if (ago < 86400000) dot.classList.add('pulse-recent');
    else return;
    document.body.appendChild(dot);
  })
  .catch(function () {});
