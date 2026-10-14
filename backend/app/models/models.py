from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    date_of_birth = Column(Date)
    average_cycle_length = Column(Integer, default=28)
    average_period_length = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    notify_email = Column(String, nullable=True)   # recipient email for health updates
    notify_name = Column(String, nullable=True)    # recipient name
    email_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cycles = relationship("Cycle", back_populates="user", cascade="all, delete-orphan")
    symptoms = relationship("Symptom", back_populates="user", cascade="all, delete-orphan")
    journals = relationship("Journal", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Cycle(Base):
    __tablename__ = "cycles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    cycle_length = Column(Integer)          # days until next period
    period_length = Column(Integer)         # days of bleeding
    flow_intensity = Column(String)         # light / medium / heavy
    notes = Column(Text)
    ai_advice = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="cycles")


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    logged_date = Column(Date, nullable=False)
    symptom_type = Column(String, nullable=False)   # cramps, headache, bloating …
    severity = Column(Integer)                       # 1-10
    notes = Column(Text)
    ai_advice = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="symptoms")


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entry_date = Column(Date, nullable=False)
    mood = Column(String)           # happy / sad / anxious / calm …
    mood_score = Column(Integer)    # 1-10
    energy_level = Column(Integer)  # 1-10
    content = Column(Text)
    ai_advice = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="journals")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    predicted_start_date = Column(Date, nullable=False)
    predicted_end_date = Column(Date)
    confidence_score = Column(Float)
    predicted_cycle_length = Column(Integer)
    model_version = Column(String, default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)   # user / assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_history")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String)  # period_alert / pms_alert / health_tip
    is_read = Column(Boolean, default=False)
    scheduled_for = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
