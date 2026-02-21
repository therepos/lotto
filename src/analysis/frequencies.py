TITLE = "Number Frequencies"
ORDER = 20

def generate(df):
    # Calculate frequencies
    counts = {}
    for i in range(1, 7):
        for n in df[f"Num{i}"]:
            counts[int(n)] = counts.get(int(n), 0) + 1

    min_count = min(counts.values()) if counts else 0
    max_count = max(counts.values()) if counts else 1
    count_range = max_count - min_count or 1

    # Build 7x7 heatmap grid cells
    grid_cells = ""
    for n in range(1, 50):
        c = counts.get(n, 0)
        t = (c - min_count) / count_range
        grid_cells += f'<div class="freq-cell" data-num="{n}" data-count="{c}" data-t="{t:.3f}">'
        grid_cells += f'<span class="freq-num">{n}</span>'
        grid_cells += f'<span class="freq-count">{c}</span>'
        grid_cells += '</div>\n'

    # Build bar data as JSON for JS
    bar_data = ",".join(
        f'{{"num":{n},"count":{counts.get(n,0)}}}'
        for n in range(1, 50)
    )

    return f"""
## Number Frequencies

<style>
#freq-section {{
  display: flex;
  gap: 2rem;
  margin: 1rem 0;
  align-items: flex-start;
}}
#freq-left {{
  flex: 0 0 auto;
}}
#freq-right {{
  flex: 1 1 auto;
  min-width: 0;
}}

/* Heatmap grid */
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
}}
.freq-cell:hover {{
  transform: scale(1.1);
  z-index: 1;
}}
.freq-num {{
  font-weight: 700;
  font-size: 13px;
}}
.freq-count {{
  font-size: 10px;
  opacity: 0.8;
}}

/* Bar chart controls */
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

/* Bar chart */
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

/* Responsive */
@media (max-width: 700px) {{
  #freq-section {{
    flex-direction: column;
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
  const data = [{bar_data}];
  const maxCount = Math.max(...data.map(d => d.count));
  const minCount = Math.min(...data.map(d => d.count));
  const range = maxCount - minCount || 1;

  function interpolate(t) {{
    const r = Math.round(LOW_COLOR[0] + (HIGH_COLOR[0] - LOW_COLOR[0]) * t);
    const g = Math.round(LOW_COLOR[1] + (HIGH_COLOR[1] - LOW_COLOR[1]) * t);
    const b = Math.round(LOW_COLOR[2] + (HIGH_COLOR[2] - LOW_COLOR[2]) * t);
    return `rgb(${{r}},${{g}},${{b}})`;
  }}

  function textColor(t) {{
    return t > 0.5 ? '#fff' : '#1e3a8a';
  }}

  // Color the heatmap grid
  document.querySelectorAll('.freq-cell').forEach(cell => {{
    const t = parseFloat(cell.dataset.t);
    cell.style.background = interpolate(t);
    cell.querySelector('.freq-num').style.color = textColor(t);
    cell.querySelector('.freq-count').style.color = textColor(t);
  }});

  // Bar chart
  const barsDiv = document.getElementById('freq-bars');
  const sortBtns = document.querySelectorAll('#freq-bar-controls button');

  function renderBars(sortBy) {{
    const sorted = [...data];
    if (sortBy === 'frequency') {{
      sorted.sort((a, b) => b.count - a.count || a.num - b.num);
    }} else {{
      sorted.sort((a, b) => a.num - b.num);
    }}

    let html = '';
    for (const d of sorted) {{
      const pct = maxCount > 0 ? (d.count / maxCount * 100) : 0;
      const t = (d.count - minCount) / range;
      const color = interpolate(t);
      html += `<div class="bar-row">`;
      html += `<span class="bar-label">${{d.num}}</span>`;
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