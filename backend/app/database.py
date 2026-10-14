from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_schema():
    inspector = inspect(engine)
    if "cycles" in inspector.get_table_names():
        cycle_columns = {col["name"] for col in inspector.get_columns("cycles")}
        if "ai_advice" not in cycle_columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE cycles ADD COLUMN ai_advice TEXT"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
