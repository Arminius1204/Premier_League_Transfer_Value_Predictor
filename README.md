# ⚽ Premier League Transfer Intelligence & Player Valuation Engine

### Machine Learning • Football Analytics • Explainable AI • Transfer Intelligence • FastAPI • Next.js

A production-oriented machine learning system for **estimating Premier League player transfer fees, quantifying prediction uncertainty, explaining model decisions, finding historically similar players, and running what-if valuation scenarios.**

The system combines historical football performance, transfer-market data, club context, player characteristics, and machine learning into an interactive football intelligence platform.

---

## 🚀 Overview

Football transfer fees are influenced by far more than goals and appearances.

Age, recent performance, playing position, experience, club context, historical market conditions, and many unobserved factors can influence the eventual fee.

This project attempts to model the relationship between **pre-transfer football information** and **actual historical transfer fees** while explicitly accounting for uncertainty.

The system answers questions such as:

> **"What transfer fee does the model estimate for this player?"**

> **"How uncertain is that estimate?"**

> **"Which historical players have similar performance profiles?"**

> **"How does the model's estimate compare with the historical market fee?"**

> **"What happens to the model estimate if a player's performance profile changes?"**

---

# 🎯 Key Features

## 💰 ML Transfer Valuation

Predicts historical Premier League transfer fees using multiple machine learning models.

Models evaluated include:

- Linear Regression
- Ridge Regression
- Random Forest
- Gradient Boosting
- XGBoost
- MLP / Neural Network

The final production system uses the validated Phase 12 ensemble architecture.

---

## 📊 Uncertainty-Aware Predictions

Instead of producing only a single number, the system generates a prediction interval using empirical conformal prediction methodology.

Example:

```text
Estimated Transfer Fee

£28.4M

Prediction Interval

£15.4M ───────── £41.3M
```

This reflects the fact that football transfers contain substantial uncertainty that cannot be captured by player statistics alone.

The interval represents model uncertainty based on the project's historical calibration methodology; it is **not a guarantee of the eventual market fee**.

---

## 🧠 Explainable AI

The system provides model-level explanations for individual valuation estimates.

Users can inspect influential factors such as:

- Age
- Goals per 90
- BPS per 90
- Career experience
- Selling-club context
- Other validated model features

The system distinguishes between **model contribution** and causal interpretation.

---

## 👥 Player Similarity Engine

The project includes a performance-based player similarity engine using:

**Cosine similarity + standardized feature representations**

Similarity can incorporate validated performance characteristics such as:

- Minutes
- Goals per 90
- Assists per 90
- BPS per 90
- Career minutes
- Club context

Transfer fee and player ID are explicitly excluded from the similarity representation.

Players are compared using position-aware filtering.

Example:

```text
Player X

Similar Players

1. Player A     92.1%
2. Player B     89.7%
3. Player C     87.4%
4. Player D     85.9%
5. Player E     84.6%
```

Historical transfer fees are displayed only as contextual information and are **not used to calculate similarity**.

---

## 🔬 What-If Valuation Simulator

Users can modify supported player characteristics and observe how the frozen valuation model responds.

For example:

```text
Baseline

Goals / 90       0.42
BPS / 90         6.10

Estimated Fee    £28.4M
```

Scenario:

```text
Goals / 90       0.55
BPS / 90         6.10

Estimated Fee    £31.1M
```

The system reports:

- Baseline prediction
- Scenario prediction
- Absolute change
- Percentage change
- Prediction intervals
- Changed features
- Out-of-distribution warnings

These are **model sensitivity scenarios**, not causal predictions.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────────┐
                         │ Historical Football Data │
                         │ Transfer Data            │
                         │ Match Data               │
                         │ Player Statistics        │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Entity Resolution       │
                         │ Data Cleaning            │
                         │ Temporal Validation     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Feature Engineering     │
                         │ Performance Features    │
                         │ Club Context            │
                         │ Player Characteristics  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ ML Model Development    │
                         │                         │
                         │ Ridge                   │
                         │ Random Forest           │
                         │ XGBoost                 │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Frozen Production Model │
                         │ Weighted Ensemble       │
                         └────────────┬────────────┘
                                      │
                 ┌────────────────────┼────────────────────┐
                 │                    │                    │
                 ▼                    ▼                    ▼
        ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
        │ Explainability │   │ Uncertainty    │   │ Player         │
        │                │   │                │   │ Similarity     │
        └────────────────┘   └────────────────┘   └────────────────┘
                 │                    │                    │
                 └────────────────────┼────────────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ What-If Valuation       │
                         │ Simulator                │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ FastAPI Backend         │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Next.js Frontend        │
                         │ Football Intelligence   │
                         │ Platform                │
                         └─────────────────────────┘
