import pandas as pd
import os
import urllib.request

def download_football_data():
    os.makedirs('data/raw/football_data', exist_ok=True)
    leagues = ['E0', 'D1', 'SP1', 'I1', 'F1']
    seasons = ['1819', '1920', '2021', '2122', '2223', '2324', '2425']
    
    for lg in leagues:
        for s in seasons:
            url = f"https://www.football-data.co.uk/mmz4281/{s}/{lg}.csv"
            file_path = f"data/raw/football_data/{lg}_{s}.csv"
            try:
                urllib.request.urlretrieve(url, file_path)
                print(f"Downloaded {lg} {s}")
            except Exception as e:
                print(f"Failed {url}: {e}")

if __name__ == "__main__":
    download_football_data()
