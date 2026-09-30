import logging
from .base_collector import BaseCollector

class FPLDataCollector(BaseCollector):
    """Collects current season data from the Fantasy Premier League (FPL) JSON API."""
    def __init__(self):
        super().__init__("fpl")
        
    def collect(self, seasons):
        stats = {"files": 0, "raw_payloads": 0, "parsed_records": "NOT YET PARSED", "http_status": [], "errors": 0, "seasons_processed": []}
        
        # FPL bootstrap-static only provides the current season. 
        # Historical seasons require custom archives. For now, we fetch it and label it as the latest season.
        latest_season = seasons[-1] 
        url = self.config['base_url']
        
        data, status = self.fetch_url(url, expected_type="json")
        stats["http_status"].append(status)
        
        if data and status == 200:
            filename = f"fpl_bootstrap_{latest_season['season_id']}.json"
            if self.save_raw_data(data, filename, latest_season["season_label"]):
                stats["files"] += 1
                stats["raw_payloads"] += 1
                stats["seasons_processed"].append(latest_season["season_label"])
        else:
            stats["errors"] += 1
            
        return stats
