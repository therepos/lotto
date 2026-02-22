(function () {
  const MAX_HISTORY = 10;

  function currentGameKey() {
    return (window.LOTTO_STATE && window.LOTTO_STATE.game) ? window.LOTTO_STATE.game : "sgtoto";
  }
  function currentGame() {
    const key = currentGameKey();
    return (window.LOTTO_GAMES && window.LOTTO_GAMES[key]) ? window.LOTTO_GAMES[key] : window.LOTTO_GAMES.sgtoto;
  }
  function storageKeyForGame(gameKey) {
    return `lotto-lookup-history-${gameKey}-v1`;
  }

  function parseCSV(text) {
    const lines = text.trim().split("\n");
    lines.shift(); // header
    return lines.map(line => {
      const cols = line.split(",");
      return {
        date: cols[0].trim(),
        main: [1,2,3,4,5,6].map(i => parseInt(cols[i], 10)).sort((a,b) => a - b),
        addl: parseInt(cols[7], 10)
      };
    }).filter(r => r.main.every(n => !isNaN(n)) && !isNaN(r.addl));
  }

  function ymdNow() {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
  }

  function same6(a, b) {
    if (a.length !== 6 || b.length !== 6) return false;
    for (let i = 0; i < 6; i++) if (a[i] !== b[i]) return false;
    return true;
  }

  function findComboFoundDate(picks, draws, maxPick) {
    // picks: sorted
    if (picks.length === 6) {
      for (const d of draws) {
        if (same6(picks, d.main)) return d.date;
      }
      return "";
    }
    // 7-pick only used for SG; check all 6-subsets
    if (picks.length === 7 && maxPick === 7) {
      for (let skip = 0; skip < 7; skip++) {
        const six = picks.filter((_, i) => i !== skip).slice().sort((a,b)=>a-b);
        for (const d of draws) {
          if (same6(six, d.main)) return d.date;
        }
      }
    }
    return "";
  }

  function buildLatestRow(draws) {
    if (!draws || draws.length === 0) return { date: "—", balls: [], comboFoundDate: "" };
    const latest = draws[0];
    const latestKey = latest.main.join("-");
    let found = "";
    for (let i = 1; i < draws.length; i++) {
      if (draws[i].main.join("-") === latestKey) { found = draws[i].date; break; }
    }
    return { date: latest.date, balls: [...latest.main, latest.addl], comboFoundDate: found };
  }

  function renderLatest(latest, prevSet) {
    const dateEl = document.getElementById("latest-date");
    const foundEl = document.getElementById("latest-found");
    const ballsWrap = document.getElementById("latest-balls");
    if (!dateEl || !foundEl || !ballsWrap) return;

    dateEl.textContent = latest.date;

    if (latest.comboFoundDate) {
      foundEl.textContent = `Found on ${latest.comboFoundDate}`;
      foundEl.className = "found-date";
    } else {
      foundEl.textContent = "Not Found";
      foundEl.className = "not-found";
    }

    ballsWrap.innerHTML = "";
    latest.balls.forEach((n, idx) => {
      const s = document.createElement("span");
      s.className = "combo-ball";
      if (prevSet && prevSet.has(n)) s.classList.add("hit-prev");
      if (latest.comboFoundDate) s.classList.add("combo-found");
      // show addl as +X
      if (idx === 6) s.textContent = `+${n}`;
      else s.textContent = String(n);
      ballsWrap.appendChild(s);
    });
  }

  function loadHistory(gameKey) {
    const k = storageKeyForGame(gameKey);
    try {
      const r = localStorage.getItem(k);
      if (!r) return [];
      const parsed = JSON.parse(r);
      return parsed.filter(e => e && e.searchDate && Array.isArray(e.numbers) && e.numbers.length >= 6);
    } catch (e) { return []; }
  }
  function saveHistory(gameKey, h) {
    const k = storageKeyForGame(gameKey);
    try { localStorage.setItem(k, JSON.stringify(h)); } catch (e) {}
  }
  function clearHistory(gameKey) {
    const k = storageKeyForGame(gameKey);
    try { localStorage.removeItem(k); } catch (e) {}
  }

  function initForGame(draws) {
    const gKey = currentGameKey();
    const g = currentGame();

    const MIN_PICK = g.minPick;
    const MAX_PICK = g.maxPick;
    const NUM_MAX = g.maxNum;

    const selected = new Set();

    const grid = document.getElementById("ball-grid");
    const display = document.getElementById("selected-display");
    const checkBtn = document.getElementById("lookup-btn");
    const clearBtn = document.getElementById("clear-btn");
    const resultsDiv = document.getElementById("check-results");
    const historyDiv = document.getElementById("search-history");
    const clearHistBtn = document.getElementById("clear-history-btn");

    if (!grid || !display || !checkBtn || !clearBtn || !resultsDiv || !historyDiv || !clearHistBtn) return;

    // Build grid 1..NUM_MAX
    grid.innerHTML = "";
    for (let n = 1; n <= NUM_MAX; n++) {
      const d = document.createElement("div");
      d.className = "ball";
      d.dataset.num = String(n);
      d.textContent = String(n);
      grid.appendChild(d);
    }

    const balls = () => grid.querySelectorAll(".ball");

    function updateUI() {
      const count = selected.size;
      balls().forEach(b => {
        const num = parseInt(b.dataset.num, 10);
        if (selected.has(num)) {
          b.classList.add("selected");
          b.classList.remove("disabled");
        } else {
          b.classList.remove("selected");
          if (count >= MAX_PICK) b.classList.add("disabled");
          else b.classList.remove("disabled");
        }
      });

      if (count === 0) {
        display.textContent = "Selected: none";
      } else {
        const sorted = [...selected].sort((a,b)=>a-b);
        const remaining = MIN_PICK - count;
        let hint = "";
        if (remaining > 0) hint = ` (pick ${remaining} more)`;
        else if (count < MAX_PICK) hint = " (or pick 1 more)";
        display.textContent = "Selected: " + sorted.join(", ") + hint;
      }
      checkBtn.disabled = count < MIN_PICK;
    }

    function runChecks(picks) {
      const latestDraw = draws[0];
      const prevDrawNums = new Set(latestDraw ? [...latestDraw.main, latestDraw.addl] : []);
      const inPrevDraw = picks.filter(n => prevDrawNums.has(n));
      const comboFoundDate = findComboFoundDate(picks, draws, MAX_PICK);
      return { prevDrawNums, inPrevDraw, comboFoundDate };
    }

    function renderResults(picks, result) {
      let html = "";

      html += '<div class="result-block">';
      html += '<div class="result-block-title">Numbers in Previous Draw</div>';
      html += '<div class="result-block-body">';
      const parts = picks.map(n => result.prevDrawNums.has(n) ? `<span class="hit">${n} ✓</span>` : `<span class="miss">${n} ✗</span>`);
      html += parts.join(" &nbsp; ");
      html += `<br><small>${result.inPrevDraw.length} of ${picks.length} appeared in previous draw</small>`;
      html += "</div></div>";

      html += '<div class="result-block">';
      html += '<div class="result-block-title">Combination in History</div>';
      html += '<div class="result-block-body">';
      html += result.comboFoundDate ? `<span class="hit">✓ Found on ${result.comboFoundDate}</span>` : "✗ This exact combination has not occurred.";
      html += "</div></div>";

      resultsDiv.innerHTML = html;
      resultsDiv.style.display = "block";
    }

    function createComboRow(entry) {
      const container = document.createElement("div");
      container.className = "history-entry";

      const row = document.createElement("div");
      row.className = "combo-row";

      const dates = document.createElement("div");
      dates.className = "combo-dates";

      const searchDateEl = document.createElement("span");
      searchDateEl.className = "search-date";
      searchDateEl.textContent = entry.searchDate;
      dates.appendChild(searchDateEl);

      const foundEl = document.createElement("span");
      if (entry.comboFoundDate) {
        foundEl.className = "found-date";
        foundEl.textContent = entry.comboFoundDate;
      } else {
        foundEl.className = "not-found";
        foundEl.textContent = "Not Found";
      }
      dates.appendChild(foundEl);

      row.appendChild(dates);

      const ballsDiv = document.createElement("div");
      ballsDiv.className = "combo-balls";

      const prevSet = new Set(entry.inPrevDraw || []);
      for (const n of entry.numbers) {
        const ball = document.createElement("span");
        ball.className = "combo-ball";
        if (prevSet.has(n)) ball.classList.add("hit-prev");
        if (entry.comboFoundDate) ball.classList.add("combo-found");
        ball.textContent = String(n);
        ballsDiv.appendChild(ball);
      }

      // pad to MAX_PICK for consistent width
      for (let i = entry.numbers.length; i < MAX_PICK; i++) {
        const empty = document.createElement("span");
        empty.className = "combo-ball empty";
        ballsDiv.appendChild(empty);
      }

      row.appendChild(ballsDiv);
      container.appendChild(row);

      container.addEventListener("click", () => {
        selected.clear();
        for (const n of entry.numbers) selected.add(n);
        updateUI();
      });

      return container;
    }

    function renderHistory() {
      const history = loadHistory(gKey);
      historyDiv.innerHTML = "";
      if (history.length === 0) { clearHistBtn.style.display = "none"; return; }
      clearHistBtn.style.display = "";
      for (const entry of history) historyDiv.appendChild(createComboRow(entry));
    }

    // latest row
    const prev = draws[1];
    const prevSet = new Set(prev ? [...prev.main, prev.addl] : []);
    const latest = buildLatestRow(draws);
    renderLatest(latest, prevSet);

    // events
    grid.onclick = (e) => {
      const ball = e.target.closest(".ball");
      if (!ball) return;
      const num = parseInt(ball.dataset.num, 10);
      if (selected.has(num)) selected.delete(num);
      else if (selected.size < MAX_PICK) selected.add(num);
      updateUI();
    };

    clearBtn.onclick = () => { selected.clear(); updateUI(); resultsDiv.style.display = "none"; };
    clearHistBtn.onclick = () => { clearHistory(gKey); renderHistory(); };

    checkBtn.onclick = () => {
      const picked = [...selected].sort((a,b)=>a-b);
      const result = runChecks(picked);
      renderResults(picked, result);

      const entry = {
        searchDate: ymdNow(),
        numbers: picked,
        inPrevDraw: result.inPrevDraw,
        comboFoundDate: result.comboFoundDate
      };

      const history = loadHistory(gKey);
      history.unshift(entry);
      if (history.length > MAX_HISTORY) history.pop();
      saveHistory(gKey, history);
      renderHistory();
    };

    updateUI();
    renderHistory();
  }

  async function loadAndRender() {
    const g = currentGame();
    try {
      const res = await fetch(g.csv, { cache: "no-store" });
      const txt = await res.text();
      const draws = parseCSV(txt);
      initForGame(draws);
    } catch (e) {
      const historyDiv = document.getElementById("search-history");
      if (historyDiv) historyDiv.textContent = "Failed to load data. Try refreshing.";
    }
  }

  window.addEventListener("lotto:gamechange", () => loadAndRender());
  window.addEventListener("DOMContentLoaded", () => loadAndRender());
})();