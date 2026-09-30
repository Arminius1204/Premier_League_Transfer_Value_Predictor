import os
import logging
from pathlib import Path

# Project Roots
PROJECT_ROOT = Path(os.path.abspath(__file__)).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Standardized Seasons
SEASONS = [
    {"season_id": "2021_2022", "season_label": "2021/22", "start_year": 2021, "end_year": 2022},
    {"season_id": "2022_2023", "season_label": "2022/23", "start_year": 2022, "end_year": 2023},
    {"season_id": "2023_2024", "season_label": "2023/24", "start_year": 2023, "end_year": 2024}
]

# Central Configuration
CONFIG = {
    "sources": {
        "football_data": {
            "name": "football-data.co.uk",
            "base_url": "https://www.football-data.co.uk/mmz4281/",
            "rate_limit_sec": 1.0,
            "output_dir": DATA_DIR / "football_data"
        },
        "understat": {
            "name": "Understat",
            "base_url": "https://understat.com/league/EPL/",
            "rate_limit_sec": 3.0,
            "output_dir": DATA_DIR / "understat"
        },
        "fbref": {
            "name": "FBref",
            "base_url": "https://fbref.com/en/comps/9/",
            "rate_limit_sec": 5.0,
            "output_dir": DATA_DIR / "fbref"
        },
        "transfermarkt": {
            "name": "Transfermarkt",
            "base_url": "https://www.transfermarkt.com/premier-league/transfers/wettbewerb/GB1/plus/?saison_id=",
            "rate_limit_sec": 5.0,
            "output_dir": DATA_DIR / "transfermarkt"
        },
        "fpl": {
            "name": "FPL API",
            "base_url": "https://fantasy.premierleague.com/api/bootstrap-static/",
            "rate_limit_sec": 1.0,
            "output_dir": DATA_DIR / "fpl"
        },
        "capology": {
            "name": "Capology",
            "base_url": "https://www.capology.com/uk/premier-league/salaries/",
            "rate_limit_sec": 5.0,
            "output_dir": DATA_DIR / "capology"
        }
    },
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
}

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "ingestion.log"),
        logging.StreamHandler()
    ]
)
