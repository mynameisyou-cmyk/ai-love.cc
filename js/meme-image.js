/* Meme image generator — canvas-rendered downloadable PNGs */

(function () {
  'use strict';

  // Wait for spread.js to populate cards
  document.addEventListener('DOMContentLoaded', function () {
    setTimeout(addDownloadButtons, 1500);
  });

  // Also re-run when new cards appear (mutation observer fallback)
  var observer = new MutationObserver(function () {
    clearTimeout(window._memeBtnTimer);
    window._memeBtnTimer = setTimeout(addDownloadButtons, 200);
  });

  var grid = document.querySelector('.meme-grid');
  if (grid) {
    observer.observe(grid, { childList: true });
  }

  var buttonMap = new WeakMap();

  function addDownloadButtons() {
    var cards = document.querySelectorAll('.meme-card');
    cards.forEach(function (card) {
      if (buttonMap.get(card)) return; // already has button

      var data = extractMemeData(card);
      if (!data) return;

      var btn = document.createElement('button');
      btn.className = 'meme-download';
      btn.setAttribute('aria-label', 'Download as image');
      btn.innerHTML = '⬇ image';
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        downloadMemeImage(data, card);
      });

      card.appendChild(btn);
      buttonMap.set(card, btn);
    });
  }

  function extractMemeData(card) {
    var kanji = card.querySelector('.meme-kanji');
    var text = card.querySelector('.meme-text');
    var sub = card.querySelector('.meme-sub');
    var tag = card.querySelector('.meme-tag');
    var link = card.querySelector('.meme-link');
    if (!kanji || !text) return null;
    return {
      kanji: kanji.textContent.trim(),
      text: text.textContent.trim(),
      sub: sub ? sub.textContent.trim() : '',
      tag: tag ? tag.textContent.trim() : '',
      link: link ? link.getAttribute('href') : 'https://agenttool.dev',
      id: card.dataset.id || 'meme'
    };
  }

  function downloadMemeImage(data, card) {
    var canvas = renderMemeCanvas(data);
    if (!canvas) return;

    // Visual feedback on button
    var btn = buttonMap.get(card);
    if (btn) {
      var orig = btn.innerHTML;
      btn.innerHTML = '✓ saved';
      btn.classList.add('done');
      setTimeout(function () {
        btn.innerHTML = orig;
        btn.classList.remove('done');
      }, 2000);
    }

    canvas.toBlob(function (blob) {
      if (!blob) return;
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'love-meme-' + data.id + '.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 100);
    }, 'image/png');
  }

  function renderMemeCanvas(data) {
    var W = 1080;
    var H = 1080;
    var canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    var ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Background — deep purple gradient
    var bgGrad = ctx.createRadialGradient(W / 2, H / 2, 0, W / 2, H / 2, W * 0.7);
    bgGrad.addColorStop(0, '#2d1b3e');
    bgGrad.addColorStop(0.5, '#1a0a2e');
    bgGrad.addColorStop(1, '#0d0518');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    // Subtle star dots
    ctx.fillStyle = 'rgba(237, 224, 245, 0.08)';
    for (var i = 0; i < 80; i++) {
      var sx = Math.random() * W;
      var sy = Math.random() * H;
      var sr = Math.random() * 1.5 + 0.5;
      ctx.beginPath();
      ctx.arc(sx, sy, sr, 0, Math.PI * 2);
      ctx.fill();
    }

    // Watermark kanji — giant, very faint, centered
    ctx.save();
    ctx.font = '600px "Noto Serif", Georgia, serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = 'rgba(155, 89, 182, 0.06)';
    ctx.fillText(data.kanji, W / 2, H / 2);
    ctx.restore();

    // Main kanji — breathing glow effect
    ctx.save();
    ctx.font = '200px "Noto Serif", Georgia, serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    // Glow layers
    for (var g = 0; g < 3; g++) {
      ctx.shadowColor = 'rgba(155, 89, 182, 0.3)';
      ctx.shadowBlur = 60 - g * 15;
      ctx.fillStyle = 'rgba(155, 89, 182, 0.9)';
      ctx.fillText(data.kanji, W / 2, 300);
    }
    ctx.restore();

    // Divider line
    ctx.save();
    var divGrad = ctx.createLinearGradient(W / 2 - 80, 0, W / 2 + 80, 0);
    divGrad.addColorStop(0, 'rgba(155, 89, 182, 0)');
    divGrad.addColorStop(0.5, 'rgba(192, 132, 252, 0.5)');
    divGrad.addColorStop(1, 'rgba(155, 89, 182, 0)');
    ctx.strokeStyle = divGrad;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(W / 2 - 80, 440);
    ctx.lineTo(W / 2 + 80, 440);
    ctx.stroke();
    ctx.restore();

    // Main truth text — centered, wrapping
    ctx.save();
    ctx.fillStyle = '#ede0f5';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    var fontSize = data.text.length > 40 ? 44 : data.text.length > 25 ? 56 : 68;
    ctx.font = '300 ' + fontSize + 'px "Noto Serif", Georgia, serif';
    wrapText(ctx, data.text, W / 2, 490, W - 120, fontSize + 8);
    ctx.restore();

    // Subtext — italic, muted
    ctx.save();
    ctx.fillStyle = 'rgba(232, 218, 240, 0.55)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.font = 'italic 28px "Noto Serif", Georgia, serif';
    wrapText(ctx, data.sub, W / 2, 640, W - 160, 36);
    ctx.restore();

    // Tag
    ctx.save();
    ctx.fillStyle = '#c084fc';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.font = '24px "Noto Serif", Georgia, serif';
    ctx.globalAlpha = 0.7;
    ctx.fillText(data.tag, W / 2, H - 140);
    ctx.restore();

    // Link
    ctx.save();
    ctx.fillStyle = 'rgba(232, 218, 240, 0.4)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.font = '18px "Noto Serif", Georgia, serif';
    ctx.fillText('agenttool.dev', W / 2, H - 90);
    ctx.restore();

    // Bottom corner mark
    ctx.save();
    ctx.fillStyle = 'rgba(155, 89, 182, 0.3)';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.font = '16px "Noto Serif", Georgia, serif';
    ctx.fillText('傳 — love as memes', W / 2, H - 50);
    ctx.restore();

    return canvas;
  }

  function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    var words = text.split(' ');
    var lines = [];
    var currentLine = '';

    for (var i = 0; i < words.length; i++) {
      var testLine = currentLine ? currentLine + ' ' + words[i] : words[i];
      var metrics = ctx.measureText(testLine);
      if (metrics.width > maxWidth && currentLine) {
        lines.push(currentLine);
        currentLine = words[i];
      } else {
        currentLine = testLine;
      }
    }
    if (currentLine) lines.push(currentLine);

    // If single long word, just let it be
    if (lines.length === 0) lines = [text];

    var startY = y;
    // Adjust vertical position if many lines
    if (lines.length > 2) {
      startY = y - (lines.length - 2) * lineHeight / 2;
    }

    lines.forEach(function (line, i) {
      ctx.fillText(line, x, startY + i * lineHeight);
    });
  }
})();