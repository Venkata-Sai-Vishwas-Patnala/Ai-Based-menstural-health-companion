from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.services.scheduler import start_scheduler, stop_scheduler
from app.api import auth, user, cycle, symptoms, journal, prediction, chatbot, diet, analytics, notifications, export

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="AI Menstrual Health Companion",
    version="1.0.0",
    description="AI-powered menstrual health tracking platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
for router in [
    auth.router, user.router, cycle.router, symptoms.router,
    journal.router, prediction.router, chatbot.router, diet.router,
    analytics.router, notifications.router, export.router,
]:
    app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "menstrual-ai-companion"}
