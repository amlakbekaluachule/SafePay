# SafePay Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- Python 3.9+ (for local development)
- Node.js 18+ (for frontend development)
- PostgreSQL 15+ (if running database separately)

## Quick Start with Docker

1. **Clone and navigate to the project:**
   ```bash
   cd safepay
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database on port 5432
   - ML API on port 8000
   - Dashboard on port 3000

3. **Train the initial model:**
   ```bash
   docker-compose exec backend python training/train_model.py
   ```

4. **Access the services:**
   - Dashboard: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - API: http://localhost:8000/api/v1

## Local Development Setup

### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Set up database:**
   ```bash
   # Using Docker for PostgreSQL
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
   
   # Or use existing PostgreSQL instance
   # Update DATABASE_URL in .env
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Train the model:**
   ```bash
   python training/train_model.py
   ```

7. **Start the API:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set environment variables (optional):**
   ```bash
   # Create .env file
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

## Production Deployment

### Backend Deployment

1. **Build Docker image:**
   ```bash
   cd backend
   docker build -t safepay-api:latest .
   ```

2. **Run container:**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e DATABASE_URL=postgresql://user:pass@host:5432/safepay \
     -e MODEL_PATH=models/fraud_detector.pkl \
     -v $(pwd)/models:/app/models \
     safepay-api:latest
   ```

### Frontend Deployment

1. **Build production bundle:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve with nginx or similar:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       root /path/to/frontend/build;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Environment Variables

### Backend

- `DATABASE_URL`: PostgreSQL connection string
- `MODEL_PATH`: Path to trained model file
- `FEATURE_METADATA_PATH`: Path to feature metadata JSON
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS`: Comma-separated list of allowed origins

### Frontend

- `REACT_APP_API_URL`: Backend API URL

## Database Migrations

Run migrations:
```bash
cd backend
alembic upgrade head
```

Create new migration:
```bash
alembic revision --autogenerate -m "description"
```

## Monitoring and Logging

- API logs are output to stdout/stderr
- Use Docker logs: `docker-compose logs -f backend`
- For production, configure centralized logging (e.g., ELK stack, CloudWatch)

## Scaling

- **API**: Use a load balancer (nginx, HAProxy) with multiple API instances
- **Database**: Use read replicas for analytics queries
- **Frontend**: Use CDN for static assets

## Security Considerations

1. **API Security:**
   - Add authentication/authorization (JWT tokens)
   - Use HTTPS in production
   - Rate limiting
   - Input validation

2. **Database Security:**
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access

3. **Model Security:**
   - Store models securely
   - Version control for models
   - Access control for model updates

## Troubleshooting

### Database Connection Issues
- Check DATABASE_URL format
- Verify PostgreSQL is running
- Check network connectivity

### Model Not Found
- Train the model: `python training/train_model.py`
- Verify MODEL_PATH in environment variables
- Check file permissions

### CORS Errors
- Update CORS_ORIGINS in backend config
- Verify frontend API_URL matches backend

