# SafePay Architecture

## System Overview

SafePay is a real-time credit card fraud detection platform built with production-grade practices. The system consists of three main components:

1. **ML API (Backend)**: FastAPI-based service for real-time fraud detection
2. **Analytics Dashboard (Frontend)**: React/TypeScript dashboard for monitoring
3. **Database**: PostgreSQL for persistent storage

## Component Details

### ML API (Backend)

**Technology Stack:**
- FastAPI for high-performance async API
- XGBoost for fraud detection model
- SHAP for model explainability
- SQLAlchemy for database ORM
- Alembic for database migrations

**Key Components:**

1. **Fraud Detector** (`app/ml/fraud_detector.py`)
   - Loads trained XGBoost model
   - Performs real-time inference
   - Computes SHAP values for explainability
   - Sub-100ms inference latency

2. **Feature Engineering** (`app/ml/feature_engineering.py`)
   - Extracts 19 features from transaction data
   - Includes temporal, behavioral, and contextual features
   - Supports user history for advanced features

3. **API Endpoints** (`app/api/`)
   - `/predictions/` - Real-time fraud prediction
   - `/transactions/` - Transaction management
   - `/analytics/` - Analytics and metrics
   - `/health/` - Health checks

4. **Services Layer** (`app/services/`)
   - TransactionService - Transaction operations
   - PredictionService - Prediction management
   - AuditService - Audit logging

5. **Database Models** (`app/models/`)
   - Transaction - Transaction records
   - Prediction - Fraud predictions with explainability
   - AuditLog - System audit trail

### Analytics Dashboard (Frontend)

**Technology Stack:**
- React 18 with TypeScript
- Chart.js for visualizations
- Axios for API communication
- React Router for navigation

**Key Features:**

1. **Dashboard** (`components/Dashboard.tsx`)
   - Real-time statistics
   - Model performance metrics
   - Recent transactions overview

2. **Transactions** (`components/Transactions.tsx`)
   - Transaction listing with filters
   - Detailed transaction view
   - Fraud prediction details with explainability

3. **Analytics** (`components/Analytics.tsx`)
   - Fraud trends over time
   - Transaction volume charts
   - Model metrics visualization

### Database Schema

**Tables:**

1. **transactions**
   - Stores all transaction data
   - Indexed on user_id, card_id, timestamp
   - Includes raw features for audit

2. **predictions**
   - Stores fraud predictions
   - Includes SHAP values and feature contributions
   - Links to transactions via foreign key
   - Supports ground truth labels

3. **audit_logs**
   - Complete audit trail
   - Tracks all system actions
   - Includes IP addresses and user agents

## Data Flow

### Prediction Flow

1. Transaction arrives at `/api/v1/predictions/`
2. TransactionService creates transaction record
3. FeatureEngineer extracts features (with user history if available)
4. FraudDetector performs inference
5. SHAP values computed for explainability
6. Prediction stored in database
7. Audit log created
8. Response returned to client

### Feature Engineering

Features extracted:
- **Basic**: amount, amount_log
- **Temporal**: hour, day_of_week, is_weekend, is_night
- **Categorical**: merchant_category, transaction_type, location_country
- **Behavioral**: transactions_24h, transactions_7d, avg_amount_7d
- **Anomaly**: location_change, unusual_merchant, amount_ratio
- **Device**: has_device_id, has_ip_address

## Model Training

The model is trained using:
- XGBoost classifier
- Synthetic data generation (replace with real data in production)
- 20,000 samples with 5% fraud rate
- Feature importance and SHAP explainability

Training script: `backend/training/train_model.py`

## Explainability

SafePay provides model explainability through:
1. **SHAP Values**: Feature-level contribution scores
2. **Feature Contributions**: Human-readable explanations
3. **Top Features**: Highlighted in dashboard

This enables:
- Regulatory compliance
- Model debugging
- Business understanding
- Trust and transparency

## Scalability Considerations

### API Scaling
- Stateless design enables horizontal scaling
- Use load balancer (nginx, HAProxy)
- Consider Redis for caching user history

### Database Scaling
- Read replicas for analytics queries
- Partitioning by timestamp for large datasets
- Connection pooling (already configured)

### Model Serving
- Current: In-process model loading
- Future: Consider dedicated model serving (TensorFlow Serving, TorchServe, or custom)

## Security

### Current Implementation
- Input validation via Pydantic
- SQL injection protection via SQLAlchemy
- CORS configuration
- Audit logging

### Production Recommendations
- Add authentication (JWT tokens)
- Rate limiting
- HTTPS/TLS
- API key management
- Database encryption at rest
- Secure model storage

## Monitoring & Observability

### Logging
- Structured logging with Python logging
- Log levels configurable
- Audit trail in database

### Metrics (Future)
- Prometheus metrics endpoint
- Custom metrics for:
  - Prediction latency
  - Fraud rate
  - Model performance
  - API throughput

### Alerting (Future)
- Fraud rate thresholds
- Model performance degradation
- System health alerts

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Docker Compose
- Single command deployment
- Development and production configurations
- Service dependencies managed

### Production
- Separate containers for each service
- Use orchestration (Kubernetes, ECS)
- CI/CD pipeline integration
- Blue-green deployments for zero downtime

## Future Enhancements

1. **Real-time Streaming**
   - Kafka/Kinesis integration
   - Stream processing pipeline

2. **Advanced ML**
   - Online learning
   - Model versioning
   - A/B testing framework

3. **Feature Store**
   - Dedicated feature store (Feast, Tecton)
   - Real-time feature serving

4. **Enhanced Dashboard**
   - Real-time WebSocket updates
   - Custom alerting rules
   - Advanced visualizations

5. **Model Monitoring**
   - Data drift detection
   - Model performance tracking
   - Automated retraining

