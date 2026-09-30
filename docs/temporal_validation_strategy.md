# Temporal Validation Strategy

## 1. Experimental Design
The dataset spans three consecutive transfer seasons:
- **2021/22** (N = 26)
- **2022/23** (N = 43)
- **2023/24** (N = 302)

To strictly enforce a "future-blind" evaluation, we have implemented a Walk-Forward Chronological Split. 

## 2. Walk-Forward Chronological Split
**Experiment 1 (The Primary Evaluation):**
*   **TRAIN:** 2021/22 + 2022/23 (Total N = 69)
*   **VALIDATION (Test):** 2023/24 (Total N = 302)

### Rationale
*   Standard walk-forward typically uses single-season shifting (e.g. Train 21/22, Val 22/23). However, a training size of N=26 (21/22 alone) is drastically insufficient for ML regression models to capture signal over noise.
*   By combining the first two seasons as the strictly-historical training set, we give models a larger base (N=69). 
*   We reserve the largest class (23/24) as the hold-out validation/test set, which perfectly mirrors a real-world scenario: "Using all historical transfer data up to 2023, predict the 2023/24 window."

## 3. Handling Limited Training Size
While N=69 is still extremely small for tree-based and neural estimators, this strictly preserves chronological integrity. Any cross-validation or random train-test splitting across seasons would constitute temporal data leakage (e.g., predicting a 2021 transfer using rules learned from a 2023 transfer). We prioritize leakage-safety over training size.
