TITLE = "Check Your Combination"
ORDER = 5

def generate(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    latest = df.iloc[0]
    latest_date = latest["Date"]
    latest_nums = sorted([int(latest[f"Num{i}"]) for i in range(1, 7)])
    latest_addl = int(latest["Addl"])

    # Previous draw (draw before latest)
    prev = df.iloc[1]
    prev_nums = set(int(prev[f"Num{i}"]) for i in range(1, 7))
    prev_addl = int(prev["Addl"])
    prev_all = prev_nums | {prev_addl}

    # Check if latest combination occurred before in history
    latest_key = "-".join(str(n) for n in latest_nums)
    combo_found_date = ""
    for _, row in df.iloc[1:].iterrows():
        hist_nums = sorted([int(row[f"Num{i}"]) for i in range(1, 7)])
        if "-".join(str(n) for n in hist_nums) == latest_key:
            combo_found_date = row["Date"]
            break

    cells = ""
    for n in range(1, 50):
        cells += f'<div class="ball" data-num="{n}">{n}</div>\n'

    # Build latest draw balls with orange/outline logic
    latest_balls_html = ""
    for n in latest_nums:
        in_prev = n in prev_all
        classes = "combo-ball"
        if in_prev:
            classes += " hit-prev"
        latest_balls_html += f'<span class="{classes}">{n}</span>\n'

    # Additional number as 7th ball
    addl_classes = "combo-ball addl-ball"
    if latest_addl in prev_all:
        addl_classes += " hit-prev"
    latest_balls_html += f'<span class="{addl_classes}">+{latest_addl}</span>\n'

    combo_date_html = f'<span class="found-date">{combo_found_date}</span>' if combo_found_date else '<span class="not-found">Not Found</span>'

    return f"""

Pick 6 or 7 numbers, then click **Check history**.

<style>
#combo-section {{
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin: 1rem auto;
  max-width: 600px;
}}

/* ── Picker grid ── */
#ball-grid {{
  display: grid;
  grid-template-columns: repeat(7, 42px);
  gap: 6px;
  margin: 0.5rem auto;
  justify-content: center;
}}
.ball {{
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  user-select: none;
  background: #fff;
  color: #333;
  transition: all 0.15s ease;
}}
.ball:hover {{ border-color: #0366d6; background: #f0f7ff; }}
.ball.selected {{ background: #0366d6; color: #fff; border-color: #0366d6; }}
.ball.disabled {{ opacity: 0.35; cursor: not-allowed; }}
#selected-display {{
  margin: 0.5rem 0; font-size: 14px; color: #586069; text-align: center;
}}
#lookup-controls {{
  margin: 0.5rem 0; display: flex; gap: 8px; justify-content: center;
}}
#lookup-controls button {{
  padding: 6px 16px; cursor: pointer; border: 1px solid #ccc;
  border-radius: 4px; background: #fafbfc; font-size: 13px;
}}
#lookup-controls button:hover {{ background: #f0f0f0; }}
#lookup-controls button#lookup-btn {{
  background: #0366d6; color: #fff; border-color: #0366d6;
}}
#lookup-controls button#lookup-btn:hover {{ background: #0255b3; }}
#lookup-controls button#lookup-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}

/* ── Results detail (hidden by default) ── */
#check-results {{
  background: #f9fafb; border: 1px solid #e5e7eb;
  border-radius: 6px; padding: 1rem; display: none;
}}
.result-block {{
  margin-bottom: 0.6rem; padding: 0.5rem 0.6rem;
  background: #fff; border-radius: 4px; border: 1px solid #e5e7eb;
}}
.result-block:last-child {{ margin-bottom: 0; }}
.result-block-title {{
  font-size: 11px; font-weight: 600; color: #6b7280;
  text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem;
}}
.result-block-body {{
  font-size: 13px; color: #374151; line-height: 1.6;
}}
.result-block-body .hit {{ color: #16a34a; font-weight: 700; }}
.result-block-body .miss {{ color: #d1d5db; }}
.result-block-body .addl-hit {{ color: #ef4444; font-weight: 700; }}

/* ── Shared combo row (Latest Draw / Search History) ── */
.panel-heading {{
  font-size: 13px; font-weight: 600; color: #6b7280;
  text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;
}}
.panel-divider {{ border: none; border-top: 1px solid #e5e7eb; margin: 0.75rem 0; }}

.combo-row {{
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
}}
.combo-dates {{
  min-width: 90px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}}
.combo-dates .search-date {{
  font-weight: 600; color: #374151; font-size: 12px; white-space: nowrap;
}}
.combo-dates .found-date {{
  font-size: 12px; color: #f97316; white-space: nowrap;
}}
.combo-dates .not-found {{
  font-size: 12px; color: #9ca3af; white-space: nowrap;
}}

.combo-balls {{
  display: grid;
  grid-template-columns: repeat(7, 42px);
  gap: 6px;
}}
.combo-ball {{
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 2px solid #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  background: #f3f4f6;
  color: #6b7280;
}}
.combo-ball.hit-prev {{
  background: #f97316;
  color: #fff;
  border-color: #f97316;
}}
.combo-ball.combo-found {{
  border: 3px solid #1f2937;
}}
.combo-ball.empty {{
  background: #f9fafb;
  border-color: #e5e7eb;
}}
.combo-ball.addl-ball {{
  border-style: dashed;
}}

/* ── Search History ── */
#search-history {{ max-height: 500px; overflow-y: auto; }}
.history-entry {{
  padding: 4px 0;
  cursor: pointer;
  border-radius: 4px;
}}
.history-entry:hover {{
  background: #f9fafb;
}}
#clear-history-btn {{
  margin-top: 0.5rem; padding: 4px 12px; cursor: pointer;
  border: 1px solid #ccc; border-radius: 4px; background: #fafbfc;
  font-size: 12px; color: #6b7280;
}}
#clear-history-btn:hover {{ background: #f0f0f0; }}

/* ── Legend ── */
.combo-legend {{
  display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 0.5rem;
}}
.combo-legend-item {{
  display: flex; align-items: center; gap: 4px; font-size: 11px; color: #6b7280;
}}
.legend-swatch {{
  width: 16px; height: 16px; border-radius: 50%; flex-shrink: 0;
}}
.legend-swatch.swatch-prev {{
  background: #f97316;
}}
.legend-swatch.swatch-combo {{
  background: #f3f4f6; border: 3px solid #1f2937;
}}

@media (max-width: 700px) {{
  #ball-grid {{
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    max-width: 340px;
  }}
  .ball {{
    width: 100%;
    height: auto;
    aspect-ratio: 1;
    font-size: 12px;
  }}
  .combo-balls {{
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
  }}
  .combo-ball {{
    width: 100%;
    height: auto;
    aspect-ratio: 1;
    font-size: 12px;
  }}
  .combo-dates {{
    min-width: 72px;
  }}
  .combo-dates .search-date {{ font-size: 11px; }}
}}
</style>

<div id="combo-section">
  <div id="combo-picker">
    <div id="ball-grid">
{cells}
    </div>
    <div id="selected-display">Selected: none</div>
    <div id="lookup-controls">
      <button id="lookup-btn" disabled>Check history</button>
      <button id="clear-btn">Clear</button>
    </div>
  </div>

  <div id="check-results"></div>

  <div id="combo-history">
    <div class="combo-legend">
      <span class="combo-legend-item"><span class="legend-swatch swatch-prev"></span> appeared in previous draw</span>
      <span class="combo-legend-item"><span class="legend-swatch swatch-combo"></span> combination found in history</span>
    </div>

    <div class="panel-heading">Latest Draw</div>
    <div class="combo-row" id="latest-draw-row">
      <div class="combo-dates">
        <span class="search-date">{latest_date}</span>
        {combo_date_html}
      </div>
      <div class="combo-balls">
        {latest_balls_html}
      </div>
    </div>
    <hr class="panel-divider">
    <div class="panel-heading">Search History</div>
    <div id="search-history"></div>
    <button id="clear-history-btn" style="display:none;">Clear history</button>
  </div>
</div>

<script src="js/lookup.js"></script>
"""
