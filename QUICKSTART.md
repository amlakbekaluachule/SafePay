# SafePay Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Docker (Recommended)

```bash
# 1. Start all services
docker-compose up --build

# 2. In another terminal, train the model
docker-compose exec backend python training/train_model.py

# 3. Access the services
# - Dashboard: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - API: http://localhost:8000/api/v1
```

### Option 2: Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL (or use Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# Initialize database
python scripts/init_db.py

# Train model
python training/train_model.py

# Start API
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## 📝 Test the API

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health/

# Test fraud prediction
curl -X POST http://localhost:8000/api/v1/predictions/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "card_id": "card_456",
    "amount": 150.50,
    "merchant_id": "merchant_789",
    "merchant_category": "electronics",
    "location_country": "US",
    "threshold": 0.5,
    "include_explainability": true
  }'
```

Or use the test script:
```bash
cd backend
pip install requests
python test_api.py
```

## 📊 Using the Dashboard

1. Open http://localhost:3000
2. View real-time fraud detection metrics
3. Browse transactions and see predictions
4. Analyze trends in the Analytics tab

## 🔧 Common Issues

**Model not found:**
- Run: `python training/train_model.py`

**Database connection error:**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env

**CORS errors:**
- Update CORS_ORIGINS in backend config
- Check REACT_APP_API_URL in frontend

## 📚 Next Steps

- Read [README.md](README.md) for architecture details
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Explore API docs at http://localhost:8000/docs

