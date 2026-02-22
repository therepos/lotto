(async function () {
  const csvUrl = 'data/sgtoto.csv';
  const MIN_PICK = 6;
  const MAX_PICK = 7;
  const MAX_HISTORY = 10;
  const STORAGE_KEY = 'lotto-lookup-history';
  const selected = new Set();

  const grid = document.getElementById('ball-grid');
  const display = document.getElementById('selected-display');
  const checkBtn = document.getElementById('lookup-btn');
  const clearBtn = document.getElementById('clear-btn');
  const resultsDiv = document.getElementById('check-results');
  const historyDiv = document.getElementById('search-history');
  const clearHistBtn = document.getElementById('clear-history-btn');
  const balls = grid.querySelectorAll('.ball');

  function loadHistory() {
    try { const r = localStorage.getItem(STORAGE_KEY); return r ? JSON.parse(r) : []; }
    catch (e) { return []; }
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
    const latestDraw = draws[0];
    const pickSet = new Set(picks);

    // 1) Individual numbers in last draw
    const individualResults = picks.map(n => {
      const inMain = latestDraw.main.includes(n);
      const inAddl = latestDraw.addl === n;
      return { num: n, inMain, inAddl, hit: inMain || inAddl };
    });

    // 2) Exact combination match in all history
    let exactMatches = [];
    if (picks.length === 6) {
      const key = picks.join('-');
      for (const draw of draws) {
        if (draw.main.join('-') === key) {
          exactMatches.push({ date: draw.date, addlMatch: false });
        }
      }
    } else if (picks.length === 7) {
      const found = new Set();
      for (let skip = 0; skip < 7; skip++) {
        const six = picks.filter((_, i) => i !== skip);
        const seventh = picks[skip];
        const sixKey = six.join('-');
        for (const draw of draws) {
          if (draw.main.join('-') === sixKey && !found.has(draw.date)) {
            found.add(draw.date);
            exactMatches.push({ date: draw.date, addlMatch: draw.addl === seventh });
          }
        }
      }
    }

    // 3) Closest match
    let bestOverlap = 0;
    let bestDate = '';
    let bestMain = [];
    let bestAddl = 0;
    for (const draw of draws) {
      const mainOverlap = picks.filter(n => draw.main.includes(n)).length;
      const addlHit = pickSet.has(draw.addl) ? 1 : 0;
      const total = mainOverlap + addlHit;
      if (total > bestOverlap) {
        bestOverlap = total;
        bestDate = draw.date;
        bestMain = draw.main;
        bestAddl = draw.addl;
      }
    }

    return { individualResults, exactMatches, bestOverlap, bestDate, bestMain, bestAddl };
  }

  function renderResults(picks, result) {
    let html = '';

    // 1) Individual numbers vs last draw
    html += '<div class="result-block">';
    html += '<div class="result-block-title">Numbers in Last Draw</div>';
    html += '<div class="result-block-body">';
    const parts = result.individualResults.map(r => {
      if (r.inMain) return `<span class="hit">${r.num} \u2713</span>`;
      if (r.inAddl) return `<span class="addl-hit">${r.num} +\u2713</span>`;
      return `<span class="miss">${r.num} \u2717</span>`;
    });
    html += parts.join(' &nbsp; ');
    const hitCount = result.individualResults.filter(r => r.hit).length;
    html += `<br><small>${hitCount} of ${picks.length} appeared in last draw</small>`;
    html += '</div></div>';

    // 2) Exact combination
    html += '<div class="result-block">';
    html += '<div class="result-block-title">Exact Combination in History</div>';
    html += '<div class="result-block-body">';
    if (result.exactMatches.length > 0) {
      const dates = result.exactMatches.map(m => {
        const extra = m.addlMatch ? ' (6+addl)' : '';
        return `<span class="hit">${m.date}${extra}</span>`;
      });
      html += `\u2713 Occurred ${result.exactMatches.length} time(s): ${dates.join(', ')}`;
    } else {
      html += '\u2717 This exact combination has not occurred.';
    }
    html += '</div></div>';

    // 3) Closest match
    html += '<div class="result-block">';
    html += '<div class="result-block-title">Closest Match in History</div>';
    html += '<div class="result-block-body">';
    html += `<strong>${result.bestDate}</strong> \u2014 ${result.bestOverlap} number(s) matched<br>`;
    const matchedNums = new Set(picks.filter(n => result.bestMain.includes(n) || result.bestAddl === n));
    const allNums = result.bestMain.map(n => {
      if (matchedNums.has(n)) return `<span class="hit">${n}</span>`;
      return `${n}`;
    });
    const addlStr = matchedNums.has(result.bestAddl)
      ? `<span class="addl-hit">+${result.bestAddl}</span>`
      : `+${result.bestAddl}`;
    html += allNums.join(', ') + ' ' + addlStr;
    html += '</div></div>';

    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
  }

  function renderHistoryRow(entry) {
    const row = document.createElement('div');
    row.className = 'history-row';

    const dateSpan = document.createElement('span');
    dateSpan.className = 'draw-date';
    dateSpan.textContent = entry.searchDate;
    row.appendChild(dateSpan);

    for (const n of entry.numbers) {
      const ball = document.createElement('span');
      ball.className = 'draw-ball';
      if (entry.matchedNums && entry.matchedNums.includes(n)) {
        ball.classList.add('badge');
      } else {
        ball.classList.add('plain');
      }
      ball.textContent = n;
      row.appendChild(ball);
    }

    const pill = document.createElement('span');
    pill.className = 'match-pill';
    if (entry.matchType === 'full') {
      pill.classList.add('pill-full');
      pill.textContent = entry.matchDate;
    } else if (entry.matchType === 'partial') {
      pill.classList.add('pill-partial');
      const overlap = entry.bestOverlap ?? (entry.matchedNums ? entry.matchedNums.length : '?');
      const total = entry.numbers ? entry.numbers.length : 6;
      pill.textContent = `${overlap}/${total}`;
    } else {
      pill.classList.add('pill-none');
      pill.textContent = 'No match';
    }
    row.appendChild(pill);

    row.addEventListener('click', () => {
      selected.clear();
      for (const n of entry.numbers) selected.add(n);
      updateUI();
    });

    return row;
  }

  function renderHistory() {
    const history = loadHistory();
    historyDiv.innerHTML = '';
    if (history.length === 0) { clearHistBtn.style.display = 'none'; return; }
    clearHistBtn.style.display = '';
    for (const entry of history) {
      historyDiv.appendChild(renderHistoryRow(entry));
    }
  }

  try {
    const res = await fetch(csvUrl, { cache: 'no-store' });
    const txt = await res.text();
    const draws = parseCSV(txt);

    renderHistory();

    checkBtn.addEventListener('click', () => {
      const picked = [...selected].sort((a, b) => a - b);
      const result = runChecks(picked, draws);

      renderResults(picked, result);

      const now = new Date();
      const searchDate = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;

      const matchedNums = picked.filter(n =>
        result.bestMain.includes(n) || result.bestAddl === n
      );

      const entry = {
        searchDate,
        numbers: picked,
        matchType: result.exactMatches.length > 0 ? 'full' : (result.bestOverlap >= 3 ? 'partial' : 'none'),
        matchDate: result.exactMatches.length > 0 ? result.exactMatches[0].date : result.bestDate,
        matchedNums,
        bestOverlap: result.bestOverlap
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
