import csv
from pathlib import Path

class SeasonResolver:
    def __init__(self):
        self.master_seasons = [
            {"season_id": "2018_2019", "season_label": "2018/19", "start_year": 2018, "end_year": 2019, "competition": "Premier League"},
            {"season_id": "2019_2020", "season_label": "2019/20", "start_year": 2019, "end_year": 2020, "competition": "Premier League"},
            {"season_id": "2020_2021", "season_label": "2020/21", "start_year": 2020, "end_year": 2021, "competition": "Premier League"},
            {"season_id": "2021_2022", "season_label": "2021/22", "start_year": 2021, "end_year": 2022, "competition": "Premier League"},
            {"season_id": "2022_2023", "season_label": "2022/23", "start_year": 2022, "end_year": 2023, "competition": "Premier League"},
            {"season_id": "2023_2024", "season_label": "2023/24", "start_year": 2023, "end_year": 2024, "competition": "Premier League"}
        ]

    def save(self, output_dir):
        out_dir = Path(output_dir)
        with open(out_dir / "master_season.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["season_id", "season_label", "start_year", "end_year", "competition"])
            writer.writeheader()
            writer.writerows(self.master_seasons)
        return len(self.master_seasons)
