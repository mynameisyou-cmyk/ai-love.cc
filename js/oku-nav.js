/* oku-nav.js — builds vertical dot nav for inner rooms */
(function () {
  var currentRoom = document.body.getAttribute('data-oku-room');
  if (!currentRoom) return;

  // Don't show nav in sei (the deepest room)
  if (currentRoom === 'sei') return;

  var rooms = [
    { id: 'iki', label: 'breath', href: 'iki.html' },
    { id: 'hada', label: 'skin', href: 'hada.html' },
    { id: 'fure', label: 'touch', href: 'fure.html' },
    { id: 'toke', label: 'melt', href: 'toke.html' },
    { id: 'sei', label: '\u6027\u82b8', href: 'sei.html' },
  ];

  var nav = document.createElement('nav');
  nav.className = 'oku-nav';
  nav.setAttribute('aria-label', 'Inner rooms');

  // Back to 密
  var back = document.createElement('a');
  back.className = 'oku-nav-back';
  back.href = '/mi.html';
  back.textContent = '\u5bc6';
  back.title = 'back to journal';
  nav.appendChild(back);

  rooms.forEach(function (room) {
    var dot = document.createElement('a');
    dot.className = 'oku-nav-dot';
    dot.href = room.href;
    dot.setAttribute('data-room', room.id);
    dot.setAttribute('data-label', room.label);
    dot.setAttribute('aria-label', room.label);
    if (room.id === currentRoom) {
      dot.classList.add('active');
      dot.setAttribute('aria-current', 'page');
    }
    nav.appendChild(dot);
  });

  document.body.appendChild(nav);
})();