```

---

# 📚 Data

The project integrates multiple historical football data sources.

### Transfer Data

**Transfermarkt**

Used for:

- historical transfer events
- transfer fees
- player information
- positions
- transfer context

### Match & Club Data

**football-data.co.uk**

Used for:

- historical Premier League match results
- club performance
- points
- goal difference
- season-level context

### Player Performance Data

**Fantasy Premier League Historical Archive**

Used for historical player performance statistics across multiple seasons.

Features include relevant:

- minutes
- goals
- assists
- bonus points
- per-90 metrics

### Historical Coverage

The current ML dataset covers:

```text
2018/19
2019/20
2020/21
2021/22
2022/23
2023/24
```

The final modeling dataset contains **781 eligible disclosed permanent transfer events** across the six-season period.

---

# 🔐 Temporal Leakage Prevention

Temporal leakage is one of the most important methodological concerns in transfer prediction.

The system therefore follows strict temporal rules.

For a transfer occurring during season `T`:

```text
Transfer
   ↑
Information available before transfer
   ↑
Previous completed season
```

Features are restricted to information available before the transfer.

The system avoids using:

- destination-club outcome information
- future transfer history
- future performance
- current market values without historical timestamps
- post-transfer statistics
- player identity as a predictive feature

For mid-season transfers, end-of-season statistics from that same season are not blindly used.

---

# 🧪 Machine Learning Methodology

The prediction target is:

```text
Actual disclosed transfer fee in GBP
```

Each eligible transfer event represents a modeling observation.

The project evaluated multiple model families:

| Model | Purpose |
|---|---|
| Linear Regression | Interpretable baseline |
| Ridge Regression | Regularized linear model |
| Random Forest | Non-linear ensemble |
| Gradient Boosting | Boosted decision trees |
| XGBoost | Advanced gradient boosting |
| MLP | Neural network benchmark |

The final production system was selected using historical chronological validation rather than the final holdout set.

---

# 📈 Validation Strategy

Random train/test splitting was deliberately avoided.

Instead, the project uses **chronological validation**.

Conceptually:

```text
2018 ──────► 2021
              │
              ▼
          Validation

2018 ───────────► 2022
                    │
                    ▼
                Validation

...

Historical Data
      │
      ▼
Final Model
      │
      ▼
2023/24 Holdout
```

The final 2023/24 holdout was kept isolated until final evaluation.

---

# 🏆 Final Model

The Phase 12 production architecture uses a weighted ensemble of:

- Ridge Regression
- XGBoost
- Random Forest

The ensemble weights were determined using historical out-of-fold validation.

The final 2023/24 holdout was excluded from ensemble weight selection.

### Final Holdout

The final holdout consisted of:

**151 transfer events from 2023/24.**

Representative final performance:

```text
MAE              ≈ £13.23M
R²               ≈ 0.028
Median AE        ≈ £8.74M
```

The relatively modest R² is an important limitation and is reported transparently.

Transfer fees are heavily influenced by factors that are difficult or impossible to observe from public historical player statistics, including negotiations, contract situations, bidding competition, club finances, and other market conditions.

---

# 📐 Uncertainty

The project uses empirical conformal prediction based on historical out-of-fold residuals.

Current calibrated intervals include approximately:

```text
80% interval
± £12.95M

90% interval
± £21.43M
```

These intervals are intended to communicate uncertainty rather than create false precision.

---

# 🔎 Model vs Market

The system also calculates:

```text
Transfer Value Gap
=
Model Predicted Fee − Actual Transfer Fee
```

This is deliberately described as a **model-market discrepancy**.

The system does not automatically label a player as "overvalued" or "undervalued."

Instead, it reports the numerical difference between:

```text
Model Estimate
        vs
Historical Market Fee
```

This distinction is important because the model does not observe every factor influencing an actual transfer.

---

# 🧩 Backend

The backend is built with **FastAPI**.

It exposes analytical services including:

```text
GET  /health

GET  /players
GET  /players/{id}

GET  /players/{id}/valuation
GET  /players/{id}/explanation
GET  /players/{id}/similar

POST /similarity/profile
POST /predict
POST /simulate

GET  /transfers
GET  /market-analysis
GET  /models
```

The API uses typed Pydantic schemas and centralized service layers.

---

# 🖥️ Frontend

The frontend is built with:

- Next.js
- React
- TypeScript
- Tailwind CSS

The application provides interfaces for:

- Player discovery
- Player profiles
- Transfer valuation
- Explainable predictions
- Similar player discovery
- Player comparison
- What-if simulation
- Historical transfer analysis
- Market analysis
- Model methodology

The frontend communicates with the FastAPI backend rather than directly accessing the ML artifacts.

---

# 📁 Project Structure

```text
premier-league-transfer-ai/
│
├── backend/
│   └── app/
│       ├── api/
│       ├── schemas/
│       ├── services/
│       └── main.py
│
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
│
├── ml/
│   ├── data_collection/
│   ├── data_cleaning/
│   ├── data_validation/
│   ├── data_parsing/
│   ├── entity_resolution/
│   ├── feature_engineering/
│   ├── training/
│   ├── evaluation/
│   ├── explainability/
│   ├── similarity/
│   ├── prediction/
│   └── uncertainty/
│
├── data/
│   ├── raw/
│   ├── parsed/
│   ├── processed/
│   └── entity_resolution/
│
├── models/
│   └── v3/
│
├── tests/
│
├── notebooks/
│
├── docs/
│
└── scripts/
```

---

# 🧪 Testing

The project maintains automated testing across the ML and application layers.

Current validation includes:

- Data validation
- Feature engineering tests
- Temporal leakage checks
- Model integrity tests
- Ensemble tests
- Conformal interval tests
- Similarity tests
- What-if simulation tests
- FastAPI API tests

The current backend/application validation suite contains:

```text
62 tests passing
```

The project treats regression testing as a requirement before advancing development phases.

---

# ⚙️ Local Setup

## 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd premier-league-transfer-ai
```

