import requests
import time
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
import urllib.parse

logger = logging.getLogger(__name__)

class APIFootballClient:
    def __init__(self, api_key: str, cache_dir: Path):
        self.api_key = api_key
        self.cache_dir = cache_dir
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Position mapping to canonical positions
        self.position_map = {
            "Attacker": "Forward",
            "Midfielder": "Midfielder",
            "Defender": "Defender",
            "Goalkeeper": "Goalkeeper"
        }

    def _get_cache_path(self, key: str) -> Path:
        safe_key = urllib.parse.quote_plus(key)
        return self.cache_dir / f"{safe_key}.json"

    def _read_cache(self, key: str) -> Optional[Dict]:
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _write_cache(self, key: str, data: Dict):
        cache_path = self._get_cache_path(key)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        if not self.api_key:
            logger.warning("API-Football key not configured")
            return None
            
        cache_key = f"{endpoint}?{urllib.parse.urlencode(params)}"
        cached = self._read_cache(cache_key)
        if cached:
            return cached
            
        url = f"{self.base_url}/{endpoint}"
        try:
            logger.info(f"Calling API-Football: {url}")
            # Basic rate limiting sleep (10 requests per minute on free tier, 1 req per 6s)
            time.sleep(6)
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("errors"):
                self._write_cache(cache_key, data)
                
            return data
        except Exception as e:
            logger.error(f"API-Football request failed: {e}")
            return None

    def search_player(self, name: str, nationality: Optional[str] = None) -> List[Dict]:
        """Search for a player by name and optionally nationality."""
        params = {"search": name}
        data = self._make_request("players", params)
        
        if not data or not data.get("response"):
            return []
            
        results = []
        for item in data["response"]:
            player_info = item.get("player", {})
            
            # If nationality is provided, filter
            if nationality and player_info.get("nationality") != nationality:
                continue
                
            # Map position if statistics exist
            position = None
            stats = item.get("statistics", [])
            if stats and stats[0].get("games", {}).get("position"):
                raw_pos = stats[0]["games"]["position"]
                position = self.position_map.get(raw_pos, raw_pos)
                
            results.append({
                "canonical_name": player_info.get("name"),
                "position": position,
                "nationality": player_info.get("nationality"),
                "date_of_birth": player_info.get("birth", {}).get("date"),
                "photo_url": player_info.get("photo"),
                "external_player_id": str(player_info.get("id")) if player_info.get("id") else None
            })
            
        return results

    def get_player(self, player_id: str) -> Optional[Dict]:
        """Get player details by external ID."""
        params = {"id": player_id}
        data = self._make_request("players", params)
        
        if not data or not data.get("response"):
            return None
            
        item = data["response"][0]
        player_info = item.get("player", {})
        
        position = None
        stats = item.get("statistics", [])
        if stats and stats[0].get("games", {}).get("position"):
            raw_pos = stats[0]["games"]["position"]
            position = self.position_map.get(raw_pos, raw_pos)
            
        return {
            "canonical_name": player_info.get("name"),
            "position": position,
            "nationality": player_info.get("nationality"),
            "date_of_birth": player_info.get("birth", {}).get("date"),
            "photo_url": player_info.get("photo"),
            "external_player_id": str(player_info.get("id")) if player_info.get("id") else None
        }
