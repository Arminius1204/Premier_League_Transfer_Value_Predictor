import csv
import pytest
from pathlib import Path

def test_no_target_leakage():
    # Ensure fee_gbp is not accidentally included as a predictor in feature set?
    # Actually, the file includes fee_gbp AS the target. 
    # We just need to check no target-derived aliases exist (e.g., fee_eur is absent).
    with open('data/processed/transfer_features_candidate.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for field in reader.fieldnames:
            if 'fee' in field.lower():
                assert field in ('fee_gbp', 'log_fee_gbp'), f"Unexpected fee column: {field}"

def test_demographics_validity():
    with open('data/processed/transfer_features_candidate.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['age_at_transfer']:
                age = float(row['age_at_transfer'])
                assert 15 <= age <= 45, f"Unrealistic age {age} for player {row['master_player_id']}"
            if row['age_squared']:
                age_sq = float(row['age_squared'])
                assert age_sq > 0

def test_per90_validity():
    with open('data/processed/transfer_features_candidate.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            mins = row['prev_season_minutes']
            g90 = row['prev_season_goals_per90']
            if g90:
                assert mins, "Per-90 metric exists but no minutes recorded"
                assert float(mins) > 0, "Per-90 metric exists but minutes <= 0"

def test_positive_fee():
    with open('data/processed/transfer_features_candidate.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            assert float(row['fee_gbp']) > 0, "Target fee_gbp must be strictly positive"

def test_unique_transfers():
    transfer_ids = set()
    with open('data/processed/transfer_features_candidate.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            tid = row['transfer_id']
            assert tid not in transfer_ids, "Duplicate transfer_id found in candidate dataset"
            transfer_ids.add(tid)
