import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ml.data_collection.config import CONFIG, SEASONS
from ml.data_collection.match_data import MatchDataCollector
from ml.data_collection.advanced_stats import AdvancedStatsCollector
from ml.data_collection.premier_league_stats import PremierLeagueStatsCollector
from ml.data_collection.transfer_data import TransferDataCollector
from ml.data_collection.fpl_data import FPLDataCollector
from ml.data_collection.capology_data import CapologyDataCollector

def run_all():
    print("Starting Data Acquisition Phase...\n")
    print(f"Target Seasons: {[s['season_label'] for s in SEASONS]}\n")
    
    collectors = [
        ("Match Data (football-data)", MatchDataCollector()),
        ("Advanced Stats (Understat)", AdvancedStatsCollector()),
        ("PL Stats (FBref)", PremierLeagueStatsCollector()),
        ("Transfers (Transfermarkt)", TransferDataCollector()),
        ("FPL API", FPLDataCollector()),
        ("Salaries (Capology)", CapologyDataCollector())
    ]
    
    report = []
    
    for name, collector in collectors:
        print(f"Running collector: {name}...")
        stats = collector.collect(SEASONS)
        
        status_codes = ", ".join(map(str, stats["http_status"]))
        seasons_proc = ", ".join(stats["seasons_processed"]) if stats["seasons_processed"] else "None"
        
        report.append({
            "Source": name,
            "Files": stats["files"],
            "Raw": stats["raw_payloads"],
            "Parsed": stats["parsed_records"],
            "HTTP": status_codes,
            "Errors": stats["errors"],
            "Seasons": seasons_proc
        })
        
    print("\n" + "="*110)
    print("ACQUISITION REPORT")
    print("="*110)
    print(f"{'Source':<30} | {'Files':<5} | {'Raw':<5} | {'Parsed':<15} | {'HTTP Status':<12} | {'Errors':<6} | {'Seasons':<15}")
    print("-" * 110)
    for r in report:
        print(f"{r['Source']:<30} | {r['Files']:<5} | {r['Raw']:<5} | {r['Parsed']:<15} | {r['HTTP']:<12} | {r['Errors']:<6} | {r['Seasons']:<15}")
    print("="*110)
    print("\nLogs available in /logs/ingestion.log")

if __name__ == "__main__":
    run_all()
