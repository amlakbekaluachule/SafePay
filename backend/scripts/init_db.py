"""Initialize database and create tables."""
from app.database import Base, engine
from app.models import Transaction, Prediction, AuditLog

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

