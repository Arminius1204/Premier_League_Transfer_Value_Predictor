import os
import time
import requests
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "fpl_historical"
RAW_DIR.mkdir(parents=True, exist_ok=True)

URLS = {
    "2018_2019": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2018-19/cleaned_players.csv",
    "2019_2020": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2019-20/cleaned_players.csv",
    "2020_2021": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2020-21/cleaned_players.csv",
    "2021_2022": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2021-22/cleaned_players.csv",
    "2022_2023": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2022-23/cleaned_players.csv",
    "2023_2024": "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/cleaned_players.csv"
}

def collect_historical_fpl():
    print("Collecting FPL Historical Data from Vaastav archive...")
    
    for season, url in URLS.items():
        print(f"Fetching {season}...")
        resp = requests.get(url)
        if resp.status_code == 200:
            out_path = RAW_DIR / f"fpl_players_{season}.csv"
            with open(out_path, "wb") as f:
                f.write(resp.content)
            print(f"Saved {out_path}")
        else:
            print(f"Failed to fetch {season}: HTTP {resp.status_code}")
        time.sleep(1)
        
if __name__ == "__main__":
    collect_historical_fpl()
