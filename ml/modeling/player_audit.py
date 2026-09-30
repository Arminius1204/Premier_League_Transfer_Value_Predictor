import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transfer_features_candidate.csv"
DOCS_DIR = PROJECT_ROOT / "docs"

def player_repetition():
    df = pd.read_csv(DATA_PATH)
    
    player_counts = df['master_player_id'].value_counts()
    repeated_players = player_counts[player_counts > 1]
    
    with open(DOCS_DIR / "player_repetition_audit.md", "w") as f:
        f.write("# Player Repetition Audit\n\n")
        f.write(f"- **Total Transfer Events:** {len(df)}\n")
        f.write(f"- **Unique Players:** {len(player_counts)}\n")
        f.write(f"- **Repeated Players (multiple transfers):** {len(repeated_players)}\n\n")
        
        f.write("## Temporal Leakage Implications\n")
        f.write("Because we are using Walk-Forward Validation, a player appearing in Train (e.g., a transfer in 2021) and Test (e.g., a transfer in 2023) is conceptually valid because their 2023 valuation reflects new historical information. However, to prevent the model from memorizing individual identities, **master_player_id** MUST NOT be used as a predictor.\n")

if __name__ == "__main__":
    player_repetition()
