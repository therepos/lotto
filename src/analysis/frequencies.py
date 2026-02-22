TITLE = "Frequencies"
ORDER = 21

def generate(df):
    return """

<span style="font-size:12px;color:#6b7280;">
  <span style="display:inline-block;width:6px;height:12px;background:#f97316;border-radius:1px;vertical-align:middle;"></span>
  appeared in latest draw
</span>

<style>
#freq-bar-controls {
  display: flex;
  gap: 0;
  margin-bottom: 0.5rem;
}
#freq-bar-controls button {
  padding: 6px 16px;
  cursor: pointer;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #374151;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.15s ease;
}
#freq-bar-controls button:first-child { border-radius: 4px 0 0 4px; }
#freq-bar-controls button:last-child { border-radius: 0 4px 4px 0; }
#freq-bar-controls button + button { border-left: none; }
#freq-bar-controls button:hover { background: #f3f4f6; }
#freq-bar-controls button.active {
  background: #1e3a8a;
  color: #fff;
  border-color: #1e3a8a;
}

#freq-bars {
  max-height: 420px;
  overflow-y: auto;
}
.bar-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 1px 0;
  font-size: 12px;
}
.bar-label {
  min-width: 22px;
  text-align: right;
  font-weight: 600;
  color: #374151;
  font-size: 11px;
}
.bar-track {
  flex: 1;
  height: 14px;
  background: #f3f4f6;
  border-radius: 2px;
  overflow: hidden;
  display: flex;
  align-items: stretch;
}
.bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
  flex-shrink: 0;
}
.bar-fill.has-marker { border-radius: 2px 0 0 2px; }
.bar-latest-marker {
  width: 6px;
  min-width: 6px;
  height: 100%;
  background: #f97316;
  border-radius: 0 2px 2px 0;
  flex-shrink: 0;
}
.bar-count {
  min-width: 24px;
  font-size: 11px;
  color: #6b7280;
}
</style>

<div>
  <div id="freq-bar-controls">
    <button class="active" data-sort="number">By Number</button>
    <button data-sort="frequency">By Frequency</button>
  </div>
  <div id="freq-bars">Loading…</div>
</div>

<script src="js/frequencies.js"></script>
"""