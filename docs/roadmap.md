# Project Roadmap

## Phase 1: Architecture & Foundation (Current)
- [x] Define project scope and core objectives.
- [x] Design system architecture.
- [x] Establish data strategy and registry schema.
- [x] Define ML methodology and data leakage policies.
- [x] Initialize repository structure (`/backend`, `/frontend`, `/ml`, etc.).

## Phase 2: Data Sourcing & Ingestion Pipeline
- [ ] Identify and document specific datasets (Transfermarkt, FBref, etc.) in the Dataset Registry.
- [ ] Develop data collection scripts (`ml/data_collection`).
- [ ] Implement data cleaning and standardization (`ml/data_cleaning`).
- [ ] Set up PostgreSQL/Supabase database schema.
- [ ] Construct the unified historical football dataset.

## Phase 3: Machine Learning Development
- [ ] Conduct exploratory data analysis (EDA) in `/notebooks`.
- [ ] Develop robust feature engineering pipelines (per-90, rolling stats).
- [ ] Train and evaluate 5+ baseline regression models.
- [ ] Develop the Ensemble valuation model.
- [ ] Implement uncertainty estimation (Prediction ranges).
- [ ] Integrate SHAP for explainable AI.
- [ ] Build player similarity algorithms.

## Phase 4: Backend API Development
- [ ] Set up Python FastAPI project structure.
- [ ] Create endpoints for player search, valuation, similarity, and simulations.
- [ ] Connect FastAPI to PostgreSQL and load ML models.

## Phase 5: Frontend Development (Next.js)
- [ ] Scaffold Next.js + Tailwind CSS project.
- [ ] Build dashboard for player valuation and SHAP visualizations.
- [ ] Build similarity comparison and What-If simulation UI.
- [ ] Develop the dedicated Manchester United analytics/scouting module.

## Phase 6: Testing, Refinement & Deployment
- [ ] End-to-end testing (frontend, backend, ML predictions).
- [ ] Refine models based on predicted-vs-actual analysis.
- [ ] Finalize documentation.
- [ ] (Optional) Deploy to cloud infrastructure.
