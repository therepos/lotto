(async function () {
  // ── User-configurable colors ─────────────────────────
  const MAIN_COLOR   = '#3b82f6';
  const ADDL_COLOR   = '#ef4444';
  const EMPTY_COLOR  = '#ffffff';
  const LOW_COLOR    = '#dbeafe';
  const HIGH_COLOR   = '#1e3a8a';
  const HIGHLIGHT_BG = '#fffde7';
  // ─────────────────────────────────────────────────────

  const csvUrl = 'data/sgtoto.csv';
  const NUM_MIN = 1;
  const NUM_MAX = 49;

  function parseCSV(text) {
    const lines = text.trim().split('\n');
    lines.shift();
    return lines.map(line => {
      const cols = line.split(',');
      return {
        date: cols[0].trim(),
        main: [1,2,3,4,5,6].map(i => parseInt(cols[i], 10)),
        addl: parseInt(cols[7], 10)
      };
    }).filter(r => r.main.every(n => !isNaN(n)) && !isNaN(r.addl));
  }

  // Week label: "2026 Feb 16"
  function weekKey(dateStr) {
    const d = new Date(dateStr);
    const wStart = new Date(d);
    wStart.setDate(d.getDate() - ((d.getDay() + 6) % 7));
    const months = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec'];
    return `${wStart.getFullYear()} ${months[wStart.getMonth()]} ${wStart.getDate()}`;
  }

  // Month label: "2026 Feb"
  function monthKey(dateStr) {
    const d = new Date(dateStr);
    const months = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec'];
    return `${d.getFullYear()} ${months[d.getMonth()]}`;
  }

  function dateSortVal(dateStr) {
    return new Date(dateStr).getTime();
  }

  function groupDraws(draws, keyFn) {
    const groups = new Map();
    for (const draw of draws) {
      const key = keyFn(draw.date);
      if (!groups.has(key)) {
        groups.set(key, { label: key, sortVal: dateSortVal(draw.date), main: {}, addl: {} });
      }
      const g = groups.get(key);
      const sv = dateSortVal(draw.date);
      if (sv > g.sortVal) g.sortVal = sv;
      for (const n of draw.main) {
        g.main[n] = (g.main[n] || 0) + 1;
      }
      g.addl[draw.addl] = (g.addl[draw.addl] || 0) + 1;
    }
    return [...groups.values()].sort((a, b) => b.sortVal - a.sortVal);
  }

  function hexToRgb(hex) {
    return [
      parseInt(hex.slice(1, 3), 16),
      parseInt(hex.slice(3, 5), 16),
      parseInt(hex.slice(5, 7), 16)
    ];
  }

  function interpolateColor(low, high, t) {
    const lo = hexToRgb(low);
    const hi = hexToRgb(high);
    const r = Math.round(lo[0] + (hi[0] - lo[0]) * t);
    const g = Math.round(lo[1] + (hi[1] - lo[1]) * t);
    const b = Math.round(lo[2] + (hi[2] - lo[2]) * t);
    return `rgb(${r},${g},${b})`;
  }

  // Render: By Draw
  function renderDraw(draws, thead, tbody) {
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
        if (isMain) {
          html += `<td style="background:${bg}"><span class="dot" style="background:${MAIN_COLOR}"></span></td>`;
        } else if (isAddl) {
          html += `<td style="background:${bg}"><span class="dot" style="background:${ADDL_COLOR}"></span></td>`;
        } else {
          html += `<td style="background:${bg}"></td>`;
        }
      }
      html += '</tr>';
    }
    tbody.innerHTML = html;
  }

  // Render: Grouped (week / month)
  function renderGrouped(groups, thead, tbody, tooltip) {
    let maxCount = 1;
    for (const g of groups) {
      for (let n = NUM_MIN; n <= NUM_MAX; n++) {
        const total = (g.main[n] || 0) + (g.addl[n] || 0);
        if (total > maxCount) maxCount = total;
      }
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
        const mc = g.main[n] || 0;
        const ac = g.addl[n] || 0;
        const total = mc + ac;
        if (total === 0) {
          const bg = i === 0 ? HIGHLIGHT_BG : EMPTY_COLOR;
          html += `<td style="background:${bg}"></td>`;
        } else {
          const t = Math.min(total / maxCount, 1);
          const bg = interpolateColor(LOW_COLOR, HIGH_COLOR, t);
          html += `<td><div class="heat-cell" style="background:${bg}" data-tip="Number ${n} — ${total} time(s) (${mc} main, ${ac} addl)">${total}</div></td>`;
        }
      }
      html += '</tr>';
    }
    tbody.innerHTML = html;

    tbody.addEventListener('mouseover', e => {
      const el = e.target.closest('.heat-cell');
      if (!el || !el.dataset.tip) { tooltip.style.display = 'none'; return; }
      tooltip.textContent = el.dataset.tip;
      tooltip.style.display = 'block';
    });
    tbody.addEventListener('mousemove', e => {
      tooltip.style.left = (e.clientX + 12) + 'px';
      tooltip.style.top = (e.clientY - 30) + 'px';
    });
    tbody.addEventListener('mouseout', e => {
      if (!e.target.closest('.heat-cell')) tooltip.style.display = 'none';
    });
  }

  // Main
  try {
    const res = await fetch(csvUrl, { cache: 'no-store' });
    const txt = await res.text();
    const draws = parseCSV(txt);

    const thead = document.querySelector('#dist-table thead');
    const tooltip = document.getElementById('dist-tooltip');
    const modeButtons = document.querySelectorAll('#dist-controls button');
    const viewButtons = document.querySelectorAll('#dist-view-toggle button');
    const tableWrap = document.getElementById('dist-table-wrap');

    let currentMode = 'draw';
    let currentView = 'compact';

    function render() {
      tooltip.style.display = 'none';

      // Toggle compact/table class
      if (currentView === 'compact') {
        tableWrap.classList.add('compact-mode');
      } else {
        tableWrap.classList.remove('compact-mode');
      }

      const oldTbody = document.querySelector('#dist-table tbody');
      const newTbody = oldTbody.cloneNode(false);
      oldTbody.parentNode.replaceChild(newTbody, oldTbody);
      const tb = document.querySelector('#dist-table tbody');

      if (currentMode === 'draw') {
        renderDraw(draws, thead, tb);
      } else if (currentMode === 'week') {
        const groups = groupDraws(draws, weekKey);
        renderGrouped(groups, thead, tb, tooltip);
      } else {
        const groups = groupDraws(draws, monthKey);
        renderGrouped(groups, thead, tb, tooltip);
      }
    }

    modeButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        modeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.dataset.mode;
        render();
      });
    });

    viewButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        viewButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentView = btn.dataset.view;
        render();
      });
    });

    render();
  } catch (e) {
    document.getElementById('dist-table-wrap').textContent =
      'Failed to load distribution data. Try refreshing.';
  }
})();