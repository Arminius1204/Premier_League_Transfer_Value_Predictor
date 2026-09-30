import logging
from .base_collector import BaseCollector

class CapologyDataCollector(BaseCollector):
    """Collects salary data from Capology. Known to be heavily protected by Cloudflare."""
    def __init__(self):
        super().__init__("capology")
        
    def collect(self, seasons):
        stats = {"files": 0, "raw_payloads": 0, "parsed_records": "NOT YET PARSED", "http_status": [], "errors": 0, "seasons_processed": []}
        
        for season_obj in seasons:
            # Capology uses season strings like "2023-2024"
            season_str = f"{season_obj['start_year']}-{season_obj['end_year']}"
            url = f"{self.config['base_url']}{season_str}/"
            
            data, status = self.fetch_url(url, expected_type="text")
            stats["http_status"].append(status)
            
            if data and status == 200:
                filename = f"capology_pl_{season_obj['season_id']}.html"
                if self.save_raw_data(data, filename, season_obj["season_label"]):
                    stats["files"] += 1
                    stats["raw_payloads"] += 1
                    stats["seasons_processed"].append(season_obj["season_label"])
            else:
                stats["errors"] += 1
                
        return stats
