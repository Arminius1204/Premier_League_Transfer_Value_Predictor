# Architecture

## High-Level Architecture Overview

The system is composed of a Next.js frontend, a Python FastAPI backend, a PostgreSQL relational database, and an advanced Machine Learning pipeline.

### 1. Frontend
- **Framework:** Next.js
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Visualization:** Modern charting/visualization library (e.g., Recharts, Chart.js, or D3)
- **Role:** Provide an interactive user interface for scouts and analysts, displaying player valuations, SHAP explainability plots, similarity comparisons, and the dedicated Manchester United scouting module.

### 2. Backend
- **Framework:** Python / FastAPI
- **Role:** Serve RESTful APIs to the frontend. It will interact with the database to fetch player data and communicate with the ML inference modules to generate on-the-fly valuations, what-if simulations, and similarity scores.

### 3. Machine Learning (ML) Pipeline
- **Core Libraries:** pandas, numpy, scikit-learn
- **Algorithms:** XGBoost, LightGBM, at least 5 regression models, Ensemble valuation. PyTorch/TensorFlow (only where genuinely useful, e.g., deep embeddings for similarity).
- **Explainability:** SHAP (Shapley Additive exPlanations) for model interpretability.
- **Role:** Handle data collection, cleaning, validation, feature engineering, model training, evaluation, explainability, similarity search, and prediction with uncertainty.

### 4. Database
- **Technology:** PostgreSQL / Supabase
- **Role:** Store raw ingested datasets, processed unified datasets, model metadata, historical transfer records, and player profiles. 

## Component Interaction
1. Data pipelines ingest and preprocess various football datasets, saving unified views into PostgreSQL.
2. The ML pipeline trains models and stores serialized models/artifacts.
3. The FastAPI backend loads models and connects to the PostgreSQL database.
4. The Next.js frontend queries the FastAPI backend for data, predictions, and simulations.
