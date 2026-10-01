import csv
import pytest
from pathlib import Path

PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

def read_csv(filename):
    with open(PROC_DIR / filename, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def test_no_duplicate_transfers():
    transfers = read_csv("transfers_normalized.csv")
    tids = [t["transfer_id"] for t in transfers]
    assert len(tids) == len(set(tids)), "Duplicate transfer IDs found"

def test_no_duplicate_players():
    players = read_csv("players.csv")
    pids = [p["master_player_id"] for p in players]
    assert len(pids) == len(set(pids)), "Duplicate master player IDs found"

def test_fee_normalization_logic():
    transfers = read_csv("transfers_normalized.csv")
    for t in transfers:
        if t["fee_status"] == "UNDISCLOSED":
            assert t["fee_numeric"] == "", "Undisclosed fee was erroneously converted to 0"
        elif t["fee_status"] == "FREE":
            assert t["fee_numeric"] == "0.0" or t["fee_numeric"] == "0", "Free transfer must be explicitly 0 or handled"
            assert t["target_eligible"].upper() == "FALSE", "Free transfer should not be target eligible by default"
        elif t["fee_status"] == "LOAN":
            assert t["fee_numeric"] == "0.0" or t["fee_numeric"] == "0", "Loan must be explicitly 0 or handled"
            assert t["target_eligible"].upper() == "FALSE", "Loan should not be target eligible"
        
        if t["target_eligible"].upper() == "TRUE":
            assert float(t["fee_numeric"]) > 0, "Target eligible transfers must have positive fee"

def test_transfer_linkage_temporal_validity():
    links = read_csv("transfer_performance_links.csv")
    for link in links:
        if link["temporal_status"] == "VALID":
            assert link["latest_valid_season"] != "UNKNOWN", "Valid temporal link must point to a known season"

def test_club_points_aggregation():
    clubs = read_csv("club_season_context.csv")
    for club in clubs:
        pts = int(club["points"])
        matches = int(club["matches"])
        assert matches <= 38, f"Too many matches for {club['club_id']}"
        assert pts <= 114, f"Impossible points total {pts}"

def test_fx_conversion():
    transfers = read_csv("transfers_normalized.csv")
    for t in transfers:
        if t["fee_status"] == "DISCLOSED":
            if t["target_eligible"] == "TRUE":
                assert t["fee_gbp"] != "", "Disclosed and eligible transfers must have fee_gbp"
            if t["fee_currency"] == "EUR" and t["fee_numeric"] != "":
                # Ensure conversion happened
                assert float(t["fee_gbp"]) < float(t["fee_numeric"]), "GBP value should be less than EUR value based on 0.85 rates"
        elif t["fee_status"] in ("FREE", "LOAN"):
            assert t["fee_gbp"] == "0.0" or t["fee_gbp"] == "0", "Free/Loan must have 0.0 GBP"
        elif t["fee_status"] == "UNDISCLOSED":
            assert t["fee_gbp"] == "", "Undisclosed must have empty fee_gbp"

def test_player_season_validity():
    ps = read_csv("player_seasons.csv")
    for row in ps:
        assert row["master_player_id"], "Missing player id"
        assert row["season_id"], "Missing season id"
