# Phase 11 Reproducibility Record

## 1. Environment & Versions
- **Python Version:** 3.11+
- **Pandas:** (Standard PyPI release)
- **Scikit-Learn:** (Standard PyPI release)
- **XGBoost:** (Standard PyPI release)

## 2. Dataset Versioning
- **Core Features Matrix:** `transfer_features_core_v2.csv`
- **Enriched Features Matrix:** `transfer_features_enriched_v2.csv`
- **Total Valid Transfers:** 781
- **Holdout Set:** 2023/24 (N=151)

## 3. Configuration Identifiers
- **Configuration Version:** `v2.0`
- **Global Random Seed:** `42`
    - Used in Random Forest Regressor
    - Used in Gradient Boosting Regressor
    - Used in XGBoost Regressor
    - Used in MLP Regressor

## 4. Hyperparameter Definitions
- **Ridge:** `alpha=10.0`
- **RandomForest:** `n_estimators=100`, `max_depth=10`, `min_samples_leaf=4`
- **GradientBoosting:** `n_estimators=100`, `max_depth=5`, `learning_rate=0.05`
- **XGBoost:** `n_estimators=100`, `max_depth=5`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`
- **MLP:** `hidden_layer_sizes=(64, 32)`, `max_iter=500`, `early_stopping=True`

## 5. Preprocessing Strategy
- **Numeric Imputation:** `median`
- **Numeric Scaling:** `StandardScaler`
- **Categorical Imputation:** `constant` (fill_value="UNKNOWN")
- **Categorical Encoding:** `OneHotEncoder(handle_unknown='ignore')`

All preprocessing steps are fit exclusively on the training chronologies to prevent temporal target leakage.

## 6. Target Transformation
- **Raw Target:** `fee_gbp` (Used for direct GBP prediction)
- **Log Target:** `log_fee_gbp` (`np.log1p()`). Predictions from log models are inversely transformed using `np.expm1()` prior to error calculation to maintain a uniform GBP evaluation metric. Log predictions are explicitly clipped to a theoretical maximum of `22` (equivalent to ~£3.5B) to prevent NumPy infinity overflow.
