TITLE = "Check Your Combination (Interactive)"
ORDER = 5

def generate(df):
    # Build a 7x7 grid of numbers 1-49
    cells = ""
    for n in range(1, 50):
        cells += f'<div class="ball" data-num="{n}">{n}</div>\n'

    return f"""
## Check Your Combination (Interactive)

Pick 6 or 7 numbers from the grid below, then click **Check history**.

<style>
#ball-grid {{
  display: grid;
  grid-template-columns: repeat(7, 40px);
  gap: 6px;
  margin: 1rem 0;
}}
.ball {{
  width: 40px;
  height: 40px;
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
.ball:hover {{
  border-color: #0366d6;
  background: #f0f7ff;
}}
.ball.selected {{
  background: #0366d6;
  color: #fff;
  border-color: #0366d6;
}}
.ball.disabled {{
  opacity: 0.35;
  cursor: not-allowed;
}}
#selected-display {{
  margin: 0.5rem 0;
  font-size: 14px;
  color: #586069;
}}
#lookup-controls {{
  margin: 0.5rem 0;
  display: flex;
  gap: 8px;
}}
#lookup-controls button {{
  padding: 6px 16px;
  cursor: pointer;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fafbfc;
}}
#lookup-controls button:hover {{
  background: #f0f0f0;
}}
#lookup-controls button#lookup-btn {{
  background: #0366d6;
  color: #fff;
  border-color: #0366d6;
}}
#lookup-controls button#lookup-btn:hover {{
  background: #0255b3;
}}
#lookup-controls button#lookup-btn:disabled {{
  opacity: 0.5;
  cursor: not-allowed;
}}
#lookup-result {{
  margin-top: 0.5rem;
  font-weight: 600;
}}
</style>

<div id="combo-lookup">
  <div id="ball-grid">
{cells}
  </div>
  <div id="selected-display">Selected: none</div>
  <div id="lookup-controls">
    <button id="lookup-btn" disabled>Check history</button>
    <button id="clear-btn">Clear</button>
  </div>
  <div id="lookup-result"></div>
</div>

<script src="js/lookup.js"></script>
"""