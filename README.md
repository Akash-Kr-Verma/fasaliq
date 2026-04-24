# FasalIQ: AI-Powered Agricultural Intelligence Platform

FasalIQ is a comprehensive agricultural decision-support system designed to empower farmers and government administrators with real-time data intelligence. The platform leverages Machine Learning to provide personalized crop recommendations, detect supply-demand anomalies, and stabilize market prices through data-driven interventions.

## 🚀 Key Features

### 👨‍🌾 For Farmers
- **CRISP Recommendation Engine**: A RandomForest-powered scoring system that suggests the most profitable and sustainable crops based on regional soil, climate, and historical market data.
- **Real-time Market Insights**: Access to live MSP (Minimum Support Price) vs. Market Price analytics to help farmers decide when and where to sell.
- **Surplus Alerts**: Early warning system for potential market gluts to prevent price crashes at the local level.

### 🏛️ For Government & Administrators
- **Maharashtra State Heatmap**: Division-level visualization of agricultural health, risk levels, and top-producing crops across the state.
- **AI Anomaly Detection**: Automated classification of crop failures and production anomalies (e.g., heatstroke, irrigation issues) using specialized ML pipelines.
- **Supply-Demand Gap Analysis**: Granular tracking of crop supply vs. buyer demand at the district level.
- **Cross-District Matchmaking**: Intelligent routing of surplus produce from high-supply districts to high-demand areas.

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python), PostgreSQL (SQLAlchemy), Docker.
- **Machine Learning**: Scikit-Learn (RandomForest), Databricks (Training Pipeline), serialized PKL models.
- **Admin Dashboard**: React.js with interactive visualizations (State Heatmaps, Analytics Charts).
- **Deployment**: Render (Auto-CI/CD), Docker Compose for local development.

## 📁 Project Structure

```text
├── admin-dashboard/    # React-based administration portal
├── backend/            # FastAPI core logic & ML models
│   ├── app/
│   │   ├── api/        # RESTful endpoints (Admin, CRISP, Data)
│   │   ├── crisp/      # ML Scorers & Anomaly Classifiers
│   │   └── models/     # Database schemas
│   └── tests/          # Verification scripts
├── android-app/        # Mobile application for farmers (In development)
├── docker-compose.yml  # Local orchestration
└── render.yaml         # Cloud deployment configuration
```

## 📅 Recent Updates (April 24, 2026)
- **Upgraded CRISP Engine**: Migrated from linear scoring to a production-ready RandomForest machine learning pipeline.
- **State-wide Intelligence**: Implemented the Maharashtra Division Heatmap for revenue-division level tracking.
- **Anomaly AI**: Launched a specialized classifier for granular crop failure diagnosis.
- **Price Analytics**: Integrated live MSP vs. Market Price tracking to trigger government intervention alerts.

## 🚦 Getting Started

### Local Development
1. Clone the repository.
2. Run `docker-compose up --build` to start the backend and database.
3. Access the API documentation at `http://localhost:8000/docs`.

### Deployment
The project is configured for automatic deployment to **Render**. Any push to the `master` branch triggers a new build and deployment cycle via `render.yaml`.

---
*Empowering Indian Agriculture through Data Intelligence.*
