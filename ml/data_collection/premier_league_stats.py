import logging
from .base_collector import BaseCollector
from .config import CONFIG

class PremierLeagueStatsCollector(BaseCollector):
    """Collects player-season statistics from FBref."""
    def __init__(self):
        super().__init__("fbref")
        
    def collect(self, seasons):
        stats = {"files": 0, "raw_payloads": 0, "parsed_records": "NOT YET PARSED", "http_status": [], "errors": 0, "seasons_processed": []}
        
        for season_obj in seasons:
            season_str = f"{season_obj['start_year']}-{season_obj['end_year']}"
            url = f"{self.config['base_url']}{season_str}/{season_str}-Premier-League-Stats"
            
            data, status = self.fetch_url(url, expected_type="text")
            stats["http_status"].append(status)
            
            if data and status == 200:
                filename = f"fbref_pl_{season_obj['season_id']}.html"
                if self.save_raw_data(data, filename, season_obj["season_label"]):
                    stats["files"] += 1
                    stats["raw_payloads"] += 1
                    stats["seasons_processed"].append(season_obj["season_label"])
            else:
                stats["errors"] += 1
                
        return stats
