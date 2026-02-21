import os
import importlib
import pkgutil
from datetime import datetime
import pandas as pd
import sys, os, pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
    
DATA_PATH = "static/data/sgtoto.csv"
OUTPUT_PATH = "app/index.md"
ANALYSES_PKG = "scripts"

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
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = [
        "# Lotto Analyses",
        "",
        f"_Last updated: **{ts}**_",
        "",
        f"[Download data (CSV)](./assets/sgtoto.csv)",
        "",
        "## Table of Contents",
    ]
    for _, title, _ in modules:
        anchor = title.lower().replace(" ", "-")
        header.append(f"- [{title}](#{anchor})")
    header.append("")

    sections = []
    for _, _, gen in modules:
        try:
            sections.append(gen(df))
        except Exception as e:
            sections.append(f"## Error\nCould not render this section: `{e}`\n")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(header + sections))
    print(f"Wrote {OUTPUT_PATH} with {len(modules)} section(s).")

if __name__ == "__main__":
    df = load_dataframe(DATA_PATH)
    mods = discover_analyses()
    buildpage(df, mods)
