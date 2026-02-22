TITLE = "Heat Map"
ORDER = 20

def generate(df):
    return """

<span style="font-size:12px;color:#6b7280;">
  <span style="display:inline-block;width:10px;height:10px;border:2.5px solid #f97316;border-radius:2px;vertical-align:middle;"></span>
  appeared in latest draw
  <span id="heatmap-range"></span>
</span>

<style>
#heatmap-grid {
  display: grid;
  grid-template-columns: repeat(7, 48px);
  gap: 3px;
  margin: 0.5rem auto 0 auto;
  width: fit-content;
}
.freq-cell {
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
}
.freq-cell:hover { transform: scale(1.1); z-index: 1; }
.freq-cell[data-latest="1"] { outline: 3px solid #f97316; outline-offset: -1px; }
.freq-num { font-weight: 700; font-size: 13px; }
.freq-count { font-size: 10px; opacity: 0.8; }

@media (max-width: 700px) {
  #heatmap-grid {
    grid-template-columns: repeat(7, 1fr);
    max-width: 340px;
    width: 100%;
  }
  .freq-cell { width: 100%; height: 38px; }
}
</style>

<div id="heatmap-grid">Loading…</div>

<script src="js/heatmap.js"></script>
"""