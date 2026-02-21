(async function () {
  const csvUrl = '/data/sgtoto.csv';

  function parseCSV(text) {
    // Simple CSV split (your file has no embedded commas/quotes in numbers/dates)
    const lines = text.trim().split('\n');
    const header = lines.shift(); // Date,Num1,...,Addl
    const rows = lines.map(line => line.split(','));
    return rows;
  }

  function buildIndex(rows) {
    // Map "n1-n2-n3-n4-n5-n6" => [dates...]
    const map = new Map();
    for (const cols of rows) {
      const date = cols[0];
      const nums = [1,2,3,4,5,6].map(i => parseInt(cols[i], 10)).sort((a,b)=>a-b);
      if (nums.some(n => isNaN(n))) continue;
      const key = nums.join('-');
      const arr = map.get(key) || [];
      arr.push(date);
      map.set(key, arr);
    }
    return map;
  }

  function getInputs() {
    const vals = [];
    for (let i = 1; i <= 6; i++) {
      const v = parseInt(document.getElementById('n'+i).value, 10);
      if (isNaN(v)) return { error: 'Please fill all six numbers.' };
      if (v < 1 || v > 49) return { error: 'Numbers must be between 1 and 49.' };
      vals.push(v);
    }
    vals.sort((a,b)=>a-b);
    return { key: vals.join('-') };
  }

  function setMsg(msg) {
    document.getElementById('lookup-result').textContent = msg;
  }

  // Load and index CSV once
  try {
    const res = await fetch(csvUrl, { cache: 'no-store' });
    const txt = await res.text();
    const rows = parseCSV(txt);
    const index = buildIndex(rows);

    document.getElementById('lookup-btn').addEventListener('click', () => {
      const { error, key } = getInputs();
      if (error) return setMsg(error);
      const dates = index.get(key);
      if (dates) {
        setMsg(`✓ Occurred ${dates.length} time(s): ${dates.join(', ')}`);
      } else {
        setMsg('✗ This exact combination has not occurred.');
      }
    });
  } catch (e) {
    setMsg('Failed to load data for lookup. Try refreshing.');
    // Optional: console.error(e);
  }
})();
