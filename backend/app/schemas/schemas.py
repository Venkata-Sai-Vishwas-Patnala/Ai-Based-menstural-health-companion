from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ──────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    average_cycle_length: int
    average_period_length: int
    notify_email: Optional[str]
    notify_name: Optional[str]
    email_notifications: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    average_cycle_length: Optional[int] = None
    average_period_length: Optional[int] = None
    notify_email: Optional[str] = None
    notify_name: Optional[str] = None
    email_notifications: Optional[bool] = None

    @field_validator('date_of_birth', mode='before')
    @classmethod
    def empty_date_to_none(cls, v):
        return None if v == '' else v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Cycle ─────────────────────────────────────────────────────────────────────
class CycleCreate(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    flow_intensity: Optional[str] = None
    notes: Optional[str] = None


class CycleOut(CycleCreate):
    id: int
    user_id: int
    cycle_length: Optional[int]
    period_length: Optional[int]
    ai_advice: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Symptom ───────────────────────────────────────────────────────────────────
class SymptomCreate(BaseModel):
    logged_date: date
    symptom_type: str
    severity: Optional[int] = None
    notes: Optional[str] = None


class SymptomOut(SymptomCreate):
    id: int
    user_id: int
    ai_advice: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Journal ───────────────────────────────────────────────────────────────────
class JournalCreate(BaseModel):
    entry_date: date
    mood: Optional[str] = None
    mood_score: Optional[int] = None
    energy_level: Optional[int] = None
    content: Optional[str] = None


class JournalOut(JournalCreate):
    id: int
    user_id: int
    ai_advice: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Prediction ────────────────────────────────────────────────────────────────
class PredictionOut(BaseModel):
    id: int
    predicted_start_date: date
    predicted_end_date: Optional[date]
    confidence_score: Optional[float]
    predicted_cycle_length: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Chat ──────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str


class ChatMessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Notification ──────────────────────────────────────────────────────────────
class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    notification_type: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
