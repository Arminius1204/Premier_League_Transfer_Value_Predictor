import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transfer_features_candidate.csv"
DOCS_DIR = PROJECT_ROOT / "docs"

def data_audit():
    df = pd.read_csv(DATA_PATH)
    
    # Identify unique transfer IDs
    num_rows = len(df)
    unique_transfers = df['transfer_id'].nunique()
    
    # Missingness
    missing = df.isnull().mean() * 100
    missing_dict = missing.round(2).to_dict()
    
    # Basic Stats
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    cat_cols = df.select_dtypes(include=['object']).columns
    
    with open(DOCS_DIR / "phase7_modeling_data_audit.md", "w") as f:
        f.write("# Phase 7: Modeling Data Audit\n\n")
        f.write(f"- **Rows:** {num_rows}\n")
        f.write(f"- **Columns:** {len(df.columns)}\n")
        f.write(f"- **Unique Transfers:** {unique_transfers}\n")
        f.write(f"- **Duplicate Rows:** {num_rows - unique_transfers}\n\n")
        
        f.write("## Missingness (%)\n")
        for col, val in missing_dict.items():
            f.write(f"- **{col}:** {val}%\n")
            
        f.write("\n## Numeric Columns\n")
        for c in numeric_cols:
            f.write(f"- {c}\n")
            
        f.write("\n## Categorical Columns\n")
        for c in cat_cols:
            f.write(f"- {c}\n")
            
    print("Audit generated at docs/phase7_modeling_data_audit.md")

if __name__ == "__main__":
    data_audit()
