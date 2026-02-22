import os
import shutil
import importlib
import pkgutil
from datetime import datetime, timezone
import pandas as pd
import markdown
import sys, pathlib

repo_root = pathlib.Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

DATA_PATH = "static/data/sgtoto.csv"
OUTPUT_DIR = "_site"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "index.html")
ANALYSES_PKG = "src.analysis"

ASSETS = {
    "static/data/sgtoto.csv": os.path.join(OUTPUT_DIR, "data", "sgtoto.csv"),
    "src/analysis/lookup.js": os.path.join(OUTPUT_DIR, "js", "lookup.js"),
    "src/analysis/distribution.js": os.path.join(OUTPUT_DIR, "js", "distribution.js"),
}

# Modules whose widget panel should be full-width / larger
WIDE_WIDGETS = {"Distribution"}

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lotto Analyses</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   Helvetica, Arial, sans-serif;
      max-width: 960px;
      margin: 2rem auto;
      padding: 0 1rem;
      line-height: 1.6;
      color: #24292e;
    }}
    table {{
      border-collapse: collapse;
      margin: 1rem 0;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 6px 12px;
      text-align: right;
    }}
    th {{
      background: #f6f8fa;
    }}
    a {{
      color: #0366d6;
    }}
    code {{
      background: #f6f8fa;
      padding: 2px 6px;
      border-radius: 3px;
    }}
    button {{
      padding: 6px 16px;
      cursor: pointer;
    }}

    /* Widget panels */
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
    .widget-panel.widget-wide {{
      /* full width, no max-width constraint */
    }}
    .widget-panel:not(.widget-wide) {{
      max-width: 600px;
      margin-left: auto;
      margin-right: auto;
    }}

    /* Mobile: center all analysis sections */
    @media (max-width: 700px) {{
      body {{
        padding: 0 0.5rem;
        margin: 1rem auto;
      }}
      h1 {{ font-size: 1.4rem; text-align: center; }}
      h2 {{ font-size: 1.1rem; text-align: center; }}
      p {{ text-align: center; }}
      .widget-panel {{
        padding: 1rem;
      }}
      .widget-panel:not(.widget-wide) {{
        max-width: 100%;
      }}
    }}
  </style>
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
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Header (outside any widget)
    header_md = f"# Lotto Analyses\n\n_Last updated: **{ts}**_\n\n[Download data (CSV)](data/sgtoto.csv)\n\n"
    header_html = markdown.markdown(header_md, extensions=["tables", "toc"])

    # Build each widget panel
    panels_html = []
    for _, title, gen in modules:
        try:
            content_md = gen(df)
        except Exception as e:
            content_md = f"\nCould not render this section: `{e}`\n"

        # Convert the module markdown to HTML
        section_md = f"## {title}\n\n{content_md}"
        section_html = markdown.markdown(section_md, extensions=["tables", "toc"])

        is_wide = title in WIDE_WIDGETS
        cls = "widget-panel widget-wide" if is_wide else "widget-panel"
        panel = f'<div class="{cls}">\n{section_html}\n</div>'
        panels_html.append(panel)

    body = header_html + "\n".join(panels_html)
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
