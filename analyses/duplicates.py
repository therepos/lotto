# analyses/duplicates.py
import pandas as pd

TITLE = "Duplicate Check of Latest Draw"
ORDER = 10  # optional: lower number = earlier on the page

def generate(df: pd.DataFrame) -> str:
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Get latest draw
    latest = df.iloc[0]
    latest_numbers = sorted(int(latest[f"Num{i}"]) for i in range(1, 7))
    latest_date = latest["Date"]

    # Check for matches
    duplicates = []
    for _, row in df.iloc[1:].iterrows():
        nums = sorted([row[f"Num{i}"] for i in range(1, 7)])
        if nums == latest_numbers:
            duplicates.append((row["Date"], nums))

    # Return a Markdown section (no file I/O here)
    lines = []
    lines.append(f"## {TITLE}\n")
    lines.append(f"**Latest Draw:** {latest_date}")
    lines.append(f"\n**Numbers:** `{latest_numbers}`\n")

    if duplicates:
        lines.append("❗ **Match Found!**")
        for date, nums in duplicates:
            lines.append(f"- {date}: `{nums}`")
    else:
        lines.append("✅ No exact match found in historical records.")
    lines.append("")  # trailing newline
    return "\n".join(lines)
