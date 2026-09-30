import csv
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROC_DIR = PROJECT_ROOT / "data" / "processed"
FIG_DIR = PROJECT_ROOT / "docs" / "figures"

def create_svg_histogram(data, title, filename, bins=20, log_x=False):
    if not data: return
    
    # Filter valid
    valid_data = [d for d in data if d is not None and d > 0]
    if log_x:
        valid_data = [math.log1p(d) for d in valid_data]
        
    if not valid_data: return
    
    min_val, max_val = min(valid_data), max(valid_data)
    bin_width = (max_val - min_val) / bins
    if bin_width == 0: bin_width = 1
    
    counts = [0] * bins
    for v in valid_data:
        b = int((v - min_val) / bin_width)
        if b >= bins: b = bins - 1
        counts[b] += 1
        
    max_count = max(counts) if max(counts) > 0 else 1
    
    width, height = 600, 400
    margin = 50
    chart_w = width - 2 * margin
    chart_h = height - 2 * margin
    
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'<rect width="{width}" height="{height}" fill="#f9f9f9" />\n'
    svg += f'<text x="{width/2}" y="30" font-family="Arial" font-size="16" text-anchor="middle">{title}</text>\n'
    
    bin_w = chart_w / bins
    
    for i, count in enumerate(counts):
        bar_h = (count / max_count) * chart_h
        x = margin + i * bin_w
        y = margin + chart_h - bar_h
        svg += f'<rect x="{x}" y="{y}" width="{bin_w-2}" height="{bar_h}" fill="#4C8BF5" />\n'
        
    svg += f'<line x1="{margin}" y1="{height-margin}" x2="{width-margin}" y2="{height-margin}" stroke="black" />\n'
    svg += f'<text x="{margin}" y="{height-margin+20}" font-family="Arial" font-size="12">{min_val:.1f}</text>\n'
    svg += f'<text x="{width-margin}" y="{height-margin+20}" font-family="Arial" font-size="12" text-anchor="end">{max_val:.1f}</text>\n'
    
    svg += '</svg>'
    
    with open(FIG_DIR / filename, 'w') as f:
        f.write(svg)

def run_eda():
    fees = []
    fees_log = []
    
    with open(PROC_DIR / 'transfer_features_candidate.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            fee = float(row['fee_gbp'])
            fees.append(fee)
            
    create_svg_histogram(fees, "Transfer Fee Distribution (GBP)", "fee_distribution.svg", bins=30)
    create_svg_histogram(fees, "Log1p Transfer Fee Distribution", "log_fee_distribution.svg", bins=30, log_x=True)
    
    # Calculate stats
    n = len(fees)
    mean = sum(fees) / n
    fees_sorted = sorted(fees)
    median = fees_sorted[n//2] if n % 2 != 0 else (fees_sorted[n//2 - 1] + fees_sorted[n//2]) / 2
    variance = sum((x - mean) ** 2 for x in fees) / n
    std = math.sqrt(variance)
    
    # Skewness
    skew = sum(((x - mean) / std) ** 3 for x in fees) / n if std > 0 else 0
    
    print(f"Fee Stats: Min={min(fees)}, Max={max(fees)}, Mean={mean:.0f}, Median={median:.0f}, Std={std:.0f}, Skew={skew:.2f}")

if __name__ == "__main__":
    run_eda()
