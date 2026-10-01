import pyreadr
import urllib.request
import os

os.makedirs('data/raw/fbref', exist_ok=True)
url = 'https://github.com/JaseZiv/worldfootballR_data/releases/download/fb_big5_advanced_season_stats/big5_team_standard.rds'
file_path = 'data/raw/fbref/big5_team_standard.rds'
csv_path = 'data/raw/fbref/big5_team_standard.csv'

print(f"Downloading {url}...")
urllib.request.urlretrieve(url, file_path)

print("Converting to CSV...")
res = pyreadr.read_r(file_path)
df = res[None]
df.to_csv(csv_path, index=False)
print("Saved to", csv_path)
