import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

COLUMNS = ["Date", "Num1", "Num2", "Num3", "Num4", "Num5", "Num6", "Addl"]

SOURCES = [
    {
        "name": "sgtoto",
        "url": "https://en.lottolyzer.com/history/singapore/toto",
        "data_path": "static/data/sgtoto.csv",
    },
    {
        "name": "mytotosupreme",
        "url": "https://en.lottolyzer.com/history/malaysia/supreme-toto/",
        "data_path": "static/data/mytotosupreme.csv",
    },
    {
        "name": "mytotostar",
        "url": "https://en.lottolyzer.com/history/malaysia/star-toto/",
        "data_path": "static/data/mytotostar.csv",
    },
    {
        "name": "mytotopower",
        "url": "https://en.lottolyzer.com/history/malaysia/power-toto/",
        "data_path": "static/data/mytotopower.csv",
    },
]


def load_existing(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        df = pd.read_csv(path)
        df = df[[c for c in COLUMNS if c in df.columns]]
        if df.empty or set(df.columns) != set(COLUMNS):
            return pd.DataFrame(columns=COLUMNS)
        return df
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return pd.DataFrame(columns=COLUMNS)


def scrape_one(url: str, existing_df: pd.DataFrame) -> list[list]:
    latest_date = None
    if not existing_df.empty and "Date" in existing_df.columns:
        latest_date = str(existing_df.iloc[0]["Date"]).strip()

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table")
    rows = table.find("tbody").find_all("tr") if table and table.find("tbody") else []

    new_rows = []
    for r in rows:
        tds = r.find_all("td")
        # Expected: Draw(0), Date(1), Winning No.(2), Addl No.(3)
        if len(tds) < 4:
            continue

        draw_date = tds[1].get_text(strip=True)
        winning_text = tds[2].get_text(strip=True)
        addl_text = tds[3].get_text(strip=True)

        # Stop if reached already-known date (page is newest-first)
        if latest_date and draw_date <= latest_date:
            break

        try:
            main = [int(x.strip()) for x in winning_text.split(",") if x.strip()]
            if len(main) != 6:
                continue
            addl = int(addl_text)
        except ValueError:
            continue

        new_rows.append([draw_date] + main + [addl])

    return new_rows


def update_source(src: dict) -> None:
    path = src["data_path"]
    url = src["url"]

    existing_df = load_existing(path)
    new_rows = scrape_one(url, existing_df)

    if new_rows:
        new_df = pd.DataFrame(new_rows, columns=COLUMNS)
        updated = pd.concat([new_df, existing_df], ignore_index=True)
        updated.to_csv(path, index=False)
        print(f"[{src['name']}] Added {len(new_rows)} new row(s).")
    else:
        print(f"[{src['name']}] No new rows to add.")


if __name__ == "__main__":
    for src in SOURCES:
        update_source(src)