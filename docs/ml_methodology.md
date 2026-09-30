# ML Methodology

## Valuation Engine Overview
The objective is to accurately predict the transfer value of a Premier League player using historical data, while providing explainability and uncertainty estimates.

## 1. Regression Models
We will train at least 5 distinct machine learning regression models to form a robust baseline:
1. Linear/Ridge/Lasso Regression (Baseline)
2. Random Forest Regressor
3. XGBoost Regressor
4. LightGBM Regressor
5. Support Vector Regression (SVR) or a Neural Network (if justifiable)

## 2. Ensemble Valuation
The final predicted transfer value will be derived from an ensemble of the aforementioned models. Techniques such as stacked generalization (Stacking) or simple weighted averaging will be evaluated to optimize performance (measured via MAE, RMSE, and MAPE).

## 3. Explainable AI (SHAP)
Transparency is critical for football analytics. We will use SHAP (Shapley Additive exPlanations) to decompose every valuation prediction. This will allow the system to explain *why* a player is valued at a certain amount (e.g., "+£15M for age (21)", "+£10M for non-penalty xG/90", "-£5M for remaining contract length").

## 4. Prediction Uncertainty/Range
Transfer fees are not absolute numbers but negotiated figures. The model will output a prediction range (e.g., £45M - £55M) rather than just a point estimate. This will be achieved using techniques like Quantile Regression or Bootstrapping.

## 5. Predicted-vs-Actual Analysis
We will maintain a robust evaluation framework that tracks the model's predicted values against actual historical transfer fees to identify biases (e.g., overvaluing strikers, undervaluing defenders).

## 6. Player Similarity
Using feature embeddings or distance metrics (e.g., Cosine Similarity, Euclidean Distance on scaled PCA features), the system will identify similar players. This is highly useful for scouting (e.g., "Find me a cheaper alternative to Declan Rice").

## 7. What-If Valuation Simulation
The system will allow users to tweak inputs to see how valuation changes (e.g., "What if this player scores 5 more goals next season?", "What if he signs a new 5-year contract?").