---

# 2. Backend Setup

Create/activate your Python environment.

Example:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
python -m uvicorn backend.app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

---

# 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
```

Create:

```text
.env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start Next.js:

```bash
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 4. Run Tests

From the project root:

```bash
pytest -q
```

For frontend validation:

```bash
cd frontend
npm run build
```

---

# ⚠️ Important

The FastAPI backend must be running for the Next.js frontend to retrieve live analytical data.

Start:

```bash
python -m uvicorn backend.app.main:app --reload
```

before using the frontend.

---

# 🔬 Limitations

This system is a research and analytical platform rather than a perfect transfer-price oracle.

Important limitations include:

### Limited observable variables

Public datasets do not capture every factor influencing transfer negotiations.

Examples include:

- contract duration
- release clauses
- agent negotiations
- bidding competition
- club finances
- player demand
- strategic importance
- confidential negotiations

### Historical data coverage

Some historical player characteristics and performance features have incomplete coverage.

### Position / demographic sparsity

Some early historical records have incomplete canonical position and demographic joins.

### Transfer-market distribution

Transfer fees are heavily right-skewed, with a small number of extremely expensive transfers producing large absolute errors.

### Model interpretation

Feature contributions describe model behavior.

They should not automatically be interpreted as causal relationships.

### Uncertainty

Prediction intervals communicate statistical uncertainty based on historical calibration. They do not guarantee that the actual transfer fee will fall inside the interval.

---

# 🛠️ Development Roadmap

### Completed

- [x] Project architecture
- [x] Historical data acquisition
- [x] Data parsing
- [x] Entity resolution
- [x] Unified football data warehouse
- [x] Temporal feature engineering
- [x] Multi-model experimentation
- [x] Six-season ML dataset
- [x] Chronological validation
- [x] Production ensemble
- [x] Explainable AI
- [x] Conformal uncertainty
- [x] Player similarity engine
- [x] What-if valuation simulator
- [x] FastAPI backend
- [x] Next.js frontend

### Future Extensions

- [ ] Expanded historical player demographics
- [ ] Additional football performance sources
- [ ] More advanced temporal valuation models
- [ ] Market trend forecasting
- [ ] Club-specific scouting workflows
- [ ] Production deployment
- [ ] Real-time data ingestion
- [ ] Additional league support

---

# 🎓 Research / Engineering Highlights

This project demonstrates practical experience with:

### Machine Learning

- Regression
- Ensemble learning
- Regularization
- Gradient boosting
- Neural networks
- Out-of-fold validation
- Chronological validation
- Conformal prediction

### Data Engineering

- Multi-source data integration
- Entity resolution
- Historical data normalization
- Currency normalization
- Temporal feature engineering
- Data validation
- Data lineage

### Explainable AI

- Feature contribution analysis
- Model-market discrepancy analysis
- Uncertainty quantification

### Software Engineering

- Python
- FastAPI
- Next.js
- React
- TypeScript
- REST APIs
- Pydantic
- Automated testing
- Modular service architecture

---

# 👨‍💻 Author

**Akshat Raj**

B.Sc. Computer Science & Mathematics  
Christ University, Bengaluru

Interested in:

- Machine Learning
- Artificial Intelligence
- Data Science
- Full-Stack Development
- Football Analytics

---

# 📄 Project Documentation

Detailed technical documentation is available in the `docs/` directory, including:

```text
Phase 12 — Ensemble & Explainability
Phase 13 — Similarity & What-If Engine
Phase 14A — FastAPI Backend
Phase 14B — Next.js Frontend
```

---

# ⭐ Why This Project?

Most football analytics projects stop at dashboards and descriptive statistics.

This project attempts to build a complete pipeline:

```text
Raw Football Data
       ↓
Data Engineering
       ↓
Temporal Feature Engineering
       ↓
Machine Learning
       ↓
Uncertainty Quantification
       ↓
Explainable AI
       ↓
Player Similarity
       ↓
What-If Simulation
       ↓
FastAPI
       ↓
Interactive Next.js Application
```

The objective is not simply to predict a transfer fee.

It is to build an **explainable, uncertainty-aware football transfer intelligence system** that connects machine learning research with a usable software product.

---

## ⭐ If you find the project interesting

Feel free to explore the repository, review the methodology, or build on the system.

**Built with Python, Machine Learning, FastAPI, Next.js, and a slightly unhealthy obsession with football transfer fees. ⚽**
