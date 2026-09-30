# Phase 14 API Contract

This document outlines the API endpoints exposed by the Phase 14A FastAPI Backend.

## Global Headers
- All requests support standard CORS.
- All requests and responses are `application/json` unless otherwise specified.

---

## 1. Health & Status

### 1.1 Application Health
`GET /health`

Returns the health status of the API and its underlying ML models.

**Parameters:**
None

**Response (200 OK):**
```json
{
  "status": "ok",
  "model_loaded": true,
  "similarity_engine_loaded": true,
  "simulation_engine_loaded": true
}
```

---

## 2. Players

### 2.1 Search Players
`GET /players`

Search and paginate historical players.

**Parameters (Query):**
- `q` (string, optional): Search query (matches canonical_name or master_player_id).
- `season` (string, optional): Filter by season (e.g., `2023-2024`).
- `position` (string, optional): Filter by player position.
- `limit` (int, default=20): Max 100.
- `offset` (int, default=0).

**Response (200 OK):**
```json
{
  "items": [
    {
      "player_id": "bruno_fernandes",
      "player_name": "Bruno Fernandes",
      "position": "Midfielder"
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

### 2.2 Player Detail
`GET /players/{player_id}`

Get detailed historical context and transfer records for a specific player.

**Parameters (Path):**
- `player_id` (string, required): The internal master player ID.

**Response (200 OK):**
```json
{
  "player_id": "bruno_fernandes",
  "player_name": "Bruno Fernandes",
  "position": "Midfielder",
  "seasons": ["2019-2020", "2020-2021"],
  "clubs": ["Manchester United"],
  "transfer_history": [
    {
      "season_id": "2019-2020",
      "transfer_type": "Purchase",
      "fee_gbp": 55000000.0,
      "buyer_club": "Manchester United",
      "seller_club": "Sporting CP"
    }
  ]
}
```

**Errors:**
- `404 Not Found`: Player ID not recognized.

---

## 3. Valuation & Explainability

### 3.1 Player Valuation
`GET /players/{player_id}/valuation`

Evaluate a player's expected transfer value based on frozen Phase 12 models.

**Parameters (Path):**
- `player_id` (string, required)

**Parameters (Query):**
- `season` (string, optional): Predict value for a specific historical season context. Defaults to the most recent season context.

**Response (200 OK):**
```json
{
  "player_id": "bruno_fernandes",
  "player_name": "Bruno Fernandes",
  "prediction": 28000000.0,
  "lower_bound": 15000000.0,
  "upper_bound": 41000000.0,
  "currency": "GBP",
  "model": "weighted_ensemble",
  "uncertainty_method": "conformal",
  "feature_coverage": 1.0
}
```

### 3.2 Player Explanation
`GET /players/{player_id}/explanation`

Retrieve feature importance metrics for a specific prediction.

**Parameters (Path):**
- `player_id` (string, required)

**Response (200 OK):**
```json
{
  "player_id": "bruno_fernandes",
  "prediction": 28000000.0,
  "positive_contributors": [
    {"feature": "t1_goals_per90", "impact": "Model contribution"}
  ],
  "negative_contributors": [
    {"feature": "age_at_transfer", "impact": "Model contribution"}
  ],
  "method": "ensemble_weights"
}
```

---

## 4. Similarity

### 4.1 Player Similarity
`GET /players/{player_id}/similar`

Retrieve the most similar players within a specific season context based on their performance profile.

**Parameters (Path):**
- `player_id` (string, required)

**Parameters (Query):**
- `season` (string, required): The target season context for the queried player.
- `top_k` (int, default=5, max=100)

**Response (200 OK):**
```json
{
  "player": {
    "player_id": "bruno_fernandes",
    "season": "2019-2020"
  },
  "results": [
    {
      "player_id": "kevin_de_bruyne",
      "player_name": "Kevin De Bruyne",
      "season": "2018-2019",
      "similarity_score": 0.91,
      "position": "Midfielder",
      "feature_coverage": 1.0,
      "historical_transfer_fee": 25000000.0
    }
  ]
}
```

### 4.2 Profile Similarity
`POST /similarity/profile`

Input an arbitrary feature profile and find historically similar players.

**Body (JSON):**
```json
{
  "position": "Forward",
  "age_at_transfer": 22,
  "t1_minutes": 2100,
  "t1_goals_per90": 0.55,
  "t1_assists_per90": 0.21,
  "t1_bps_per90": 6.2,
  "career_minutes_before_transfer": 6000,
  "selling_club_pts_t1": 61
}
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "player_id": "rasmus_hojlund",
      "player_name": "Rasmus Hojlund",
      "season": "2023-2024",
      "similarity_score": 0.88,
      "position": "Forward",
      "feature_coverage": 1.0,
      "historical_transfer_fee": 65000000.0
    }
  ]
}
```

---

## 5. Simulation & Direct Prediction

### 5.1 What-If Simulation
`POST /simulate`

Run a what-if scenario by modifying specific features of a player and computing the resulting valuation difference.

**Body (JSON):**
```json
{
  "player_id": "bruno_fernandes",
  "season": "2019-2020",
  "changes": {
    "t1_goals_per90": 0.85
  }
}
```

**Response (200 OK):**
```json
{
  "player_id": "bruno_fernandes",
  "baseline": {
    "prediction": 28000000.0,
    "lower_bound": 15000000.0,
    "upper_bound": 41000000.0
  },
  "scenario": {
    "prediction": 33500000.0,
    "lower_bound": 20500000.0,
    "upper_bound": 46500000.0
  },
  "absolute_change": 5500000.0,
  "percentage_change": 19.5,
  "changed_features": {
    "t1_goals_per90": 0.85
  },
  "warnings": []
}
```

### 5.2 Direct Prediction
`POST /predict`

Evaluate a raw feature dictionary directly through the production model.

**Body (JSON):**
`{"t1_minutes": 1500, "age_at_transfer": 24, ...}`

**Response (200 OK):**
```json
{
  "prediction": 25000000.0,
  "lower_bound": 12000000.0,
  "upper_bound": 38000000.0,
  "model_information": "weighted_ensemble",
  "uncertainty_information": "conformal_prediction",
  "feature_coverage": 1.0,
  "warnings": []
}
```

---

## 6. Transfers & Market Analysis

### 6.1 Transfer Search
`GET /transfers`

Query the canonical transfer database.

**Parameters (Query):**
- `season`
- `club`
- `player`
- `position`
- `min_fee`
- `max_fee`
- `limit`
- `offset`

**Response (200 OK):**
```json
{
  "items": [
    {
      "player_id": "...",
      "player_name": "...",
      "season_id": "...",
      "transfer_type": "Purchase",
      "fee_gbp": 50000000.0,
      "buyer_club": "...",
      "seller_club": "..."
    }
  ],
  "total": 500,
  "limit": 20,
  "offset": 0
}
```

### 6.2 Market Analysis
`GET /market-analysis`

Retrieve historical market statistics.

**Parameters (Query):**
- `season`
- `position`

**Response (200 OK):**
```json
{
  "total_transfers": 1500,
  "disclosed_transfers": 850,
  "median_fee": 8500000.0,
  "mean_fee": 12500000.0
}
```

---

## 7. Model Metadata

### 7.1 Model Info
`GET /models`

Retrieve metadata regarding the frozen Phase 12 machine learning artifacts serving the API.

**Response (200 OK):**
```json
{
  "production_model": "weighted_ensemble",
  "candidate_models": ["Ridge", "RandomForest", "XGBoost"],
  "ensemble_information": {
    "weights": {"Ridge": 0.3, "RandomForest": 0.4, "XGBoost": 0.3},
    "method": "weighted_average"
  },
  "validation_methodology": "walk_forward_cv",
  "metrics": {
    "MAE": 4500000.0,
    "RMSE": 6000000.0,
    "R2": 0.72,
    "median_absolute_error": 3200000.0
  },
  "uncertainty_methodology": "conformal_prediction",
  "training_period": "2010-2021",
  "final_holdout_period": "2022-2023"
}
```
