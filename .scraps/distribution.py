TITLE = "Number Distribution Over Time"
ORDER = 15

def generate(df):
    return """
## Number Distribution Over Time

View how each number (1–49) appears across draws over time.

<style>
#dist-view-toggle {
  display: flex;
  gap: 0;
  margin: 1rem 0 0 0;
}
#dist-view-toggle button {
  padding: 8px 20px;
  cursor: pointer;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #374151;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s ease;
}
#dist-view-toggle button:first-child {
  border-radius: 4px 0 0 4px;
}
#dist-view-toggle button:last-child {
  border-radius: 0 4px 4px 0;
}
#dist-view-toggle button + button {
  border-left: none;
}
#dist-view-toggle button:hover {
  background: #f3f4f6;
}
#dist-view-toggle button.active {
  background: #1e3a8a;
  color: #fff;
  border-color: #1e3a8a;
}
#dist-view-toggle button.active + button {
  border-left: 1px solid #d1d5db;
}

#dist-controls {
  display: flex;
  gap: 0;
  margin: 0.5rem 0 0.5rem 0;
}
#dist-controls button {
  padding: 8px 20px;
  cursor: pointer;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #374151;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s ease;
}
#dist-controls button:first-child {
  border-radius: 4px 0 0 4px;
}
#dist-controls button:last-child {
  border-radius: 0 4px 4px 0;
}
#dist-controls button + button {
  border-left: none;
}
#dist-controls button:hover {
  background: #f3f4f6;
}
#dist-controls button.active {
  background: #1e3a8a;
  color: #fff;
  border-color: #1e3a8a;
}
#dist-controls button.active + button {
  border-left: 1px solid #d1d5db;
}

#dist-table-wrap {
  overflow-x: auto;
  margin: 0.5rem 0 1.5rem 0;
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
}
#dist-table-wrap.compact-mode {
  overflow-x: hidden;
}
#dist-table {
  border-collapse: collapse;
  font-size: 12px;
  min-width: 100%;
}
#dist-table.compact #dist-table {
  min-width: auto;
  width: 100%;
}
#dist-table thead {
  position: sticky;
  top: 0;
  z-index: 2;
}
#dist-table th {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 4px 3px;
  text-align: center;
  font-weight: 600;
  color: #374151;
  min-width: 26px;
  font-size: 11px;
}
#dist-table th.row-header {
  position: sticky;
  left: 0;
  z-index: 3;
  background: #f9fafb;
  text-align: right;
  padding: 4px 8px;
  white-space: nowrap;
  min-width: 90px;
}
#dist-table td {
  border: 1px solid #e5e7eb;
  padding: 0;
  text-align: center;
  width: 26px;
  height: 26px;
  position: relative;
}
#dist-table td.row-label {
  position: sticky;
  left: 0;
  z-index: 1;
  background: #fff;
  text-align: right;
  padding: 4px 8px;
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  font-weight: 500;
}

/* Compact mode: smaller cells */
#dist-table-wrap.compact-mode #dist-table th {
  min-width: 0;
  padding: 2px 0;
  font-size: 9px;
  width: auto;
}
#dist-table-wrap.compact-mode #dist-table th.row-header {
  min-width: 80px;
  padding: 2px 6px;
  font-size: 10px;
}
#dist-table-wrap.compact-mode #dist-table td {
  width: auto;
  height: 14px;
  padding: 0;
  border-color: #f0f0f0;
}
#dist-table-wrap.compact-mode #dist-table td.row-label {
  padding: 1px 6px;
  font-size: 10px;
  height: 14px;
}
#dist-table-wrap.compact-mode .dot {
  width: 6px;
  height: 6px;
}
#dist-table-wrap.compact-mode .heat-cell {
  font-size: 8px;
}

/* Latest row highlight */
#dist-table tr.latest-row td {
  background-color: #fffde7 !important;
}
#dist-table tr.latest-row td.row-label {
  background-color: #fffde7 !important;
}

#dist-table .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  vertical-align: middle;
}
#dist-table .heat-cell {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: transparent;
}
#dist-table .heat-cell:hover {
  color: #fff;
  font-weight: 700;
  text-shadow: 0 0 2px rgba(0,0,0,0.5);
}
#dist-tooltip {
  display: none;
  position: fixed;
  background: #1f2937;
  color: #fff;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 100;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
</style>

<div id="dist-view-toggle">
  <button class="active" data-view="compact">Compact</button>
  <button data-view="table">Table</button>
</div>
<div id="dist-controls">
  <button class="active" data-mode="draw">By Draw</button>
  <button data-mode="week">By Week</button>
  <button data-mode="month">By Month</button>
</div>
<div id="dist-table-wrap" class="compact-mode">
  <table id="dist-table"><thead></thead><tbody></tbody></table>
</div>
<div id="dist-tooltip"></div>

<script src="js/distribution.js"></script>
"""