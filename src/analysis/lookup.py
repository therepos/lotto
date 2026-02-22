TITLE = "Check Your Combination"
ORDER = 5

def generate(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    latest = df.iloc[0]
    latest_date = latest["Date"]
    latest_nums = [int(latest[f"Num{i}"]) for i in range(1, 7)]
    latest_addl = int(latest["Addl"])

    latest_sorted = sorted(latest_nums)
    has_dup = False
    dup_date = ""
    best_partial = 0
    best_partial_date = ""
    for _, row in df.iloc[1:].iterrows():
        nums = sorted([int(row[f"Num{i}"]) for i in range(1, 7)])
        if nums == latest_sorted:
            has_dup = True
            dup_date = row["Date"]
            break
        overlap = len(set(nums) & set(latest_sorted))
        if overlap > best_partial:
            best_partial = overlap
            best_partial_date = row["Date"]

    cells = ""
    for n in range(1, 50):
        cells += f'<div class="ball" data-num="{n}">{n}</div>\n'

    main_balls = " ".join(
        f'<span class="draw-ball main">{n}</span>' for n in latest_nums
    )
    addl_ball = f'<span class="draw-ball addl">+{latest_addl}</span>'

    if has_dup:
        pill_class = "pill-full"
        pill_text = dup_date
    elif best_partial >= 3:
        pill_class = "pill-partial"
        pill_text = best_partial_date
    else:
        pill_class = "pill-none"
        pill_text = "No match"

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
#ball-grid {{
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
  margin: 0.5rem auto;
  max-width: 340px;
}}
.ball {{
  width: 100%;
  aspect-ratio: 1;
  max-width: 42px;
  border-radius: 50%;
  border: 2px solid #ccc;
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

.panel-heading {{
  font-size: 13px; font-weight: 600; color: #6b7280;
  text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;
}}
.panel-divider {{ border: none; border-top: 1px solid #e5e7eb; margin: 0.75rem 0; }}
.draw-row {{
  display: flex; align-items: center; gap: 4px; padding: 4px 0;
  font-size: 13px; flex-wrap: wrap; justify-content: center;
}}
.draw-row .draw-date {{
  font-weight: 600; color: #374151; min-width: 82px;
  font-size: 12px; white-space: nowrap;
}}
.draw-ball {{
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 50%;
  font-size: 11px; font-weight: 700; flex-shrink: 0;
}}
.draw-ball.main {{ background: #0366d6; color: #fff; }}
.draw-ball.addl {{ background: #ef4444; color: #fff; }}
.draw-ball.badge {{ background: #0366d6; color: #fff; }}
.draw-ball.plain {{ background: #f3f4f6; color: #6b7280; border: 1px solid #d1d5db; }}
.match-pill {{
  display: inline-flex; align-items: center; justify-content: center;
  padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;
  min-width: 80px; text-align: center; white-space: nowrap; flex-shrink: 0;
}}
.pill-full {{ background: #dcfce7; color: #166534; }}
.pill-partial {{ background: #fef3c7; color: #92400e; }}
.pill-none {{ background: #f3f4f6; color: #9ca3af; }}
#search-history {{ max-height: 400px; overflow-y: auto; }}
.history-row {{
  display: flex; align-items: center; gap: 4px; padding: 4px 6px;
  font-size: 13px; flex-wrap: wrap; cursor: pointer; border-radius: 4px;
  justify-content: center;
}}
.history-row:hover {{ background: #f0f0f0; }}
.history-row .draw-date {{
  font-weight: 500; color: #6b7280; min-width: 82px;
  font-size: 11px; white-space: nowrap;
}}
.history-row .draw-ball {{ width: 24px; height: 24px; font-size: 10px; }}
.history-row .match-pill {{ font-size: 10px; min-width: 82px; padding: 2px 6px; }}
#clear-history-btn {{
  margin-top: 0.5rem; padding: 4px 12px; cursor: pointer;
  border: 1px solid #ccc; border-radius: 4px; background: #fafbfc;
  font-size: 12px; color: #6b7280;
}}
#clear-history-btn:hover {{ background: #f0f0f0; }}

@media (max-width: 700px) {{
  #combo-section {{ max-width: 100%; }}
  #ball-grid {{ max-width: 100%; }}
  .ball {{ font-size: 12px; }}
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
    <div class="panel-heading">Latest Draw</div>
    <div class="draw-row">
      <span class="draw-date">{latest_date}</span>
      {main_balls}
      {addl_ball}
      <span class="match-pill {pill_class}">{pill_text}</span>
    </div>
    <hr class="panel-divider">
    <div class="panel-heading">Search History</div>
    <div id="search-history"></div>
    <button id="clear-history-btn" style="display:none;">Clear history</button>
  </div>
</div>

<script src="js/lookup.js"></script>
"""
