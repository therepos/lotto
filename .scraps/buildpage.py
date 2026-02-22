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

# Assets to copy into _site/ for the deployed site
ASSETS = {
    "static/data/sgtoto.csv": os.path.join(OUTPUT_DIR, "data", "sgtoto.csv"),
    "src/analysis/lookup.js": os.path.join(OUTPUT_DIR, "js", "lookup.js"),
    "src/analysis/distribution.js": os.path.join(OUTPUT_DIR, "js", "distribution.js"),
}

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lotto Analyses</title>
  <style>
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
    input[type="number"] {{
      width: 4rem;
      padding: 4px;
      margin: 2px;
    }}
    button {{
      padding: 6px 16px;
      cursor: pointer;
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

    # Build markdown content — no Table of Contents
    md_parts = [
        "# Lotto Analyses",
        "",
        f"_Last updated: **{ts}**_",
        "",
        "[Download data (CSV)](data/sgtoto.csv)",
        "",
    ]

    for _, _, gen in modules:
        try:
            md_parts.append(gen(df))
        except Exception as e:
            md_parts.append(f"## Error\nCould not render this section: `{e}`\n")

    md_text = "\n".join(md_parts)

    # Convert markdown to HTML, preserving raw HTML blocks
    body_html = markdown.markdown(
        md_text,
        extensions=["tables", "toc"],
    )

    html = HTML_TEMPLATE.format(body=body_html)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {OUTPUT_PATH} with {len(modules)} section(s).")


if __name__ == "__main__":
    copy_assets()
    df = load_dataframe(DATA_PATH)
    mods = discover_analyses()
    buildpage(df, mods)