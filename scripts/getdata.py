import requests

URL = "https://en.lottolyzer.com/static/exports/history-sg-toto.csv"
DEST = "data/sg_toto.csv"

response = requests.get(URL)
response.raise_for_status()

with open(DEST, "wb") as f:
    f.write(response.content)

print(f"Downloaded data to {DEST}")
