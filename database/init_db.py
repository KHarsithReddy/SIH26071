from database.database import engine, Base
from database.models import PredictionHistory

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")