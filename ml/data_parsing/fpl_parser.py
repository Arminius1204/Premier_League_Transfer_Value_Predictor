import json
from ml.data_parsing.base_parser import BaseParser

class FPLParser(BaseParser):
    def __init__(self):
        super().__init__("fpl")
        
    def parse(self):
        files = self.get_raw_files(".json")
        parsed_files = 0
        parsed_records = 0
        
        for file in files:
            # Skip metadata files
            if str(file).endswith(".meta.json"):
                continue
                
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            elements = data.get("elements", [])
            teams_data = data.get("teams", [])
            
            # Map teams for reference
            teams_map = {t["id"]: t["name"] for t in teams_data}
            
            parsed_rows = []
            headers = ["source_player_id", "source_player_name", "source_club_id", "source_club_name", "season_id", 
                       "goals_scored", "assists", "minutes", "expected_goals", "expected_assists", "bps", "now_cost"]
            
            # Since FPL static endpoint doesn't contain season in the JSON, we infer it from the file name
            season_id = "unknown"
            if "bootstrap_" in file.name:
                season_id = file.name.split("bootstrap_")[1].replace(".json", "")
                
            for p in elements:
                row = {
                    "source_player_id": p.get("id"),
                    "source_player_name": f"{p.get('first_name', '')} {p.get('second_name', '')}".strip(),
                    "source_club_id": p.get("team"),
                    "source_club_name": teams_map.get(p.get("team"), "Unknown"),
                    "season_id": season_id,
                    "goals_scored": p.get("goals_scored"),
                    "assists": p.get("assists"),
                    "minutes": p.get("minutes"),
                    "expected_goals": p.get("expected_goals"),
                    "expected_assists": p.get("expected_assists"),
                    "bps": p.get("bps"),
                    "now_cost": p.get("now_cost")
                }
                parsed_rows.append(row)
                
            if parsed_rows:
                out_name = f"fpl_parsed_{season_id}.csv"
                self.write_csv(out_name, headers, parsed_rows)
                parsed_files += 1
                parsed_records += len(parsed_rows)
                
        return {"parsed_files": parsed_files, "parsed_records": parsed_records}

if __name__ == "__main__":
    parser = FPLParser()
    parser.parse()
