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
                
            # Regex to find the JSON payload for teamsData
            match = re.search(r"var teamsData\s*=\s*JSON\.parse\('(.*?)'\);", html)
            if not match:
                self.logger.error(f"Could not find teamsData in {file.name}")
                continue
                
            raw_data = match.group(1)
            decoded_data = raw_data.encode('utf-8').decode('unicode_escape')
            
            try:
                teams = json.loads(decoded_data)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON in {file.name}: {e}")
                continue
                
            parsed_rows = []
            headers = ["source_club_id", "source_club_name", "season_id", 
                       "matches", "goals", "xG", "missed", "xGA", "pts", "xpts"]
                       
            for team_id, t_data in teams.items():
                hist = t_data.get("history", [])
                
                # Aggregate season totals
                matches = len(hist)
                goals = sum(h.get("scored", 0) for h in hist)
                xG = sum(h.get("xG", 0.0) for h in hist)
                missed = sum(h.get("missed", 0) for h in hist)
                xGA = sum(h.get("xGA", 0.0) for h in hist)
                pts = sum(h.get("pts", 0) for h in hist)
                xpts = sum(h.get("xpts", 0.0) for h in hist)
                
                row = {
                    "source_club_id": t_data.get("id", team_id),
                    "source_club_name": t_data.get("title"),
                    "season_id": season_id,
                    "matches": matches,
                    "goals": goals,
                    "xG": round(xG, 2),
                    "missed": missed,
                    "xGA": round(xGA, 2),
                    "pts": pts,
                    "xpts": round(xpts, 2)
                }
                parsed_rows.append(row)
                
            if parsed_rows:
                out_name = f"understat_teams_parsed_{season_id}.csv"
                self.write_csv(out_name, headers, parsed_rows)
                parsed_files += 1
                parsed_records += len(parsed_rows)
                
        return {"parsed_files": parsed_files, "parsed_records": parsed_records}

if __name__ == "__main__":
    parser = UnderstatParser()
    parser.parse()
