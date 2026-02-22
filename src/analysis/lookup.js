(async function () {
  const csvUrl = 'data/sgtoto.csv';
  const MIN_PICK = 6;
  const MAX_PICK = 7;
  const MAX_HISTORY = 10;
  const STORAGE_KEY = 'lotto-lookup-history-v2';
  const selected = new Set();

  const grid = document.getElementById('ball-grid');
  const display = document.getElementById('selected-display');
  const checkBtn = document.getElementById('lookup-btn');
  const clearBtn = document.getElementById('clear-btn');
  const resultsDiv = document.getElementById('check-results');
  const historyDiv = document.getElementById('search-history');
  const clearHistBtn = document.getElementById('clear-history-btn');
  const balls = grid.querySelectorAll('.ball');

  // Clear old v1 history
  try { localStorage.removeItem('lotto-lookup-history'); } catch(e) {}

  function loadHistory() {
    try {
      const r = localStorage.getItem(STORAGE_KEY);
      if (!r) return [];
      const parsed = JSON.parse(r);
      // Validate entries — only keep well-formed v2 entries
      return parsed.filter(e =>
        e && e.searchDate && Array.isArray(e.numbers) && e.numbers.length >= 6
      );
    } catch (e) { return []; }
  }
  function saveHistory(h) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(h)); } catch (e) {}
  }
  function clearHistoryData() {
    try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
  }

  function parseCSV(text) {
    const lines = text.trim().split('\n');
    lines.shift();
    return lines.map(line => {
      const cols = line.split(',');
      return {
        date: cols[0].trim(),
        main: [1,2,3,4,5,6].map(i => parseInt(cols[i], 10)).sort((a,b) => a - b),
        addl: parseInt(cols[7], 10)
      };
    }).filter(r => r.main.every(n => !isNaN(n)) && !isNaN(r.addl));
  }

  function updateUI() {
    const count = selected.size;
    balls.forEach(b => {
      const num = parseInt(b.dataset.num, 10);
      if (selected.has(num)) {
        b.classList.add('selected');
        b.classList.remove('disabled');
      } else {
        b.classList.remove('selected');
        if (count >= MAX_PICK) b.classList.add('disabled');
        else b.classList.remove('disabled');
      }
    });
    if (count === 0) {
      display.textContent = 'Selected: none';
    } else {
      const sorted = [...selected].sort((a, b) => a - b);
      const remaining = MIN_PICK - count;
      let hint = '';
      if (remaining > 0) hint = ` (pick ${remaining} more)`;
      else if (count < MAX_PICK) hint = ' (or pick 1 more for 7-number check)';
      display.textContent = 'Selected: ' + sorted.join(', ') + hint;
    }
    checkBtn.disabled = count < MIN_PICK;
  }

  grid.addEventListener('click', e => {
    const ball = e.target.closest('.ball');
    if (!ball) return;
    const num = parseInt(ball.dataset.num, 10);
    if (selected.has(num)) selected.delete(num);
    else if (selected.size < MAX_PICK) selected.add(num);
    updateUI();
  });

  clearBtn.addEventListener('click', () => { selected.clear(); updateUI(); resultsDiv.style.display = 'none'; });
  clearHistBtn.addEventListener('click', () => { clearHistoryData(); renderHistory(); });

  function runChecks(picks, draws) {
    // Numbers from the draw before the latest (the "previous draw")
    const prevDraw = draws.length > 1 ? draws[1] : null;
    const prevDrawNums = prevDraw
      ? new Set([...prevDraw.main, prevDraw.addl])
      : new Set();

    // Check if exact 6-number combination exists in all history
    let comboFoundDate = '';
    if (picks.length === 6) {
      const key = picks.join('-');
      for (const draw of draws) {
        if (draw.main.join('-') === key) {
          comboFoundDate = draw.date;
          break;
        }
      }
    } else if (picks.length === 7) {
      for (let skip = 0; skip < 7; skip++) {
        const six = picks.filter((_, i) => i !== skip).sort((a,b) => a - b);
        const key = six.join('-');
        for (const draw of draws) {
          if (draw.main.join('-') === key) {
            comboFoundDate = draw.date;
            break;
          }
        }
        if (comboFoundDate) break;
      }
    }

    // Numbers that appeared in previous draw
    const inPrevDraw = picks.filter(n => prevDrawNums.has(n));

    return { prevDrawNums, inPrevDraw, comboFoundDate };
  }

  function renderResults(picks, result) {
    let html = '';

    html += '<div class="result-block">';
    html += '<div class="result-block-title">Numbers in Previous Draw</div>';
    html += '<div class="result-block-body">';
    const parts = picks.map(n => {
      if (result.prevDrawNums.has(n)) return `<span class="hit">${n} ✓</span>`;
      return `<span class="miss">${n} ✗</span>`;
    });
    html += parts.join(' &nbsp; ');
    html += `<br><small>${result.inPrevDraw.length} of ${picks.length} appeared in previous draw</small>`;
    html += '</div></div>';

    html += '<div class="result-block">';
    html += '<div class="result-block-title">Combination in History</div>';
    html += '<div class="result-block-body">';
    if (result.comboFoundDate) {
      html += `<span class="hit">✓ Found on ${result.comboFoundDate}</span>`;
    } else {
      html += '✗ This exact combination has not occurred.';
    }
    html += '</div></div>';

    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
  }

  function createComboRow(entry) {
    // Guard against malformed entries
    if (!entry || !entry.searchDate || !Array.isArray(entry.numbers)) {
      return document.createElement('div');
    }

    const container = document.createElement('div');
    container.className = 'history-entry';

    const row = document.createElement('div');
    row.className = 'combo-row';

    // Dates column
    const dates = document.createElement('div');
    dates.className = 'combo-dates';

    const searchDateEl = document.createElement('span');
    searchDateEl.className = 'search-date';
    searchDateEl.textContent = entry.searchDate;
    dates.appendChild(searchDateEl);

    if (entry.comboFoundDate) {
      const foundDateEl = document.createElement('span');
      foundDateEl.className = 'found-date';
      foundDateEl.textContent = entry.comboFoundDate;
      dates.appendChild(foundDateEl);
    } else {
      const notFoundEl = document.createElement('span');
      notFoundEl.className = 'not-found';
      notFoundEl.textContent = 'Not Found';
      dates.appendChild(notFoundEl);
    }

    row.appendChild(dates);

    // Balls
    const ballsDiv = document.createElement('div');
    ballsDiv.className = 'combo-balls';

    const prevSet = new Set(entry.inPrevDraw || []);

    for (const n of entry.numbers) {
      const ball = document.createElement('span');
      ball.className = 'combo-ball';
      if (prevSet.has(n)) {
        ball.classList.add('hit-prev');
      }
      if (entry.comboFoundDate) {
        ball.classList.add('combo-found');
      }
      ball.textContent = n;
      ballsDiv.appendChild(ball);
    }

    // Pad empty slots to 7
    for (let i = entry.numbers.length; i < 7; i++) {
      const empty = document.createElement('span');
      empty.className = 'combo-ball empty';
      ballsDiv.appendChild(empty);
    }

    row.appendChild(ballsDiv);
    container.appendChild(row);

    container.addEventListener('click', () => {
      selected.clear();
      for (const n of entry.numbers) selected.add(n);
      updateUI();
    });

    return container;
  }

  function renderHistory() {
    const history = loadHistory();
    historyDiv.innerHTML = '';
    if (history.length === 0) { clearHistBtn.style.display = 'none'; return; }
    clearHistBtn.style.display = '';
    for (const entry of history) {
      historyDiv.appendChild(createComboRow(entry));
    }
  }

  try {
    const res = await fetch(csvUrl, { cache: 'no-store' });
    const txt = await res.text();
    const draws = parseCSV(txt);

    // Apply combo-found styling to latest draw row if applicable
    const latestRow = document.getElementById('latest-draw-row');
    if (latestRow) {
      const foundDateEl = latestRow.querySelector('.found-date');
      if (foundDateEl) {
        latestRow.querySelectorAll('.combo-ball:not(.empty)').forEach(b => {
          b.classList.add('combo-found');
        });
      }
    }

    renderHistory();

    checkBtn.addEventListener('click', () => {
      const picked = [...selected].sort((a, b) => a - b);
      const result = runChecks(picked, draws);

      renderResults(picked, result);

      const now = new Date();
      const searchDate = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;

      const entry = {
        searchDate,
        numbers: picked,
        inPrevDraw: result.inPrevDraw,
        comboFoundDate: result.comboFoundDate
      };

      const history = loadHistory();
      history.unshift(entry);
      if (history.length > MAX_HISTORY) history.pop();
      saveHistory(history);
      renderHistory();
    });
  } catch (e) {
    historyDiv.textContent = 'Failed to load data. Try refreshing.';
  }
})();
