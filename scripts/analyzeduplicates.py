import pandas as pd
import os

DATA_PATH = "data/sgtoto.csv"
REPORT_PATH = "reports/duplicate_check.md"

# Load data
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

# Get latest draw
latest = df.iloc[0]
latest_numbers = sorted([latest[f"Num{i}"] for i in range(1, 7)])
latest_date = latest["Date"]

# Check for matches
duplicates = []
for _, row in df.iloc[1:].iterrows():
    nums = sorted([row[f"Num{i}"] for i in range(1, 7)])
    if nums == latest_numbers:
        duplicates.append((row["Date"], nums))

# Write report
os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

with open(REPORT_PATH, "w") as f:
    f.write(f"# Duplicate Check Report ({latest_date})\n\n")
    f.write(f"**Draw Numbers:** {latest_numbers}\n\n")
    if duplicates:
        f.write("❗ **Match Found!**\n\n")
        for date, nums in duplicates:
            f.write(f"- {date}: {nums}\n")
    else:
        f.write("✅ No exact match found in historical records.\n")

print(f"Report written to {REPORT_PATH}")
