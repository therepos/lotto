(async function () {
  const csvUrl = 'data/sgtoto.csv';
  const MAX_PICK = 6;
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
      display.textContent = 'Selected: ' + sorted.join(', ') + (count < MAX_PICK ? ` (pick ${MAX_PICK - count} more)` : '');
    }

    checkBtn.disabled = count !== MAX_PICK;
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
      const nums = [1,2,3,4,5,6].map(i => parseInt(cols[i], 10)).sort((a,b) => a - b);
      if (nums.some(n => isNaN(n))) continue;
      const key = nums.join('-');
      const arr = map.get(key) || [];
      arr.push(date);
      map.set(key, arr);
    }
    return map;
  }

  try {
    const res = await fetch(csvUrl, { cache: 'no-store' });
    const txt = await res.text();
    const rows = parseCSV(txt);
    const index = buildIndex(rows);

    checkBtn.addEventListener('click', () => {
      if (selected.size !== MAX_PICK) return;
      const key = [...selected].sort((a, b) => a - b).join('-');
      const dates = index.get(key);
      if (dates) {
        resultDiv.textContent = `✓ Occurred ${dates.length} time(s): ${dates.join(', ')}`;
      } else {
        resultDiv.textContent = '✗ This exact combination has not occurred.';
      }
    });
  } catch (e) {
    resultDiv.textContent = 'Failed to load data for lookup. Try refreshing.';
  }
})();