TITLE = "Heat Map"
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

    return f"""

<span style="font-size:12px;color:#6b7280;">
  <span style="display:inline-block;width:10px;height:10px;border:2.5px solid #f97316;border-radius:2px;vertical-align:middle;"></span> appeared in latest draw
</span>

<style>
#heatmap-grid {{
  display: grid;
  grid-template-columns: repeat(7, 48px);
  gap: 3px;
  margin: 0.5rem auto 0 auto;
  width: fit-content;
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

@media (max-width: 700px) {{
  #heatmap-grid {{
    grid-template-columns: repeat(7, 1fr);
    max-width: 340px;
    width: 100%;
  }}
  .freq-cell {{
    width: 100%;
    height: 38px;
  }}
}}
</style>

<div id="heatmap-grid">
{grid_cells}
</div>

<script>
(function() {{
  const LOW_COLOR = [219, 234, 254];
  const HIGH_COLOR = [30, 58, 138];

  function interpolate(t) {{
    const r = Math.round(LOW_COLOR[0] + (HIGH_COLOR[0] - LOW_COLOR[0]) * t);
    const g = Math.round(LOW_COLOR[1] + (HIGH_COLOR[1] - LOW_COLOR[1]) * t);
    const b = Math.round(LOW_COLOR[2] + (HIGH_COLOR[2] - LOW_COLOR[2]) * t);
    return `rgb(${{r}},${{g}},${{b}})`;
  }}

  function textColor(t) {{ return t > 0.5 ? '#fff' : '#1e3a8a'; }}

  document.querySelectorAll('.freq-cell').forEach(cell => {{
    const t = parseFloat(cell.dataset.t);
    cell.style.background = interpolate(t);
    cell.querySelector('.freq-num').style.color = textColor(t);
    cell.querySelector('.freq-count').style.color = textColor(t);
  }});
}})();
</script>
"""
