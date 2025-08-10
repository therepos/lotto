# scripts/getdata.py
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://en.lottolyzer.com/history/singapore/toto"
DATA_PATH = "docs/assets/sgtoto.csv"
COLUMNS = ["Date", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6", "Addl"]

# Load existing data (8-column schema)
if os.path.exists(DATA_PATH):
    existing_df = pd.read_csv(DATA_PATH)
    # If the file has extra columns, keep only what we need
    existing_df = existing_df[[c for c in COLUMNS if c in existing_df.columns]]
    # If file missing (first run), initialize empty
    if existing_df.empty or set(existing_df.columns) != set(COLUMNS):
        existing_df = pd.DataFrame(columns=COLUMNS)
else:
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    existing_df = pd.DataFrame(columns=COLUMNS)

latest_date = None
if not existing_df.empty and "Date" in existing_df.columns:
    latest_date = str(existing_df.iloc[0]["Date"]).strip()

# Fetch page
resp = requests.get(URL, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# The first table on the page is the “Summary Table”
table = soup.find("table")
rows = table.find("tbody").find_all("tr") if table else []

new_rows = []
for r in rows:
    tds = r.find_all("td")
    # Expect at least: Draw(0), Date(1), Winning No.(2), Addl No.(3)
    if len(tds) < 4:
        continue

    draw_date = tds[1].get_text(strip=True)
    winning_text = tds[2].get_text(strip=True)
    addl_text = tds[3].get_text(strip=True)

    # Stop if we've reached data we already have (page is newest-first)
    if latest_date and draw_date <= latest_date:
        break

    # Parse numbers
    try:
        main = [int(x.strip()) for x in winning_text.split(",") if x.strip()]
        if len(main) != 6:
            continue  # skip malformed row
        addl = int(addl_text)
    except ValueError:
        continue

    new_rows.append([draw_date] + main + [addl])

# Write back
if new_rows:
    new_df = pd.DataFrame(new_rows, columns=COLUMNS)
    # Ensure newest-first order
    updated = pd.concat([new_df, existing_df], ignore_index=True)
    updated.to_csv(DATA_PATH, index=False)
    print(f"Added {len(new_rows)} new row(s).")
else:
    print("No new rows to add.")
