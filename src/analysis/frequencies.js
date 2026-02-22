(function () {
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
    const m = s.match(/^(\d{2})\/(\d{2})\/(\d{2}|\d{4})$/);
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

  function interpolate(t) {
    const LOW = [219, 234, 254];
    const HIGH = [30, 58, 138];
    const r = Math.round(LOW[0] + (HIGH[0] - LOW[0]) * t);
    const g = Math.round(LOW[1] + (HIGH[1] - LOW[1]) * t);
    const b = Math.round(LOW[2] + (HIGH[2] - LOW[2]) * t);
    return `rgb(${r},${g},${b})`;
  }

  async function loadAndRender() {
    const g = currentGame();
    const NUM_MAX = g.maxNum;

    const barsDiv = document.getElementById('freq-bars');
    const sortBtns = document.querySelectorAll('#freq-bar-controls button');
    if (!barsDiv || !sortBtns.length) return;

    try {
      const res = await fetch(g.csv, { cache: 'no-store' });
      const txt = await res.text();
      const draws = parseCSV(txt);
      if (!draws.length) { barsDiv.textContent = 'No data.'; return; }

      // counts (main numbers only, like your previous Python)
      const counts = {};
      for (const d of draws) for (const n of d.main) counts[n] = (counts[n] || 0) + 1;

      const latest = draws[0];
      const latestAll = new Set([...latest.main, latest.addl]);

      const data = [];
      for (let n = 1; n <= NUM_MAX; n++) {
        data.push({ num: n, count: counts[n] || 0, latest: latestAll.has(n) ? 1 : 0 });
      }

      const maxCount = Math.max(...data.map(d => d.count), 0);
      const minCount = Math.min(...data.map(d => d.count), 0);
      const range = (maxCount - minCount) || 1;

      let currentSort = 'number';

      function renderBars(sortBy) {
        const sorted = [...data];
        if (sortBy === 'frequency') sorted.sort((a, b) => b.count - a.count || a.num - b.num);
        else sorted.sort((a, b) => a.num - b.num);

        let html = '';
        for (const d of sorted) {
          const pct = maxCount > 0 ? (d.count / maxCount * 100) : 0;
          const t = (d.count - minCount) / range;
          const color = interpolate(t);
          const fillCls = d.latest ? 'bar-fill has-marker' : 'bar-fill';

          html += `<div class="bar-row">`;
          html += `<span class="bar-label">${d.num}</span>`;
          html += `<div class="bar-track">`;
          html += `<div class="${fillCls}" style="width:${pct}%;background:${color}"></div>`;
          if (d.latest) html += `<div class="bar-latest-marker"></div>`;
          html += `</div>`;
          html += `<span class="bar-count">${d.count}</span>`;
          html += `</div>`;
        }
        barsDiv.innerHTML = html;
      }

      sortBtns.forEach(btn => {
        btn.onclick = () => {
          sortBtns.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentSort = btn.dataset.sort;
          renderBars(currentSort);
        };
      });

      // keep existing active button state if present
      const active = [...sortBtns].find(b => b.classList.contains('active'));
      currentSort = active ? active.dataset.sort : 'number';
      renderBars(currentSort);

    } catch (e) {
      barsDiv.textContent = 'Failed to load frequency data. Try refreshing.';
    }
  }

  window.addEventListener('lotto:gamechange', loadAndRender);
  window.addEventListener('DOMContentLoaded', loadAndRender);
})();