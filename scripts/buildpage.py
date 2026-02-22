import os
import shutil
import importlib
import pkgutil
import pandas as pd
import markdown
import sys, pathlib

repo_root = pathlib.Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

DATA_PATH = "static/data/sgtoto.csv"   # only used to keep existing flow; widgets now load in browser
OUTPUT_DIR = "_site"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "index.html")
ANALYSES_PKG = "src.analysis"

ASSETS = {
    # data
    "static/data/sgtoto.csv": os.path.join(OUTPUT_DIR, "data", "sgtoto.csv"),
    "static/data/mytotosupreme.csv": os.path.join(OUTPUT_DIR, "data", "mytotosupreme.csv"),
    "static/data/mytotostar.csv": os.path.join(OUTPUT_DIR, "data", "mytotostar.csv"),
    "static/data/mytotopower.csv": os.path.join(OUTPUT_DIR, "data", "mytotopower.csv"),
    # js
    "src/analysis/lookup.js": os.path.join(OUTPUT_DIR, "js", "lookup.js"),
    "src/analysis/distribution.js": os.path.join(OUTPUT_DIR, "js", "distribution.js"),
}

WIDE_WIDGETS = {"Distribution"}

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lotto</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      max-width: 960px;
      margin: 2rem auto;
      padding: 0 1rem;
      line-height: 1.6;
      color: #24292e;
    }}
    h1 {{ text-align: center; margin-bottom: 0.5rem; }}

    .gamebar {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 10px;
      margin: 0.75rem 0 1.25rem 0;
    }}
    .gamebar label {{
      font-size: 12px;
      color: #6b7280;
      font-weight: 600;
      letter-spacing: .04em;
      text-transform: uppercase;
    }}
    .gamebar select {{
      padding: 6px 10px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      background: #fff;
      font-size: 13px;
    }}

    table {{ border-collapse: collapse; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ddd; padding: 6px 12px; text-align: right; }}
    th {{ background: #f6f8fa; }}
    a {{ color: #0366d6; }}
    code {{ background: #f6f8fa; padding: 2px 6px; border-radius: 3px; }}
    button {{ padding: 6px 16px; cursor: pointer; }}

    .widget-panel {{
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.25rem;
    }}
    .widget-panel h2 {{
      margin-top: 0;
      font-size: 1rem;
      color: #1f2937;
    }}
    .widget-panel:not(.widget-wide) {{
      max-width: 600px;
      margin-left: auto;
      margin-right: auto;
    }}

    @media (max-width: 700px) {{
      body {{ padding: 0 0.5rem; margin: 1rem auto; }}
      h1 {{ font-size: 1.4rem; text-align: center; }}
      h2 {{ font-size: 1.1rem; text-align: center; }}
      p {{ text-align: center; }}
      .widget-panel {{ padding: 1rem; }}
      .widget-panel:not(.widget-wide) {{ max-width: 100%; }}
    }}
  </style>

  <script>
    // Single source of truth for games (filenames unchanged)
    window.LOTTO_GAMES = {{
      sgtoto: {{
        label: "Singapore Toto (6/49)",
        csv: "data/sgtoto.csv",
        maxNum: 49,
        minPick: 6,
        maxPick: 7
      }},
      mytotosupreme: {{
        label: "Malaysia Supreme Toto",
        csv: "data/mytotosupreme.csv",
        maxNum: 58,
        minPick: 6,
        maxPick: 6
      }},
      mytotostar: {{
        label: "Malaysia Star Toto",
        csv: "data/mytotostar.csv",
        maxNum: 50,
        minPick: 6,
        maxPick: 6
      }},
      mytotopower: {{
        label: "Malaysia Power Toto",
        csv: "data/mytotopower.csv",
        maxNum: 55,
        minPick: 6,
        maxPick: 6
      }}
    }};

    window.LOTTO_STATE = {{
      game: "sgtoto"
    }};

    function setGame(gameKey) {{
      if (!window.LOTTO_GAMES[gameKey]) return;
      window.LOTTO_STATE.game = gameKey;
      try {{ localStorage.setItem("lotto-game", gameKey); }} catch(e) {{}}
      window.dispatchEvent(new CustomEvent("lotto:gamechange", {{ detail: {{ game: gameKey }} }}));
    }}

    function initGameFromUrlOrStorage() {{
      const params = new URLSearchParams(window.location.search);
      const q = params.get("game");
      if (q && window.LOTTO_GAMES[q]) return q;
      try {{
        const s = localStorage.getItem("lotto-game");
        if (s && window.LOTTO_GAMES[s]) return s;
      }} catch(e) {{}}
      return "sgtoto";
    }}

    window.addEventListener("DOMContentLoaded", () => {{
      const g = initGameFromUrlOrStorage();
      window.LOTTO_STATE.game = g;
    }});
  </script>
</head>
<body>
{body}
</body>
</html>
"""


def copy_assets():
    for src, dst in ASSETS.items():
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"Copied {src} → {dst}")


def load_dataframe(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df


def discover_analyses():
    pkg = importlib.import_module(ANALYSES_PKG)
    modules = []
    for m in pkgutil.iter_modules(pkg.__path__):
        if m.ispkg:
            continue
        mod = importlib.import_module(f"{ANALYSES_PKG}.{m.name}")
        gen = getattr(mod, "generate", None)
        if callable(gen):
            title = getattr(mod, "TITLE", m.name.replace("_", " ").title())
            order = getattr(mod, "ORDER", 1000)
            modules.append((order, title, gen))
    modules.sort(key=lambda x: (x[0], x[1].lower()))
    return modules


def buildpage(df, modules):
    header_html = """
<h1>Lotto</h1>
<div class="gamebar">
  <label for="game-select">Game</label>
  <select id="game-select"></select>
</div>

<script>
(function () {
  const sel = document.getElementById("game-select");
  const games = window.LOTTO_GAMES || {};
  const current = (window.LOTTO_STATE && window.LOTTO_STATE.game) ? window.LOTTO_STATE.game : "sgtoto";

  for (const key of Object.keys(games)) {
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = games[key].label;
    sel.appendChild(opt);
  }
  sel.value = games[current] ? current : Object.keys(games)[0];

  sel.addEventListener("change", () => {
    const g = sel.value;
    // update query string (nice shareable URL)
    try {
      const u = new URL(window.location.href);
      u.searchParams.set("game", g);
      window.history.replaceState({}, "", u.toString());
    } catch(e) {}

    // trigger rerender
    setGame(g);
  });

  // Fire initial render after selector is ready
  setGame(sel.value);
})();
</script>
"""

    panels_html = []
    for _, title, gen in modules:
        try:
            content_md = gen(df)
        except Exception as e:
            content_md = f"\nCould not render this section: `{e}`\n"

        section_md = f"## {title}\n\n{content_md}"
        section_html = markdown.markdown(section_md, extensions=["tables", "toc"])

        is_wide = title in WIDE_WIDGETS
        cls = "widget-panel widget-wide" if is_wide else "widget-panel"
        panel = f'<div class="{cls}">\n{section_html}\n</div>'
        panels_html.append(panel)

    body = header_html + "\n".join(panels_html)

    body += """
<footer style="margin-top:2rem;padding:1rem 0;border-top:1px solid #e5e7eb;font-size:12px;color:#9ca3af;display:flex;gap:1.5rem;justify-content:center;">
  <a href="https://github.com/therepos/lotto" style="color:#9ca3af;text-decoration:none;">GitHub</a>
  <a href="https://en.lottolyzer.com/history/singapore/toto" style="color:#9ca3af;text-decoration:none;">Source Data</a>
</footer>
"""
    html = HTML_TEMPLATE.format(body=body)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {OUTPUT_PATH} with {len(modules)} section(s).")


if __name__ == "__main__":
    copy_assets()
    df = load_dataframe(DATA_PATH)
    mods = discover_analyses()
    buildpage(df, mods)