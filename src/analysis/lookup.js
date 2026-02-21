(async function () {
  const csvUrl = 'data/sgtoto.csv';
  const MIN_PICK = 6;
  const MAX_PICK = 7;
  const MATCH_THRESHOLD = 3;
  const MAX_HISTORY = 10;
  const STORAGE_KEY = 'lotto-lookup-history';
  const selected = new Set();

  const grid = document.getElementById('ball-grid');
  const display = document.getElementById('selected-display');
  const checkBtn = document.getElementById('lookup-btn');
  const clearBtn = document.getElementById('clear-btn');
  const historyDiv = document.getElementById('search-history');
  const clearHistBtn = document.getElementById('clear-history-btn');
  const balls = grid.querySelectorAll('.ball');

  // localStorage helpers
  function loadHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistory(history) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) { /* ignore */ }
  }

  function clearHistory() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) { /* ignore */ }
  }

  // CSV parsing & index
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

  // Find best match for a set of numbers against all draws
  function findBestMatch(picks, draws) {
    const pickSet = new Set(picks);
    let bestOverlap = 0;
    let bestDate = '';
    let bestMatchedNums = new Set();
    let isExact = false;

    if (picks.length === 6) {
      const pickKey = [...picks].sort((a,b) => a - b).join('-');
      for (const draw of draws) {
        const drawKey = draw.main.join('-');
        if (drawKey === pickKey) {
          return {
            type: 'full',
            date: draw.date,
            matchedNums: new Set(picks)
          };
        }
        const overlap = picks.filter(n => draw.main.includes(n));
        if (overlap.length > bestOverlap) {
          bestOverlap = overlap.length;
          bestDate = draw.date;
          bestMatchedNums = new Set(overlap);
        }
      }
    } else if (picks.length === 7) {
      // Check all 7 ways to choose 6 from 7
      for (let skip = 0; skip < 7; skip++) {
        const six = picks.filter((_, i) => i !== skip);
        const seventh = picks[skip];
        const sixKey = six.sort((a,b) => a - b).join('-');
        for (const draw of draws) {
          const drawKey = draw.main.join('-');
          if (drawKey === sixKey) {
            const matched = new Set(six);
            if (draw.addl === seventh) matched.add(seventh);
            return {
              type: 'full',
              date: draw.date,
              matchedNums: matched
            };
          }
        }
      }
      // Partial match for 7-number picks
      for (const draw of draws) {
        const overlap = picks.filter(n => draw.main.includes(n) || draw.addl === n);
        if (overlap.length > bestOverlap) {
          bestOverlap = overlap.length;
          bestDate = draw.date;
          bestMatchedNums = new Set(overlap);
        }
      }
    }

    if (bestOverlap >= MATCH_THRESHOLD) {
      return {
        type: 'partial',
        date: bestDate,
        matchedNums: bestMatchedNums
      };
    }

    return { type: 'none', date: '', matchedNums: new Set() };
  }

  // Render a single history row
  function renderHistoryRow(entry) {
    const row = document.createElement('div');
    row.className = 'history-row';

    // Search date
    const dateSpan = document.createElement('span');
    dateSpan.className = 'draw-date';
    dateSpan.textContent = entry.searchDate;
    row.appendChild(dateSpan);

    // Number balls
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

    // Match pill
    const pill = document.createElement('span');
    pill.className = 'match-pill';
    if (entry.matchType === 'full') {
      pill.classList.add('pill-full');
      pill.textContent = entry.matchDate;
    } else if (entry.matchType === 'partial') {
      pill.classList.add('pill-partial');
      pill.textContent = entry.matchDate;
    } else {
      pill.classList.add('pill-none');
      pill.textContent = 'No match';
    }
    row.appendChild(pill);

    // Click to reload numbers
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
    if (history.length === 0) {
      clearHistBtn.style.display = 'none';
      return;
    }
    clearHistBtn.style.display = '';
    for (const entry of history) {
      historyDiv.appendChild(renderHistoryRow(entry));
    }
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
        b.classList.add('disabled', count >= MAX_PICK);
        if (count < MAX_PICK) b.classList.remove('disabled');
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

  // Ball grid click
  grid.addEventListener('click', e => {
    const ball = e.target.closest('.ball');
    if (!ball) return;
    const num = parseInt(ball.dataset.num, 10);
    if (selected.has(num)) {
      selected.delete(num);
    } else if (selected.size < MAX_PICK) {
      selected.add(num);
    }
    updateUI();
  });

  clearBtn.addEventListener('click', () => {
    selected.clear();
    updateUI();
  });

  clearHistBtn.addEventListener('click', () => {
    clearHistory();
    renderHistory();
  });

  // Main
  try {
    const res = await fetch(csvUrl, { cache: 'no-store' });
    const txt = await res.text();
    const draws = parseCSV(txt);

    // Render saved history
    renderHistory();

    checkBtn.addEventListener('click', () => {
      const picked = [...selected].sort((a, b) => a - b);
      const result = findBestMatch(picked, draws);

      // Build search date (today)
      const now = new Date();
      const y = now.getFullYear();
      const m = String(now.getMonth() + 1).padStart(2, '0');
      const d = String(now.getDate()).padStart(2, '0');
      const searchDate = `${y}-${m}-${d}`;

      const entry = {
        searchDate: searchDate,
        numbers: picked,
        matchType: result.type,
        matchDate: result.date,
        matchedNums: [...result.matchedNums]
      };

      // Save to history
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