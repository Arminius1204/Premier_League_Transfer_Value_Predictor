import json
import re
from ml.data_parsing.base_parser import BaseParser

class UnderstatParser(BaseParser):
    def __init__(self):
        super().__init__("understat")
        
    def parse(self):
        files = self.get_raw_files(".html")
        parsed_files = 0
        parsed_records = 0
        
        for file in files:
            season_id = file.name.split("epl_")[1].replace(".html", "")
            
            with open(file, 'r', encoding='utf-8') as f:
                html = f.read()
                
            # Regex to find the JSON payload for playersData
            match = re.search(r"var playersData\s*=\s*JSON\.parse\('(.*?)'\);", html)
            if not match:
                self.logger.error(f"Could not find playersData in {file.name}")
                continue
                
            raw_data = match.group(1)
            # Understat escapes hex codes, e.g., \x22 for "
            decoded_data = raw_data.encode('utf-8').decode('unicode_escape')
            
            try:
                players = json.loads(decoded_data)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON in {file.name}: {e}")
                continue
                
            parsed_rows = []
            headers = ["source_player_id", "source_player_name", "source_club_name", "season_id", 
                       "games", "time", "goals", "xG", "assists", "xA", "shots", "key_passes"]
                       
            for p in players:
                row = {
                    "source_player_id": p.get("id"),
                    "source_player_name": p.get("player_name"),
                    "source_club_name": p.get("team_title"),
                    "season_id": season_id,
                    "games": p.get("games"),
                    "time": p.get("time"),
                    "goals": p.get("goals"),
                    "xG": p.get("xG"),
                    "assists": p.get("assists"),
                    "xA": p.get("xA"),
                    "shots": p.get("shots"),
                    "key_passes": p.get("key_passes")
                }
                parsed_rows.append(row)
                
            if parsed_rows:
                out_name = f"understat_parsed_{season_id}.csv"
                self.write_csv(out_name, headers, parsed_rows)
                parsed_files += 1
                parsed_records += len(parsed_rows)
                
        return {"parsed_files": parsed_files, "parsed_records": parsed_records}

if __name__ == "__main__":
    parser = UnderstatParser()
    parser.parse()
