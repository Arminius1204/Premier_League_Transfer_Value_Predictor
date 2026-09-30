import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_PATH = PROJECT_ROOT / "data" / "processed" / "model_experiment_results.csv"
FIG_DIR = PROJECT_ROOT / "docs" / "figures" / "modeling"
FIG_DIR.mkdir(parents=True, exist_ok=True)

def plot_results():
    df = pd.read_csv(RESULTS_PATH)
    
    # Filter out the MLP exploding log values for visualization
    df_clean = df[df['MAE'] < 1e10]
    
    # 1. Model Metric Comparison (MAE)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_clean, x='MAE', y='model', hue='target_type', errorbar=None)
    plt.title('Mean Absolute Error (GBP) by Model and Target Type')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'metric_comparison_mae.png')
    plt.close()
    
    # 2. R2 Comparison
    # R2 is heavily negative, so let's clip it for the plot
    df_clean['R2_clipped'] = np.maximum(df_clean['R2'], -1.0)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_clean, x='R2_clipped', y='model', hue='target_type')
    plt.title('R² Score (Clipped at -1.0 for visibility)')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'metric_comparison_r2.png')
    plt.close()
    
if __name__ == "__main__":
    plot_results()
