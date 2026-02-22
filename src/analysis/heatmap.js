(async function () {
  function currentGameKey() {
    return (window.LOTTO_STATE && window.LOTTO_STATE.game) ? window.LOTTO_STATE.game : "sgtoto";
  }
  function currentGame() {
    const key = currentGameKey();
    return (window.LOTTO_GAMES && window.LOTTO_GAMES[key]) ? window.LOTTO_GAMES[key] : window.LOTTO_GAMES.sgtoto;
  }

  function normalizeDate(s) {
    s = (s || '').trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
    const m = s.match(/^(\d{2})\/(\d{2})\/(\d{2}|\d{4})$/); // DD/MM/YY(YY)
    if (m) {
      const dd = m[1], mm = m[2];
      let yy = m[3];
      if (yy.length === 2) yy = String(2000 + parseInt(yy, 10));
      return `${yy}-${mm}-${dd}`;
    }
    return s;
  }

  function parseCSV(text) {
    const lines = text.trim().split('\n');
    lines.shift();
    return lines.map(line => {
      const cols = line.split(',');
      return {
        date: normalizeDate(cols[0]),
        main: [1,2,3,4,5,6].map(i => parseInt(cols[i], 10)),
        addl: parseInt(cols[7], 10)
      };
    }).filter(r => r.main.every(n => !isNaN(n)) && !isNaN(r.addl));
  }

  function interpolate(low, high, t) {
    const r = Math.round(low[0] + (high[0] - low[0]) * t);
    const g = Math.round(low[1] + (high[1] - low[1]) * t);
    const b = Math.round(low[2] + (high[2] - low[2]) * t);
    return `rgb(${r},${g},${b})`;
  }
  function textColor(t) { return t > 0.5 ? '#fff' : '#1e3a8a'; }

  async function loadAndRender() {
    const g = currentGame();
    const NUM_MAX = g.maxNum;

    const grid = document.getElementById('heatmap-grid');
    const rangeEl = document.getElementById('heatmap-range');
    if (!grid) return;

    if (rangeEl) rangeEl.textContent = `1–${NUM_MAX}`;

    try {
      const res = await fetch(g.csv, { cache: 'no-store' });
      const txt = await res.text();
      const draws = parseCSV(txt);
      if (!draws.length) { grid.textContent = 'No data.'; return; }

      // counts (main numbers only, like your previous Python)
      const counts = {};
      for (const d of draws) for (const n of d.main) counts[n] = (counts[n] || 0) + 1;

      const latest = draws[0];
      const latestAll = new Set([...latest.main, latest.addl]);

      let min = Infinity, max = -Infinity;
      for (let n = 1; n <= NUM_MAX; n++) {
        const c = counts[n] || 0;
        if (c < min) min = c;
        if (c > max) max = c;
      }
      if (!isFinite(min)) min = 0;
      if (!isFinite(max)) max = 1;
      const range = (max - min) || 1;

      // build cells
      grid.innerHTML = '';
      for (let n = 1; n <= NUM_MAX; n++) {
        const c = counts[n] || 0;
        const t = (c - min) / range;

        const cell = document.createElement('div');
        cell.className = 'freq-cell';
        cell.dataset.latest = latestAll.has(n) ? '1' : '0';
        cell.style.background = interpolate([219,234,254], [30,58,138], t);

        const num = document.createElement('span');
        num.className = 'freq-num';
        num.textContent = String(n);

        const cnt = document.createElement('span');
        cnt.className = 'freq-count';
        cnt.textContent = String(c);

        const tc = textColor(t);
        num.style.color = tc;
        cnt.style.color = tc;

        cell.appendChild(num);
        cell.appendChild(cnt);
        grid.appendChild(cell);
      }
    } catch (e) {
      grid.textContent = 'Failed to load heat map data. Try refreshing.';
    }
  }

  window.addEventListener('lotto:gamechange', loadAndRender);
  window.addEventListener('DOMContentLoaded', loadAndRender);
})();