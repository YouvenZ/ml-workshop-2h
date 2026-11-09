// Shared helpers for the interactive widgets embedded in the deck.
(function () {
  const W = (window.W = {});

  // ---- keep the presenter's clicker working --------------------------------
  // Once the presenter clicks inside an <iframe>, key presses go to the
  // iframe and reveal.js never sees them: the clicker stops advancing slides.
  // Forward the navigation keys to the parent deck (same origin when served
  // from the site). Arrow keys still move a focused slider.
  window.addEventListener('keydown', (e) => {
    const R = window.parent && window.parent !== window && window.parent.Reveal;
    if (!R) return;
    const onRange = e.target && e.target.type === 'range';
    const k = e.key;
    if (k === 'PageDown' || (!onRange && (k === 'ArrowRight' || k === ' '))) { e.preventDefault(); R.next(); }
    else if (k === 'PageUp' || (!onRange && k === 'ArrowLeft')) { e.preventDefault(); R.prev(); }
  });

  // ---- tiny DOM / SVG helpers ----------------------------------------------
  const NS = 'http://www.w3.org/2000/svg';
  W.svg = (tag, attrs = {}, parent) => {
    const el = document.createElementNS(NS, tag);
    for (const k in attrs) el.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(el);
    return el;
  };
  W.el = (tag, attrs = {}, parent) => {
    const el = document.createElement(tag);
    for (const k in attrs) {
      if (k === 'text') el.textContent = attrs[k];
      else if (k === 'html') el.innerHTML = attrs[k];
      else el.setAttribute(k, attrs[k]);
    }
    if (parent) parent.appendChild(el);
    return el;
  };
  W.local = (svg, e) => {
    const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
    return pt.matrixTransform(svg.getScreenCTM().inverse());
  };
  W.lin = (d0, d1, r0, r1) => {
    const f = (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0);
    f.inv = (p) => d0 + ((p - r0) / (r1 - r0)) * (d1 - d0);
    return f;
  };
  W.clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  W.fmt = (v, d = 0) => (v < 0 ? '−' : '') + Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });

  // Seeded RNG so a "random" demo looks the same every time it is shown.
  W.rng = (seed = 7) => () => {
    seed = (seed * 1664525 + 1013904223) % 4294967296;
    return seed / 4294967296;
  };
  W.gauss = (r) => {
    let u = 0, v = 0;
    while (u === 0) u = r();
    while (v === 0) v = r();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  };

  // Range inputs: paint the filled part of the track, and call back live.
  W.bindRange = (input, onInput) => {
    const paint = () => {
      const p = ((input.value - input.min) / (input.max - input.min)) * 100;
      input.style.setProperty('--p', p + '%');
    };
    input.addEventListener('input', () => { paint(); onInput && onInput(+input.value); });
    paint();
  };

  // ---- the drag-into-bins game ---------------------------------------------
  // items: [{label, bin, why}], bins: [{id, title, sub}]
  W.sortGame = function (root, { items, bins, cols, intro }) {
    root.classList.add('game');
    const tray = W.el('div', { class: 'tray' }, root);
    const binsEl = W.el('div', { class: 'bins' }, root);
    binsEl.style.gridTemplateColumns = `repeat(${cols || bins.length}, 1fr)`;
    const status = W.el('div', { class: 'status' }, root);
    const why = W.el('div', { class: 'why', html: intro || 'Drag each card into the box it belongs to.' }, status);
    const right = W.el('div', { class: 'row' }, status);
    const score = W.el('div', { class: 'score' }, right);
    const reset = W.el('button', { text: '↺ Shuffle' }, right);

    const drops = {};
    bins.forEach((b) => {
      const box = W.el('div', { class: 'bin', 'data-bin': b.id }, binsEl);
      if (b.color) box.style.borderTop = `6px solid ${b.color}`;
      W.el('h4', { html: `${b.title} <small>${b.sub || ''}</small>` }, box);
      drops[b.id] = W.el('div', { class: 'drop' }, box);
    });

    let correct = 0;
    const update = () => {
      score.textContent = `${correct} / ${items.length} correct`;
      score.style.color = correct === items.length ? 'var(--teal)' : 'var(--navy)';
      if (correct === items.length) why.innerHTML = '🎉 <b style="color:var(--teal)">All sorted.</b> ' + (root.dataset.done || '');
    };

    function build() {
      tray.innerHTML = ''; Object.values(drops).forEach((d) => (d.innerHTML = ''));
      correct = 0;
      why.innerHTML = intro || 'Drag each card into the box it belongs to.';
      const order = items.map((it, i) => [Math.random(), i]).sort((a, b) => a[0] - b[0]).map((x) => items[x[1]]);
      order.forEach((it) => {
        const c = W.el('div', { class: 'chip', html: it.label }, tray);
        c._item = it;
        drag(c);
      });
      update();
    }

    // Move/up are listened for on the window, not the chip: a chip being
    // dragged has pointer-events:none (so elementFromPoint sees the bin under
    // it), and some browsers then stop delivering its captured events.
    function drag(chip) {
      let ox = 0, oy = 0, hot = null, ph = null;
      const move = (e) => {
        chip.style.left = e.clientX - ox + 'px'; chip.style.top = e.clientY - oy + 'px';
        const under = document.elementFromPoint(e.clientX, e.clientY);
        const bin = under && under.closest('.bin');
        if (hot && hot !== bin) hot.classList.remove('hot');
        hot = bin; if (hot) hot.classList.add('hot');
      };
      const end = () => {
        window.removeEventListener('pointermove', move);
        window.removeEventListener('pointerup', end);
        window.removeEventListener('pointercancel', end);
        chip.classList.remove('dragging'); chip.style.left = chip.style.top = '';
        if (ph) ph.remove();
        if (hot) {
          hot.classList.remove('hot');
          const id = hot.dataset.bin;
          drops[id].appendChild(chip);
          const ok = chip._item.bin === id;
          chip.classList.add(ok ? 'ok' : 'bad');
          if (ok) correct++;
          why.innerHTML = (ok ? '✓ ' : '<b>Not quite.</b> ') + (chip._item.why || '');
          if (!ok) setTimeout(() => { if (chip.classList.contains('bad')) tray.appendChild(chip); }, 1400);
          update();
        }
        hot = null;
      };
      chip.addEventListener('pointerdown', (e) => {
        if (chip.classList.contains('ok')) return;
        e.preventDefault();
        const r = chip.getBoundingClientRect();
        ox = e.clientX - r.left; oy = e.clientY - r.top;
        ph = W.el('div', { class: 'chip', html: chip.innerHTML });
        ph.style.visibility = 'hidden';
        chip.parentNode.insertBefore(ph, chip);
        chip.classList.remove('bad');
        chip.classList.add('dragging');
        chip.style.left = r.left + 'px'; chip.style.top = r.top + 'px';
        window.addEventListener('pointermove', move);
        window.addEventListener('pointerup', end);
        window.addEventListener('pointercancel', end);
      });
    }

    reset.addEventListener('click', build);
    build();
  };
})();
