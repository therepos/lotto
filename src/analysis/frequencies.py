TITLE = "Frequencies"
ORDER = 21

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

    # Bar data JSON
    bar_data = ",".join(
        f'{{"num":{n},"count":{counts.get(n,0)},"latest":{1 if n in latest_all else 0}}}'
        for n in range(1, 50)
    )

    latest_nums_js = ",".join(str(n) for n in sorted(latest_all))

    return f"""

<span style="font-size:12px;color:#6b7280;">
  <span style="display:inline-block;width:6px;height:12px;background:#f97316;border-radius:1px;vertical-align:middle;"></span> appeared in latest draw
</span>

<style>
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
.bar-track {{
  flex: 1;
  height: 14px;
  background: #f3f4f6;
  border-radius: 2px;
  overflow: hidden;
  display: flex;
  align-items: stretch;
}}
.bar-fill {{
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
  flex-shrink: 0;
}}
.bar-fill.has-marker {{
  border-radius: 2px 0 0 2px;
}}
.bar-latest-marker {{
  width: 6px;
  min-width: 6px;
  height: 100%;
  background: #f97316;
  border-radius: 0 2px 2px 0;
  flex-shrink: 0;
}}
.bar-count {{
  min-width: 24px;
  font-size: 11px;
  color: #6b7280;
}}
</style>

<div>
  <div id="freq-bar-controls">
    <button class="active" data-sort="number">By Number</button>
    <button data-sort="frequency">By Frequency</button>
  </div>
  <div id="freq-bars"></div>
</div>

<script>
(function() {{
  const LOW_COLOR = [219, 234, 254];
  const HIGH_COLOR = [30, 58, 138];
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
      const color = interpolate(t);
      const fillCls = isLatest ? 'bar-fill has-marker' : 'bar-fill';
      html += `<div class="bar-row">`;
      html += `<span class="bar-label">${{d.num}}</span>`;
      html += `<div class="bar-track">`;
      html += `<div class="${{fillCls}}" style="width:${{pct}}%;background:${{color}}"></div>`;
      if (isLatest) {{
        html += `<div class="bar-latest-marker"></div>`;
      }}
      html += `</div>`;
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
