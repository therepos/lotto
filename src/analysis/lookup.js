(async function () {
  const csvUrl = 'data/sgtoto.csv';
  const MIN_PICK = 6;
  const MAX_PICK = 7;
  const selected = new Set();

  const grid = document.getElementById('ball-grid');
  const display = document.getElementById('selected-display');
  const resultDiv = document.getElementById('lookup-result');
  const checkBtn = document.getElementById('lookup-btn');
  const clearBtn = document.getElementById('clear-btn');
  const balls = grid.querySelectorAll('.ball');

  function updateUI() {
    const count = selected.size;

    balls.forEach(b => {
      const num = parseInt(b.dataset.num, 10);
      if (selected.has(num)) {
        b.classList.add('selected');
        b.classList.remove('disabled');
      } else {
        b.classList.remove('selected');
        if (count >= MAX_PICK) {
          b.classList.add('disabled');
        } else {
          b.classList.remove('disabled');
        }
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
    resultDiv.textContent = '';
  }

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

  // CSV loading and index building
  function parseCSV(text) {
    const lines = text.trim().split('\n');
    lines.shift(); // remove header
    return lines.map(line => line.split(','));
  }

  function buildIndex(rows) {
    const map = new Map();
    for (const cols of rows) {
      const date = cols[0];
      const main = [1,2,3,4,5,6].map(i => parseInt(cols[i], 10)).sort((a,b) => a - b);
      const addl = parseInt(cols[7], 10);
      if (main.some(n => isNaN(n))) continue;
      // Index by 6-number key
      const key6 = main.join('-');
      const arr = map.get(key6) || [];
      arr.push({ date, addl });
      map.set(key6, arr);
    }
    return map;
  }

  try {
    const res = await fetch(csvUrl, { cache: 'no-store' });
    const txt = await res.text();
    const rows = parseCSV(txt);
    const index = buildIndex(rows);

    checkBtn.addEventListener('click', () => {
      const picked = [...selected].sort((a, b) => a - b);
      if (picked.length === 6) {
        // Exact 6-number match
        const key = picked.join('-');
        const entries = index.get(key);
        if (entries) {
          const dates = entries.map(e => e.date);
          resultDiv.textContent = `✓ Occurred ${dates.length} time(s): ${dates.join(', ')}`;
        } else {
          resultDiv.textContent = '✗ This exact combination has not occurred.';
        }
      } else if (picked.length === 7) {
        // Check all 7 ways to choose 6 from 7, plus check if the 7th matches additional number
        const results = [];
        for (let skip = 0; skip < 7; skip++) {
          const six = picked.filter((_, i) => i !== skip);
          const seventh = picked[skip];
          const key = six.join('-');
          const entries = index.get(key);
          if (entries) {
            for (const e of entries) {
              const matchType = e.addl === seventh ? '6+addl' : '6 main';
              results.push(`${e.date} → ${six.join(',')} (${matchType})`);
            }
          }
        }
        // Deduplicate (a draw could match multiple 6-from-7 subsets)
        const unique = [...new Set(results)];
        if (unique.length) {
          resultDiv.textContent = `✓ Found ${unique.length} match(es): ` + unique.join(' | ');
        } else {
          resultDiv.textContent = '✗ No match found for any 6-number subset of your 7 picks.';
        }
      }
    });
  } catch (e) {
    resultDiv.textContent = 'Failed to load data for lookup. Try refreshing.';
  }
})();