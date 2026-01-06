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
