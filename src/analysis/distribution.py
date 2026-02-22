TITLE = "Number Distribution Over Time"
ORDER = 15

def generate(df):
    return """
## Number Distribution Over Time

View how each number (1–49) appears across draws over time.

<style>
#dist-controls {
  display: flex;
  gap: 0;
  margin: 1rem 0 0.5rem 0;
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

#dist-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
#dist-download-btn {
  padding: 5px 14px;
  cursor: pointer;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: #f9fafb;
  color: #374151;
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
#dist-download-btn:hover {
  background: #f3f4f6;
}

#dist-table-wrap {
  overflow-x: hidden;
  margin: 0 0 1.5rem 0;
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
}
#dist-table {
  border-collapse: collapse;
  font-size: 12px;
  width: 100%;
  table-layout: fixed;
}
#dist-table thead {
  position: sticky;
  top: 0;
  z-index: 2;
}
#dist-table th {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 2px 0;
  text-align: center;
  font-weight: 600;
  color: #374151;
  font-size: 9px;
  overflow: hidden;
}
#dist-table th.row-header {
  position: sticky;
  left: 0;
  z-index: 3;
  background: #f9fafb;
  text-align: left;
  padding: 2px 4px;
  white-space: nowrap;
  width: 72px;
  min-width: 72px;
  max-width: 72px;
  font-size: 10px;
}
#dist-table td {
  border: 1px solid #f0f0f0;
  padding: 0;
  text-align: center;
  height: 14px;
  position: relative;
  overflow: hidden;
}
#dist-table td.row-label {
  position: sticky;
  left: 0;
  z-index: 1;
  background: #fff;
  text-align: left;
  padding: 1px 4px;
  font-size: 10px;
  color: #6b7280;
  white-space: nowrap;
  font-weight: 500;
  width: 72px;
  min-width: 72px;
  max-width: 72px;
}
#dist-table .dot {
  width: 6px;
  height: 6px;
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
  font-size: 8px;
  color: transparent;
}
#dist-table .heat-cell:hover {
  color: #fff;
  font-weight: 700;
  text-shadow: 0 0 2px rgba(0,0,0,0.5);
}

/* Latest row highlight */
#dist-table tr.latest-row td {
  background-color: #fffde7 !important;
}
#dist-table tr.latest-row td.row-label {
  background-color: #fffde7 !important;
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

@media (max-width: 700px) {
  #dist-table th.row-header,
  #dist-table td.row-label {
    width: 58px;
    min-width: 58px;
    max-width: 58px;
    font-size: 8px;
    padding: 1px 2px;
  }
  #dist-table th {
    font-size: 7px;
  }
  #dist-table .dot {
    width: 4px;
    height: 4px;
  }
  #dist-table td {
    height: 12px;
  }
}
</style>

<div id="dist-toolbar">
  <div id="dist-controls">
    <button class="active" data-mode="draw">By Draw</button>
    <button data-mode="week">By Week</button>
    <button data-mode="month">By Month</button>
  </div>
  <a id="dist-download-btn" href="#" download="distribution.xlsx">&#x2B73; Excel</a>
</div>
<div id="dist-table-wrap">
  <table id="dist-table"><thead></thead><tbody></tbody></table>
</div>
<div id="dist-tooltip"></div>

<script src="js/distribution.js"></script>
"""
