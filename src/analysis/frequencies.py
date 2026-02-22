TITLE = "Number Frequencies"
ORDER = 20

def generate(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Get latest draw numbers
    latest = df.iloc[0]
    latest_nums = set(int(latest[f"Num{i}"]) for i in range(1, 7))
    latest_addl = int(latest["Addl"])
    latest_all = latest_nums | {latest_addl}

    # Calculate frequencies
    counts = {}
    for i in range(1, 7):
        for n in df[f"Num{i}"]:
            counts[int(n)] = counts.get(int(n), 0) + 1

    min_count = min(counts.values()) if counts else 0
    max_count = max(counts.values()) if counts else 1
    count_range = max_count - min_count or 1

    # Build grid cells with latest-draw flag
    grid_cells = ""
    for n in range(1, 50):
        c = counts.get(n, 0)
        t = (c - min_count) / count_range
        is_latest = 1 if n in latest_all else 0
        grid_cells += f'<div class="freq-cell" data-num="{n}" data-count="{c}" data-t="{t:.3f}" data-latest="{is_latest}">'
        grid_cells += f'<span class="freq-num">{n}</span>'
        grid_cells += f'<span class="freq-count">{c}</span>'
        grid_cells += '</div>\n'

    # Bar data JSON
    bar_data = ",".join(
        f'{{"num":{n},"count":{counts.get(n,0)},"latest":{1 if n in latest_all else 0}}}'
        for n in range(1, 50)
    )

    latest_nums_js = ",".join(str(n) for n in sorted(latest_all))

    return f"""
## Number Frequencies

<span style="font-size:12px;color:#6b7280;">
  <span style="display:inline-block;width:10px;height:10px;background:#f97316;border-radius:2px;vertical-align:middle;"></span> appeared in latest draw
</span>

<style>
#freq-section {{
  display: flex;
  gap: 2rem;
  margin: 1rem auto;
  align-items: flex-start;
  max-width: 960px;
}}
#freq-left {{
  flex: 0 0 auto;
}}
#freq-right {{
  flex: 1 1 auto;
  min-width: 0;
}}

#freq-grid {{
  display: grid;
  grid-template-columns: repeat(7, 48px);
  gap: 3px;
}}
.freq-cell {{
  width: 48px;
  height: 42px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  transition: transform 0.1s ease;
  cursor: default;
  position: relative;
}}
.freq-cell:hover {{
  transform: scale(1.1);
  z-index: 1;
}}
.freq-cell[data-latest="1"] {{
  outline: 3px solid #f97316;
  outline-offset: -1px;
}}
.freq-num {{ font-weight: 700; font-size: 13px; }}
.freq-count {{ font-size: 10px; opacity: 0.8; }}

#freq-bar-controls {{
  display: flex;
  gap: 0;
  margin-bottom: 0.5rem;
}}
#freq-bar-controls button {{
  padding: 6px 16px;
  cursor: pointer;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #374151;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.15s ease;
}}
#freq-bar-controls button:first-child {{
  border-radius: 4px 0 0 4px;
}}
#freq-bar-controls button:last-child {{
  border-radius: 0 4px 4px 0;
}}
#freq-bar-controls button + button {{
  border-left: none;
}}
#freq-bar-controls button:hover {{
  background: #f3f4f6;
}}
#freq-bar-controls button.active {{
  background: #1e3a8a;
  color: #fff;
  border-color: #1e3a8a;
}}

#freq-bars {{
  max-height: 420px;
  overflow-y: auto;
}}
.bar-row {{
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 1px 0;
  font-size: 12px;
}}
.bar-label {{
  min-width: 22px;
  text-align: right;
  font-weight: 600;
  color: #374151;
  font-size: 11px;
}}
.bar-label.latest {{
  color: #f97316;
}}
.bar-track {{
  flex: 1;
  height: 14px;
  background: #f3f4f6;
  border-radius: 2px;
  overflow: hidden;
}}
.bar-fill {{
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}}
.bar-count {{
  min-width: 24px;
  font-size: 11px;
  color: #6b7280;
}}

@media (max-width: 700px) {{
  #freq-section {{
    flex-direction: column;
    align-items: center;
  }}
  #freq-grid {{
    grid-template-columns: repeat(7, 1fr);
    max-width: 340px;
    width: 100%;
  }}
  .freq-cell {{
    width: 100%;
    height: 38px;
  }}
  #freq-right {{
    width: 100%;
  }}
}}
</style>

<div id="freq-section">
  <div id="freq-left">
    <div id="freq-grid">
{grid_cells}
    </div>
  </div>
  <div id="freq-right">
    <div id="freq-bar-controls">
      <button class="active" data-sort="number">By Number</button>
      <button data-sort="frequency">By Frequency</button>
    </div>
    <div id="freq-bars"></div>
  </div>
</div>

<script>
(function() {{
  const LOW_COLOR = [219, 234, 254];
  const HIGH_COLOR = [30, 58, 138];
  const ORANGE = '#f97316';
  const data = [{bar_data}];
  const latestNums = new Set([{latest_nums_js}]);
  const maxCount = Math.max(...data.map(d => d.count));
  const minCount = Math.min(...data.map(d => d.count));
  const range = maxCount - minCount || 1;

  function interpolate(t) {{
    const r = Math.round(LOW_COLOR[0] + (HIGH_COLOR[0] - LOW_COLOR[0]) * t);
    const g = Math.round(LOW_COLOR[1] + (HIGH_COLOR[1] - LOW_COLOR[1]) * t);
    const b = Math.round(LOW_COLOR[2] + (HIGH_COLOR[2] - LOW_COLOR[2]) * t);
    return `rgb(${{r}},${{g}},${{b}})`;
  }}

  function textColor(t) {{ return t > 0.5 ? '#fff' : '#1e3a8a'; }}

  // Color the heatmap grid
  document.querySelectorAll('.freq-cell').forEach(cell => {{
    const t = parseFloat(cell.dataset.t);
    const isLatest = cell.dataset.latest === '1';
    if (isLatest) {{
      cell.style.background = ORANGE;
      cell.querySelector('.freq-num').style.color = '#fff';
      cell.querySelector('.freq-count').style.color = '#fff';
    }} else {{
      cell.style.background = interpolate(t);
      cell.querySelector('.freq-num').style.color = textColor(t);
      cell.querySelector('.freq-count').style.color = textColor(t);
    }}
  }});

  // Bar chart
  const barsDiv = document.getElementById('freq-bars');
  const sortBtns = document.querySelectorAll('#freq-bar-controls button');

  function renderBars(sortBy) {{
    const sorted = [...data];
    if (sortBy === 'frequency') sorted.sort((a, b) => b.count - a.count || a.num - b.num);
    else sorted.sort((a, b) => a.num - b.num);

    let html = '';
    for (const d of sorted) {{
      const pct = maxCount > 0 ? (d.count / maxCount * 100) : 0;
      const t = (d.count - minCount) / range;
      const isLatest = latestNums.has(d.num);
      const color = isLatest ? ORANGE : interpolate(t);
      const labelCls = isLatest ? 'bar-label latest' : 'bar-label';
      html += `<div class="bar-row">`;
      html += `<span class="${{labelCls}}">${{d.num}}</span>`;
      html += `<div class="bar-track"><div class="bar-fill" style="width:${{pct}}%;background:${{color}}"></div></div>`;
      html += `<span class="bar-count">${{d.count}}</span>`;
      html += `</div>`;
    }}
    barsDiv.innerHTML = html;
  }}

  sortBtns.forEach(btn => {{
    btn.addEventListener('click', () => {{
      sortBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderBars(btn.dataset.sort);
    }});
  }});

  renderBars('number');
}})();
</script>
"""
