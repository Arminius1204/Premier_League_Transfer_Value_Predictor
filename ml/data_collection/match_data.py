import logging
from .base_collector import BaseCollector
from .config import CONFIG

class MatchDataCollector(BaseCollector):
    """Collects historical match results and betting odds from football-data.co.uk"""
    def __init__(self):
        super().__init__("football_data")
        
    def collect(self, seasons):
        stats = {"files": 0, "raw_payloads": 0, "parsed_records": "NOT YET PARSED", "http_status": [], "errors": 0, "seasons_processed": []}
        
        for season_obj in seasons:
            yy_yy = f"{str(season_obj['start_year'])[-2:]}{str(season_obj['end_year'])[-2:]}"
            url = f"{self.config['base_url']}{yy_yy}/E0.csv"
            
            data, status = self.fetch_url(url, expected_type="text")
            stats["http_status"].append(status)
            
            if data and status == 200:
                filename = f"E0_{season_obj['season_id']}.csv"
                if self.save_raw_data(data, filename, season_obj["season_label"]):
                    stats["files"] += 1
                    stats["raw_payloads"] += 1
                    stats["seasons_processed"].append(season_obj["season_label"])
            else:
                stats["errors"] += 1
                
        return stats
