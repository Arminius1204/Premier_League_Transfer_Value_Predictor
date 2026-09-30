# Data Leakage Policy

Data leakage is the most common cause of overly optimistic machine learning models in sports analytics. This document outlines the strict policies to prevent data leakage in our transfer valuation engine.

## 1. Temporal Integrity (Time Travel Prevention)
- **Strict Cut-offs:** When predicting a transfer fee that occurred on Date X (e.g., August 15, 2021), the model must **only** have access to data generated *before* Date X. 
- **Season Stats:** If a transfer happens mid-season (January window), the model cannot use the full end-of-season statistics for that year. It must only use rolling stats up to December 31st, or the previous season's stats.

## 2. Target Variable Isolation
- The target variable (`transfer_fee`) must never be used to derive features for the training set (e.g., average transfer fee of a player's previous moves) unless rigorously calculated strictly on historical data prior to the prediction point.

## 3. Train/Validation/Test Split
- **Chronological Splitting:** We will not use random k-fold cross-validation, as this leaks future data into past predictions.
- **Time-Series Split:** We will use chronological splitting (e.g., Train on transfers from 2010-2019, Validate on 2020-2021, Test on 2022-2023).

## 4. Feature Engineering Restrictions
- Avoid using "Future Potential" stats or "End of Season Rank" if the transfer occurred before the season ended.
- Any rolling average or cumulative sum feature must be strictly right-aligned/lagged to ensure the current event is not included in the historical window.
