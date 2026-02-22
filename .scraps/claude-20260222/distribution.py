TITLE = "Distribution"
ORDER = 15

def generate(df):
    return """

View how each number (1–49) appears across draws over time.

<style>
#dist-controls {
  display: flex;
  gap: 0;
  margin: 1rem 0 0.5rem 0;
  align-items: stretch;
}
#dist-controls button,
#dist-controls a {
  padding: 8px 20px;
  cursor: pointer;
  border: 1px solid #d1d5db;
  background: #f9fafb;
  color: #374151;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  line-height: 1;
}
#dist-controls > *:first-child {
  border-radius: 4px 0 0 4px;
}
#dist-controls > *:last-child {
  border-radius: 0 4px 4px 0;
}
#dist-controls > * + * {
  border-left: none;
}
#dist-controls button:hover,
#dist-controls a:hover {
  background: #f3f4f6;
}
#dist-controls button.active {
  background: #1e3a8a;
  color: #fff;
  border-color: #1e3a8a;
}
#dist-controls button.active + *,
#dist-controls button.active + button {
  border-left: 1px solid #d1d5db;
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

.excel-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
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
  #dist-controls button,
  #dist-controls a {
    padding: 6px 12px;
    font-size: 11px;
  }
}
</style>

<div id="dist-controls">
  <button class="active" data-mode="draw">By Draw</button>
  <button data-mode="week">By Week</button>
  <button data-mode="month">By Month</button>
  <a id="dist-download-btn" href="#" download="distribution.xlsx"><svg class="excel-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" fill="#fff" stroke="#217346" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 2v6h6" stroke="#217346" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 13l2.5 4M8 17l2.5-4M13.5 13L11 17M13.5 17L11 13" stroke="#217346" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg> Excel</a>
</div>
<div id="dist-table-wrap">
  <table id="dist-table"><thead></thead><tbody></tbody></table>
</div>
<div id="dist-tooltip"></div>

<script src="js/distribution.js"></script>
"""
