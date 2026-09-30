import json
import csv
import logging
from pathlib import Path
from datetime import datetime

class BaseParser:
    def __init__(self, source_name):
        self.source_name = source_name
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.raw_dir = self.project_root / "data" / "raw" / source_name
        self.parsed_dir = self.project_root / "data" / "parsed" / source_name
        self.parsed_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"{source_name}_parser")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def get_raw_files(self, extension):
        if not self.raw_dir.exists():
            return []
        return list(self.raw_dir.glob(f"*{extension}"))

    def write_csv(self, filename, headers, rows):
        """Writes parsed rows to a CSV file."""
        filepath = self.parsed_dir / filename
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        self.logger.info(f"Wrote {len(rows)} records to {filepath}")
