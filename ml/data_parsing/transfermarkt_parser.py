import re
import uuid
from bs4 import BeautifulSoup
from ml.data_parsing.base_parser import BaseParser

class TransfermarktParser(BaseParser):
    def __init__(self):
        super().__init__("transfermarkt")
        
    def parse(self):
        files = self.get_raw_files(".html")
        parsed_files = 0
        parsed_records = 0
        
        for file in files:
            season_id = file.name.split("pl_")[1].replace(".html", "")
            
            with open(file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, "html.parser")
                
            parsed_rows = []
            
            # The page has boxes for each club. Class "box" containing a header (club name)
            # and then tables for Arrivals (Zugänge) and Departures (Abgänge).
            # But wait, looking for player profile links is more robust.
            
            # Find all rows in all tables that look like transfer rows.
            for row in soup.find_all("tr"):
                cols = row.find_all("td")
                
                # Check if it's a valid transfer row (often > 5 columns)
                if len(cols) < 6:
                    continue
                    
                links = row.find_all("a", href=re.compile(r'/profil/spieler/'))
                if not links:
                    continue
                    
                player_link = links[0]
                player_name = player_link.get_text(strip=True)
                
                href = player_link.get("href", "")
                player_id_match = re.search(r'/spieler/(\d+)', href)
                player_id = player_id_match.group(1) if player_id_match else None
                
                if not player_id:
                    continue
                    
                # We will extract ALL text from the row and do heuristic extraction for fee to be safe
                row_text = row.get_text(separator=" | ", strip=True)
                
                # Try to find transfer ID from fee link
                transfer_link = row.find("a", href=re.compile(r'/transfer_id/\d+'))
                source_transfer_id = ""
                if transfer_link:
                    tid_match = re.search(r'/transfer_id/(\d+)', transfer_link.get("href", ""))
                    if tid_match:
                        source_transfer_id = tid_match.group(1)
                
                # Heuristic for Fee
                fee_str = "UNKNOWN"
                fee_type = "UNKNOWN"
                
                # In the Transfermarkt HTML, the fee is usually the last column.
                if transfer_link:
                    fee_raw = transfer_link.get_text(strip=True)
                    if "Free transfer" in fee_raw or "ablösefrei" in fee_raw.lower():
                        fee_type = "FREE"
                        fee_str = "0"
                    elif "Loan" in fee_raw or "Leihe" in fee_raw:
                        fee_type = "LOAN"
                        fee_str = "0"
                    elif "?" in fee_raw or "Undisclosed" in fee_raw:
                        fee_type = "UNDISCLOSED"
                        fee_str = "UNDISCLOSED"
                    else:
                        fee_type = "DISCLOSED"
                        fee_str = fee_raw
                else:
                    # Fallback text search
                    if "Free transfer" in row_text:
                        fee_type = "FREE"
                        fee_str = "0"
                    elif "Loan" in row_text:
                        fee_type = "LOAN"
                        fee_str = "0"
                    elif "?" in row_text:
                        fee_type = "UNDISCLOSED"
                        fee_str = "UNDISCLOSED"
                    else:
                        curr_match = re.search(r'[€£\x80][\d,\.]+[km]?', row_text)
                        if curr_match:
                            fee_type = "DISCLOSED"
                            fee_str = curr_match.group(0)
                        
                parsed_row = {
                    "transfer_id": str(uuid.uuid4())[:12],
                    "source_transfer_id": source_transfer_id,
                    "source_player_id": player_id,
                    "source_player_name": player_name,
                    "season_id": season_id,
                    "fee_status": fee_type,
                    "raw_fee_string": fee_str,
                    "raw_row_text": row_text
                }
                
                # Check for duplicates (TM lists a transfer twice, once for In, once for Out)
                if parsed_row not in parsed_rows:
                    parsed_rows.append(parsed_row)
                    
            # Deduplicate by player_id + season (rough proxy to avoid double counting same transfer)
            seen_transfers = set()
            deduped_rows = []
            for r in parsed_rows:
                key = (r["source_player_id"], r["season_id"], r["fee_status"])
                if key not in seen_transfers:
                    seen_transfers.add(key)
                    deduped_rows.append(r)
                    
            if deduped_rows:
                out_name = f"transfermarkt_parsed_{season_id}.csv"
                headers = ["transfer_id", "source_transfer_id", "source_player_id", "source_player_name", "season_id", 
                           "fee_status", "raw_fee_string", "raw_row_text"]
                self.write_csv(out_name, headers, deduped_rows)
                parsed_files += 1
                parsed_records += len(deduped_rows)
                
        return {"parsed_files": parsed_files, "parsed_records": parsed_records}

if __name__ == "__main__":
    parser = TransfermarktParser()
    parser.parse()
