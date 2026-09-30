import os
import time
import json
import logging
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import CONFIG

class BaseCollector:
    def __init__(self, source_id):
        self.source_id = source_id
        self.config = CONFIG["sources"].get(source_id)
        if not self.config:
            raise ValueError(f"Unknown source ID: {source_id}")
            
        self.logger = logging.getLogger(self.config["name"])
        self.output_dir = self.config["output_dir"]
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup session with robust retries
        self.session = requests.Session()
        self.session.headers.update(CONFIG["headers"])
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def fetch_url(self, url, expected_type="text"):
        """Fetches a URL, respecting rate limits and anti-bot rules."""
        time.sleep(self.config["rate_limit_sec"]) # Enforce rate limit
        self.logger.info(f"Fetching: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 403:
                self.logger.error(f"Access Denied (403) for {url}. Anti-bot system detected. Respecting restriction.")
                return None, 403
                
            response.raise_for_status()
            
            if expected_type == "json":
                return response.json(), response.status_code
            return response.text, response.status_code
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP Error for {url}: {e}")
            return None, e.response.status_code if e.response else 500
        except Exception as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None, 0

    def save_raw_data(self, data, filename, season):
        """Saves raw data with metadata, without cleaning or transforming."""
        if not data:
            return False
            
        filepath = self.output_dir / filename
        
        # Determine format
        if isinstance(data, dict) or isinstance(data, list):
            content = json.dumps(data, indent=2)
            ext = ".json"
        elif filepath.suffix == ".csv":
            content = data
            ext = ""
        else:
            content = data
            ext = ".html"
            
        if not filepath.suffix:
            filepath = filepath.with_suffix(ext)

        # Write the raw file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Write metadata file alongside it
        metadata = {
            "source": self.config["name"],
            "season": season,
            "retrieval_timestamp": datetime.utcnow().isoformat() + "Z",
            "original_filename": filepath.name,
            "size_bytes": len(content)
        }
        
        meta_filepath = filepath.with_suffix('.meta.json')
        with open(meta_filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
            
        self.logger.info(f"Saved raw data and metadata to {filepath}")
        return True
