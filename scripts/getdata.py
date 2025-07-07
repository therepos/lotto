import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://en.lottolyzer.com/history/singapore/toto"
DATA_PATH = "data/sgtoto.csv"

# Load existing CSV data
try:
    existing_df = pd.read_csv(DATA_PATH)
    latest_date = existing_df.iloc[0]["Date"]
except Exception:
    existing_df = pd.DataFrame(columns=["Date", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6", "Addl"])
    latest_date = None

# Scrape page
resp = requests.get(URL)
soup = BeautifulSoup(resp.text, "html.parser")

rows = soup.select("table tbody tr")
new_rows = []

for row in rows:
    cols = row.find_all("td")
    if len(cols) < 4:
        continue

    draw_date = cols[1].text.strip()

    if latest_date and draw_date <= latest_date:
        break  # Already processed

    # Extract main numbers and addl number
    main_numbers = [int(n) for n in cols[2].text.strip().split(",")]
    addl = int(cols[3].text.strip())

    new_row = [draw_date] + main_numbers + [addl]
    new_rows.append(new_row)

# Update dataset
if new_rows:
    new_df = pd.DataFrame(new_rows, columns=existing_df.columns)
    updated_df = pd.concat([new_df, existing_df], ignore_index=True)
    updated_df.to_csv(DATA_PATH, index=False)
    print(f"Added {len(new_rows)} new rows.")
else:
    print("No new results.")
