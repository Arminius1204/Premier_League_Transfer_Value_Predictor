import csv
from ml.data_parsing.base_parser import BaseParser

class FootballDataParser(BaseParser):
    def __init__(self):
        super().__init__("football_data")
        
    def parse(self):
        files = self.get_raw_files(".csv")
        parsed_files = 0
        parsed_records = 0
        
        for file in files:
            season_id = file.name.replace("E0_", "").replace(".csv", "")
            
            with open(file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                parsed_rows = []
                headers = ["source_match_id", "season_id", "source_home_team", "source_away_team", 
                           "home_goals", "away_goals", "match_date"]
                
                for idx, row in enumerate(reader):
                    # Basic validation
                    if not row.get("HomeTeam") or not row.get("AwayTeam"):
                        continue
                        
                    parsed_row = {
                        "source_match_id": f"{season_id}_{idx}",
                        "season_id": season_id,
                        "source_home_team": row.get("HomeTeam"),
                        "source_away_team": row.get("AwayTeam"),
                        "home_goals": row.get("FTHG"),
                        "away_goals": row.get("FTAG"),
                        "match_date": row.get("Date")
                    }
                    parsed_rows.append(parsed_row)
                    
            if parsed_rows:
                out_name = f"football_data_parsed_{season_id}.csv"
                self.write_csv(out_name, headers, parsed_rows)
                parsed_files += 1
                parsed_records += len(parsed_rows)
                
        return {"parsed_files": parsed_files, "parsed_records": parsed_records}

if __name__ == "__main__":
    parser = FootballDataParser()
    parser.parse()
