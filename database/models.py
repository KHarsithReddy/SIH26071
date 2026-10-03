from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime

from database.database import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)

    prediction_type = Column(String(50), nullable=False)

    risk_level = Column(String(50), nullable=False)

    predicted_class = Column(Integer, nullable=False)

    confidence_score = Column(Float, nullable=False)

    probabilities = Column(JSON, nullable=True)

    overall_status = Column(String(50), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )