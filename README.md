# SafePay - Real-Time Credit Card Fraud Detection Platform

A production-grade, auditable, and explainable fraud detection system with real-time ML inference and professional analytics dashboard.

## Architecture

- **ML API**: FastAPI-based real-time fraud detection service with model explainability
- **Analytics Dashboard**: React/TypeScript dashboard for monitoring and analytics
- **ML Pipeline**: Training pipeline with feature engineering and SHAP-based explainability
- **Data Pipeline**: Real-time transaction ingestion and feature computation
- **Database**: PostgreSQL for transactions, predictions, and audit logs

## Features

- Real-time fraud detection with sub-100ms latency
- Model explainability using SHAP values
- Comprehensive audit logging
- Professional analytics dashboard
- Production-ready with Docker deployment
- Feature store for efficient inference

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)
- Node.js 18+ (for frontend development)

### Using Docker Compose

```bash
docker-compose up --build
```

This will start:
- ML API on `http://localhost:8000`
- Dashboard on `http://localhost:3000`
- PostgreSQL on `localhost:5432`

### Local Development

#### Backend (ML API)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend (Dashboard)
```bash
cd frontend
npm install
npm start
```

#### Database Setup
```bash
# Using Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# Run migrations
cd backend
alembic upgrade head
```

## API Documentation

Once the API is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
safepay/
├── backend/              # ML API and training pipeline
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── ml/          # ML models and inference
│   │   ├── services/    # Business logic
│   │   └── main.py      # FastAPI app
│   ├── training/        # Model training scripts
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── frontend/            # React dashboard
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/   # API clients
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Model Training

Train a new fraud detection model:

```bash
cd backend
python training/train_model.py
```

The model will be saved to `backend/models/fraud_detector.pkl` and feature metadata to `backend/models/feature_metadata.json`.

## License

MIT

