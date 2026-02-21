(async function () {
  // ── User-configurable colors ─────────────────────────
  const MAIN_COLOR   = '#3b82f6';   // blue — main number dot
  const ADDL_COLOR   = '#ef4444';   // red — additional number dot
  const EMPTY_COLOR  = '#ffffff';   // white — not drawn
  const LOW_COLOR    = '#dbeafe';   // light blue — 1 hit (week/month)
  const HIGH_COLOR   = '#1e3a8a';   // dark blue — max hits (week/month)
  const BORDER_COLOR = '#e5e7eb';   // light grey — cell borders
  // ─────────────────────────────────────────────────────

  const csvUrl = 'data/sgtoto.csv';
  const NUM_MIN = 1;
  const NUM_MAX = 49;

  // Parse CSV
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

  // Group helpers
  function weekKey(dateStr) {
    const d = new Date(dateStr);
    // ISO week: find Thursday of that week
    const thu = new Date(d);
    thu.setDate(d.getDate() - ((d.getDay() + 6) % 7) + 3);
    const jan4 = new Date(thu.getFullYear(), 0, 4);
    const weekNum = Math.ceil(((thu - jan4) / 86400000 + jan4.getDay() + 1) / 7);
    // Return label: "Wk {weekNum} '{YY}"
    const wStart = new Date(d);
    wStart.setDate(d.getDate() - ((d.getDay() + 6) % 7));
    const wEnd = new Date(wStart);
    wEnd.setDate(wStart.getDate() + 6);
    const fmt = dt => {
      const mm = String(dt.getMonth() + 1).padStart(2, '0');
      const dd = String(dt.getDate()).padStart(2, '0');
      return `${mm}-${dd}`;
    };
    const yr = wStart.getFullYear().toString().slice(-2);
    return `${fmt(wStart)} to ${fmt(wEnd)} '${yr}`;
  }

  function monthKey(dateStr) {
    const d = new Date(dateStr);
    const months = ['Jan','Feb','Mar','Apr','May','Jun',
                    'Jul','Aug','Sep','Oct','Nov','Dec'];
    return `${months[d.getMonth()]} ${d.getFullYear()}`;
  }

  // Sort key for chronological ordering (newest first)
  function dateSortVal(dateStr) {
    return new Date(dateStr).getTime();
  }

  // Aggregate draws into groups
  function groupDraws(draws, keyFn) {
    const groups = new Map();
    for (const draw of draws) {
      const key = keyFn(draw.date);
      if (!groups.has(key)) {
        groups.set(key, { label: key, sortVal: dateSortVal(draw.date), main: {}, addl: {} });
      }
      const g = groups.get(key);
      // Update sortVal to latest date in group
      const sv = dateSortVal(draw.date);
      if (sv > g.sortVal) g.sortVal = sv;
      for (const n of draw.main) {
        g.main[n] = (g.main[n] || 0) + 1;
      }
      g.addl[draw.addl] = (g.addl[draw.addl] || 0) + 1;
    }
    // Sort newest first
    return [...groups.values()].sort((a, b) => b.sortVal - a.sortVal);
  }

  // Color interpolation for heatmap
  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return [r, g, b];
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
    // Header row
    let hrow = '<tr><th class="row-header">Date</th>';
    for (let n = NUM_MIN; n <= NUM_MAX; n++) hrow += `<th>${n}</th>`;
    hrow += '</tr>';
    thead.innerHTML = hrow;

    // Data rows (already newest first from CSV)
    let html = '';
    for (const draw of draws) {
      html += `<tr><td class="row-label">${draw.date}</td>`;
      for (let n = NUM_MIN; n <= NUM_MAX; n++) {
        const isMain = draw.main.includes(n);
        const isAddl = draw.addl === n;
        if (isMain) {
          html += `<td style="background:${EMPTY_COLOR}"><span class="dot" style="background:${MAIN_COLOR}"></span></td>`;
        } else if (isAddl) {
          html += `<td style="background:${EMPTY_COLOR}"><span class="dot" style="background:${ADDL_COLOR}"></span></td>`;
        } else {
          html += `<td style="background:${EMPTY_COLOR}"></td>`;
        }
      }
      html += '</tr>';
    }
    tbody.innerHTML = html;
  }

  // Render: Grouped (week / month)
  function renderGrouped(groups, thead, tbody, tooltip) {
    // Find max count across all groups for scaling
    let maxCount = 1;
    for (const g of groups) {
      for (let n = NUM_MIN; n <= NUM_MAX; n++) {
        const total = (g.main[n] || 0) + (g.addl[n] || 0);
        if (total > maxCount) maxCount = total;
      }
    }

    // Header
    let hrow = '<tr><th class="row-header">Period</th>';
    for (let n = NUM_MIN; n <= NUM_MAX; n++) hrow += `<th>${n}</th>`;
    hrow += '</tr>';
    thead.innerHTML = hrow;

    // Rows
    let html = '';
    for (const g of groups) {
      html += `<tr><td class="row-label">${g.label}</td>`;
      for (let n = NUM_MIN; n <= NUM_MAX; n++) {
        const mc = g.main[n] || 0;
        const ac = g.addl[n] || 0;
        const total = mc + ac;
        if (total === 0) {
          html += `<td style="background:${EMPTY_COLOR}"></td>`;
        } else {
          const t = Math.min(total / maxCount, 1);
          const bg = interpolateColor(LOW_COLOR, HIGH_COLOR, t);
          html += `<td><div class="heat-cell" style="background:${bg}" data-tip="Number ${n} — ${total} time(s) (${mc} main, ${ac} addl)">${total}</div></td>`;
        }
      }
      html += '</tr>';
    }
    tbody.innerHTML = html;

    // Tooltip handling
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
    const tbody = document.querySelector('#dist-table tbody');
    const tooltip = document.getElementById('dist-tooltip');
    const buttons = document.querySelectorAll('#dist-controls button');

    let currentMode = 'draw';

    function render() {
      tooltip.style.display = 'none';
      // Clone tbody to remove old event listeners
      const newTbody = tbody.cloneNode(false);
      tbody.parentNode.replaceChild(newTbody, tbody);
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

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentMode = btn.dataset.mode;
        render();
      });
    });

    render();
  } catch (e) {
    document.getElementById('dist-table-wrap').textContent =
      'Failed to load distribution data. Try refreshing.';
  }
})();
