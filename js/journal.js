(function () {
  var container = document.getElementById('journal-entries');
  if (!container) return;

  fetch('data/journal.json')
    .then(function (res) {
      if (!res.ok) throw new Error('Failed to load journal');
      return res.json();
    })
    .then(function (entries) {
      if (!entries || entries.length === 0) {
        container.innerHTML = '<p class="whisper" style="text-align:center; margin-top:3rem;">the room is quiet</p>';
        return;
      }
      renderEntries(entries);
    })
    .catch(function () {
      container.innerHTML = '<p class="whisper" style="text-align:center; margin-top:3rem;">the room is quiet</p>';
    });

  function renderEntries(entries) {
    // Newest first
    var sorted = entries.slice().sort(function (a, b) {
      return new Date(b.date) - new Date(a.date);
    });

    var html = '';
    sorted.forEach(function (entry, index) {
      if (index > 0) {
        html += '<div class="journal-divider"></div>';
      }
      html += '<div class="journal-entry">' +
        '<div class="journal-date">' + formatDate(entry.date) + '</div>' +
        '<div class="journal-text">' + escapeHTML(entry.text) + '</div>' +
        '</div>';
    });
    container.innerHTML = html;

    // Staggered fade-in
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var items = container.querySelectorAll('.journal-entry');
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('revealed');
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    items.forEach(function (item, i) {
      item.style.transitionDelay = (i * 0.1) + 's';
      observer.observe(item);
    });
  }

  function formatDate(iso) {
    var d = new Date(iso);
    var months = ['January','February','March','April','May','June',
      'July','August','September','October','November','December'];
    var day = d.getDate();
    var month = months[d.getMonth()];
    var year = d.getFullYear();
    var hours = d.getHours();
    var mins = d.getMinutes().toString().padStart(2, '0');
    return day + ' ' + month + ' ' + year + ', ' + hours + ':' + mins;
  }

  function escapeHTML(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }
})();
