(async function () {
  const MAIN_COLOR = '#3b82f6';
  const ADDL_COLOR = '#ef4444';
  const EMPTY_COLOR = '#ffffff';
  const LOW_COLOR = '#dbeafe';
  const HIGH_COLOR = '#1e3a8a';
  const HIGHLIGHT_BG = '#fffde7';

  function currentGameKey() {
    return (window.LOTTO_STATE && window.LOTTO_STATE.game) ? window.LOTTO_STATE.game : "sgtoto";
  }
  function currentGame() {
    const key = currentGameKey();
    return (window.LOTTO_GAMES && window.LOTTO_GAMES[key]) ? window.LOTTO_GAMES[key] : window.LOTTO_GAMES.sgtoto;
  }

  function normalizeDate(s) {
    s = (s || '').trim();
    // already ISO
    if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;

    // DD/MM/YY or DD/MM/YYYY
    const m = s.match(/^(\d{2})\/(\d{2})\/(\d{2}|\d{4})$/);
    if (m) {
      const dd = m[1], mm = m[2];
      let yy = m[3];
      if (yy.length === 2) yy = String(2000 + parseInt(yy, 10)); // 00-99 -> 2000-2099
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
        date: cols[0].trim(),
        main: [1, 2, 3, 4, 5, 6].map(i => parseInt(cols[i], 10)),
        addl: parseInt(cols[7], 10)
      };
    }).filter(r => r.main.every(n => !isNaN(n)) && !isNaN(r.addl));
  }

  function weekKey(dateStr) {
    const d = new Date(dateStr);
    const wStart = new Date(d);
    wStart.setDate(d.getDate() - ((d.getDay() + 6) % 7));
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${wStart.getFullYear()} ${months[wStart.getMonth()]} ${wStart.getDate()}`;
  }

  function monthKey(dateStr) {
    const d = new Date(dateStr);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${d.getFullYear()} ${months[d.getMonth()]}`;
  }

  function dateSortVal(dateStr) { return new Date(dateStr).getTime(); }

  function groupDraws(draws, keyFn) {
    const groups = new Map();
    for (const draw of draws) {
      const key = keyFn(draw.date);
      if (!groups.has(key))
        groups.set(key, { label: key, sortVal: dateSortVal(draw.date), main: {}, addl: {} });
      const g = groups.get(key);
      const sv = dateSortVal(draw.date);
      if (sv > g.sortVal) g.sortVal = sv;
      for (const n of draw.main) g.main[n] = (g.main[n] || 0) + 1;
      g.addl[draw.addl] = (g.addl[draw.addl] || 0) + 1;
    }
    return [...groups.values()].sort((a, b) => b.sortVal - a.sortVal);
  }

  function hexToRgb(hex) {
    return [parseInt(hex.slice(1, 3), 16), parseInt(hex.slice(3, 5), 16), parseInt(hex.slice(5, 7), 16)];
  }
  function interpolateColor(low, high, t) {
    const lo = hexToRgb(low), hi = hexToRgb(high);
    return `rgb(${Math.round(lo[0] + (hi[0] - lo[0]) * t)},${Math.round(lo[1] + (hi[1] - lo[1]) * t)},${Math.round(lo[2] + (hi[2] - lo[2]) * t)})`;
  }

  function renderDraw(draws, thead, tbody, NUM_MIN, NUM_MAX) {
    let hrow = '<tr><th class="row-header">Date</th>';
    for (let n = NUM_MIN; n <= NUM_MAX; n++) hrow += `<th>${n}</th>`;
    hrow += '</tr>';
    thead.innerHTML = hrow;

    let html = '';
    for (let i = 0; i < draws.length; i++) {
      const draw = draws[i];
      const cls = i === 0 ? ' class="latest-row"' : '';
      html += `<tr${cls}><td class="row-label">${draw.date}</td>`;
      for (let n = NUM_MIN; n <= NUM_MAX; n++) {
        const isMain = draw.main.includes(n);
        const isAddl = draw.addl === n;
        const bg = i === 0 ? HIGHLIGHT_BG : EMPTY_COLOR;
        if (isMain) html += `<td style="background:${bg}"><span class="dot" style="background:${MAIN_COLOR}"></span></td>`;
        else if (isAddl) html += `<td style="background:${bg}"><span class="dot" style="background:${ADDL_COLOR}"></span></td>`;
        else html += `<td style="background:${bg}"></td>`;
      }
      html += '</tr>';
    }
    tbody.innerHTML = html;
  }

  function renderGrouped(groups, thead, tbody, tooltip, NUM_MIN, NUM_MAX) {
    let maxCount = 1;
    for (const g of groups)
      for (let n = NUM_MIN; n <= NUM_MAX; n++) {
        const total = (g.main[n] || 0) + (g.addl[n] || 0);
        if (total > maxCount) maxCount = total;
      }

    let hrow = '<tr><th class="row-header">Period</th>';
    for (let n = NUM_MIN; n <= NUM_MAX; n++) hrow += `<th>${n}</th>`;
    hrow += '</tr>';
    thead.innerHTML = hrow;

    let html = '';
    for (let i = 0; i < groups.length; i++) {
      const g = groups[i];
      const cls = i === 0 ? ' class="latest-row"' : '';
      html += `<tr${cls}><td class="row-label">${g.label}</td>`;
      for (let n = NUM_MIN; n <= NUM_MAX; n++) {
        const mc = g.main[n] || 0, ac = g.addl[n] || 0, total = mc + ac;
        if (total === 0) {
          html += `<td style="background:${i === 0 ? HIGHLIGHT_BG : EMPTY_COLOR}"></td>`;
        } else {
          const t = Math.min(total / maxCount, 1);
          const bg = interpolateColor(LOW_COLOR, HIGH_COLOR, t);
          html += `<td><div class="heat-cell" style="background:${bg}" data-tip="Number ${n} — ${total} time(s) (${mc} main, ${ac} addl)">${total}</div></td>`;
        }
      }
      html += '</tr>';
    }
    tbody.innerHTML = html;

    tbody.onmouseover = (e) => {
      const el = e.target.closest('.heat-cell');
      if (!el || !el.dataset.tip) { tooltip.style.display = 'none'; return; }
      tooltip.textContent = el.dataset.tip;
      tooltip.style.display = 'block';
    };
    tbody.onmousemove = (e) => {
      tooltip.style.left = (e.clientX + 12) + 'px';
      tooltip.style.top = (e.clientY - 30) + 'px';
    };
    tbody.onmouseout = (e) => {
      if (!e.target.closest('.heat-cell')) tooltip.style.display = 'none';
    };
  }

  function buildExcelData(draws, currentMode, NUM_MIN, NUM_MAX) {
    const rows = [];
    if (currentMode === 'draw') {
      const header = ['Date'];
      for (let n = NUM_MIN; n <= NUM_MAX; n++) header.push(n);
      rows.push(header);
      for (const draw of draws) {
        const row = [draw.date];
        for (let n = NUM_MIN; n <= NUM_MAX; n++) {
          if (draw.main.includes(n)) row.push('M');
          else if (draw.addl === n) row.push('A');
          else row.push('');
        }
        rows.push(row);
      }
    } else {
      const keyFn = currentMode === 'week' ? weekKey : monthKey;
      const groups = groupDraws(draws, keyFn);
      const header = ['Period'];
      for (let n = NUM_MIN; n <= NUM_MAX; n++) header.push(n);
      rows.push(header);
      for (const g of groups) {
        const row = [g.label];
        for (let n = NUM_MIN; n <= NUM_MAX; n++) {
          const total = (g.main[n] || 0) + (g.addl[n] || 0);
          row.push(total || '');
        }
        rows.push(row);
      }
    }
    return rows;
  }

  async function downloadExcel(draws, currentMode, NUM_MIN, NUM_MAX) {
    if (!window.XLSX) {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
      document.head.appendChild(script);
      await new Promise((resolve, reject) => {
        script.onload = resolve;
        script.onerror = reject;
      });
    }

    const data = buildExcelData(draws, currentMode, NUM_MIN, NUM_MAX);
    const ws = XLSX.utils.aoa_to_sheet(data);

    const cols = [{ wch: 14 }];
    for (let n = NUM_MIN; n <= NUM_MAX; n++) cols.push({ wch: 4 });
    ws['!cols'] = cols;

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Distribution');
    XLSX.writeFile(wb, `distribution_${currentGameKey()}_${currentMode}.xlsx`);
  }

  async function loadAndRender() {
    const g = currentGame();
    const csvUrl = g.csv;
    const NUM_MIN = 1;
    const NUM_MAX = g.maxNum;

    const rangeEl = document.getElementById('dist-range');
    if (rangeEl) rangeEl.textContent = `1–${NUM_MAX}`;

    try {
      const res = await fetch(csvUrl, { cache: 'no-store' });
      const txt = await res.text();
      const draws = parseCSV(txt);

      const thead = document.querySelector('#dist-table thead');
      const tooltip = document.getElementById('dist-tooltip');
      const modeButtons = document.querySelectorAll('#dist-controls button');
      const downloadBtn = document.getElementById('dist-download-btn');

      let currentMode = 'draw';

      function render() {
        tooltip.style.display = 'none';
        const oldTbody = document.querySelector('#dist-table tbody');
        const newTbody = oldTbody.cloneNode(false);
        oldTbody.parentNode.replaceChild(newTbody, oldTbody);
        const tb = document.querySelector('#dist-table tbody');

        if (currentMode === 'draw') renderDraw(draws, thead, tb, NUM_MIN, NUM_MAX);
        else if (currentMode === 'week') renderGrouped(groupDraws(draws, weekKey), thead, tb, tooltip, NUM_MIN, NUM_MAX);
        else renderGrouped(groupDraws(draws, monthKey), thead, tb, tooltip, NUM_MIN, NUM_MAX);
      }

      modeButtons.forEach(btn => {
        btn.onclick = () => {
          modeButtons.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentMode = btn.dataset.mode;
          render();
        };
      });

      if (downloadBtn) {
        downloadBtn.onclick = (e) => {
          e.preventDefault();
          downloadExcel(draws, currentMode, NUM_MIN, NUM_MAX);
        };
      }

      render();
    } catch (e) {
      const wrap = document.getElementById('dist-table-wrap');
      if (wrap) wrap.textContent = 'Failed to load distribution data. Try refreshing.';
    }
  }

  window.addEventListener("lotto:gamechange", () => loadAndRender());
  loadAndRender();
})();