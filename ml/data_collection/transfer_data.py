import logging
from .base_collector import BaseCollector
from .config import CONFIG

class TransferDataCollector(BaseCollector):
    """Collects transfer data from Transfermarkt. Expects strict anti-bot measures."""
    def __init__(self):
        super().__init__("transfermarkt")
        
    def collect(self, seasons):
        stats = {"files": 0, "raw_payloads": 0, "parsed_records": "NOT YET PARSED", "http_status": [], "errors": 0, "seasons_processed": []}
        
        for season_obj in seasons:
            url = f"{self.config['base_url']}{season_obj['start_year']}"
            
            data, status = self.fetch_url(url, expected_type="text")
            stats["http_status"].append(status)
            
            if data and status == 200:
                filename = f"transfermarkt_pl_{season_obj['season_id']}.html"
                if self.save_raw_data(data, filename, season_obj["season_label"]):
                    stats["files"] += 1
                    stats["raw_payloads"] += 1
                    stats["seasons_processed"].append(season_obj["season_label"])
            else:
                stats["errors"] += 1
                
        return stats
