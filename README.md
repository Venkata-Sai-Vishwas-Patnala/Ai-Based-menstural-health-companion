# AI Menstrual Health Companion

A full-stack menstrual health tracking platform with AI-powered cycle prediction, a Gemini chatbot, symptom and mood tracking, email alerts, and PDF health reports.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Quick Start with Docker](#quick-start-with-docker)
6. [Local Development without Docker](#local-development-without-docker)
7. [Environment Variables](#environment-variables)
8. [API Reference](#api-reference)
9. [ML Prediction System](#ml-prediction-system)
10. [Email Notifications](#email-notifications)
11. [Seeding Test Data](#seeding-test-data)
12. [Security Notes](#security-notes)
13. [Disclaimer](#disclaimer)

---

## Features

| Feature             | Description                                                  |
|---------------------|--------------------------------------------------------------|
| Cycle Tracker       | Log period start/end date and flow intensity                 |
| Symptoms Tracker    | Log symptoms with severity 1-10                              |
| Mood Journal        | Track mood, energy level, and free-text journal entries      |
| AI Prediction       | RandomForest-based next period prediction with confidence    |
| Pre-period Countdown| Day-by-day advice cards for the 7 days before your period    |
| Phase Indicator     | Menstrual / Follicular / Ovulation / Luteal phase detection  |
| AI Chatbot          | Gemini-powered menstrual health assistant                    |
| Diet Guide          | Phase-based nutrition recommendations                        |
| Analytics           | Charts for cycle trends, mood trends, and symptom frequency  |
| Notifications       | Period alerts, PMS reminders, mood and symptom alerts        |
| PDF Export          | Download a full health report                                |
| Email Alerts        | SMTP-based HTML emails for period countdown and health tips  |

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Frontend   | React 18, Vite, Chart.js, react-markdown        |
| Backend    | FastAPI (Python 3.11), SQLAlchemy, Alembic      |
| Database   | PostgreSQL 16                                   |
| Cache      | Redis 7                                         |
| ML         | Scikit-learn RandomForestRegressor              |
| Auth       | JWT (python-jose) + bcrypt                      |
| Scheduler  | APScheduler                                     |
| PDF        | ReportLab                                       |
| AI Chatbot | Google Gemini API (google-generativeai)         |
| Container  | Docker + Docker Compose                         |

---

## Project Structure

```
menstrual-ai-companion/
├── backend/
│   ├── app/
│   │   ├── api/            # Route handlers (auth, cycle, symptoms, etc.)
│   │   ├── ml/             # RandomForest predictor
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # APScheduler + email service
│   │   ├── utils/          # Auth helpers, diet logic
│   │   ├── config.py       # Pydantic settings (reads .env)
│   │   ├── database.py     # SQLAlchemy engine + session
│   │   └── main.py         # FastAPI app, CORS, router registration
│   ├── ml_models/          # Trained .joblib model (generated at runtime)
│   ├── scripts/
│   │   ├── data/           # FedCycleData CSV for population prior training
│   │   ├── seed_data.py    # Seed synthetic cycles/symptoms/journals
│   │   └── train_from_csv.py  # Train model on CSV dataset
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # Sidebar, StatCard, Icons (all SVG, no emoji)
│   │   ├── context/        # AuthContext (JWT storage)
│   │   ├── pages/          # Dashboard, CycleTracker, Chatbot, etc.
│   │   ├── services/       # Axios instance with auth interceptor
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── nginx.conf          # Nginx reverse proxy config for Docker
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── .env                    # Your local secrets (never commit this)
├── .env.example            # Template — copy to .env and fill in values
├── .gitignore
└── docker-compose.yml
```

---

## Prerequisites

### For Docker setup (recommended)

- Docker Desktop 4.x or later
- Docker Compose v2 (included with Docker Desktop)

Verify installation:

```bash
docker --version
docker compose version
```

### For local development (without Docker)

- Python 3.11
- Node.js 20 and npm
- PostgreSQL 16 running locally
- Redis 7 running locally

---

## Quick Start with Docker

This is the recommended way to run the full stack.

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/menstrual-ai-companion.git
cd menstrual-ai-companion
```

### Step 2 — Create your environment file

```bash
cp .env.example .env
```

### Step 3 — Fill in required values in .env

Open `.env` in any text editor and set the following:

```
SECRET_KEY=your-random-32-character-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

All other values have working defaults for Docker. See the [Environment Variables](#environment-variables) section for the full reference.

To get a Gemini API key, visit: https://aistudio.google.com/app/apikey

### Step 4 — Build and start all services

```bash
docker compose up --build
```

This starts four containers: PostgreSQL, Redis, the FastAPI backend, and the React frontend served by Nginx.

The first build takes 3-5 minutes. Subsequent starts are faster.

### Step 5 — Open the app

| Service      | URL                          |
|--------------|------------------------------|
| Frontend     | http://localhost:9000        |
| Backend API  | http://localhost:8888        |
| API Docs     | http://localhost:8888/docs   |

### Stopping the app

```bash
docker compose down
```

To also delete the database volume (full reset):

```bash
docker compose down -v
```

### Rebuilding after code changes

```bash
# Rebuild and restart everything
docker compose up --build

# Rebuild only the backend
docker compose up --build backend

# Rebuild only the frontend
docker compose up --build frontend
```

### Viewing logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Frontend only
docker compose logs -f frontend
```

---

## Local Development without Docker

Use this if you want hot-reload for active development.

### Step 1 — Start PostgreSQL and Redis

Make sure PostgreSQL 16 and Redis 7 are running locally. Then create the database:

```bash
psql -U postgres -c "CREATE USER menstrual_user WITH PASSWORD 'menstrual_pass';"
psql -U postgres -c "CREATE DATABASE menstrual_db OWNER menstrual_user;"
```

### Step 2 — Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the project root (or export variables manually). Update `DATABASE_URL` to point to your local Postgres:

```
DATABASE_URL=postgresql://menstrual_user:menstrual_pass@localhost:5432/menstrual_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-random-32-character-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash
MODEL_DIR=./ml_models
CORS_ORIGINS=http://localhost:5173
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

The backend runs at http://localhost:8000. Tables are created automatically on first startup.

### Step 3 — Frontend setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at http://localhost:5173 and proxies all `/api` requests to the backend at port 8000.

---

## Environment Variables

| Variable                    | Required | Default                  | Description                                              |
|-----------------------------|----------|--------------------------|----------------------------------------------------------|
| DATABASE_URL                | Yes      | -                        | PostgreSQL connection string                             |
| SECRET_KEY                  | Yes      | -                        | JWT signing key, minimum 32 characters                   |
| ALGORITHM                   | No       | HS256                    | JWT algorithm                                            |
| ACCESS_TOKEN_EXPIRE_MINUTES | No       | 1440                     | JWT expiry in minutes (default 24 hours)                 |
| REDIS_URL                   | No       | redis://redis:6379/0     | Redis connection string                                  |
| GEMINI_API_KEY              | No       | -                        | Google Gemini API key (chatbot requires this)            |
| GEMINI_MODEL                | No       | gemini-2.5-flash         | Gemini model name                                        |
| MODEL_DIR                   | No       | /tmp                     | Directory to store the trained .joblib model file        |
| SMTP_HOST                   | No       | smtp.gmail.com           | SMTP server hostname                                     |
| SMTP_PORT                   | No       | 587                      | SMTP port (587 for STARTTLS)                             |
| SMTP_USER                   | No       | -                        | SMTP login email address                                 |
| SMTP_PASSWORD               | No       | -                        | SMTP password or Gmail app password                      |
| SMTP_FROM_NAME              | No       | MenstrualAI Health       | Display name in sent emails                              |
| CORS_ORIGINS                | No       | http://localhost:5173    | Comma-separated list of allowed CORS origins             |

---

## API Reference

All endpoints are prefixed with `/api/v1`.

Interactive documentation is available at `/docs` (Swagger UI) and `/redoc`.

### Authentication

| Method | Endpoint         | Auth | Description              |
|--------|------------------|------|--------------------------|
| POST   | /auth/register   | No   | Create a new account     |
| POST   | /auth/login      | No   | Login and receive JWT    |

### User

| Method | Endpoint   | Auth | Description          |
|--------|------------|------|----------------------|
| GET    | /user/me   | Yes  | Get current profile  |
| PUT    | /user/me   | Yes  | Update profile       |

### Cycle

| Method | Endpoint        | Auth | Description              |
|--------|-----------------|------|--------------------------|
| POST   | /cycle/         | Yes  | Log a new cycle          |
| GET    | /cycle/         | Yes  | Get all cycles           |
| DELETE | /cycle/{id}     | Yes  | Delete a cycle           |

### Symptoms

| Method | Endpoint        | Auth | Description              |
|--------|-----------------|------|--------------------------|
| POST   | /symptoms/      | Yes  | Log a symptom            |
| GET    | /symptoms/      | Yes  | Get all symptoms         |

### Journal

| Method | Endpoint        | Auth | Description              |
|--------|-----------------|------|--------------------------|
| POST   | /journal/       | Yes  | Create a journal entry   |
| GET    | /journal/       | Yes  | Get all journal entries  |

### Prediction

| Method | Endpoint              | Auth | Description                                  |
|--------|-----------------------|------|----------------------------------------------|
| POST   | /prediction/          | Yes  | Generate and store a new prediction          |
| GET    | /prediction/latest    | Yes  | Get latest prediction (recomputed live)      |
| POST   | /prediction/train     | Yes  | Manually retrain the ML model                |

### Chatbot

| Method | Endpoint          | Auth | Description              |
|--------|-------------------|------|--------------------------|
| POST   | /chatbot/ask      | Yes  | Send a message           |
| GET    | /chatbot/history  | Yes  | Get chat history         |
| DELETE | /chatbot/history  | Yes  | Clear chat history       |

### Analytics

| Method | Endpoint                    | Auth | Description                              |
|--------|-----------------------------|------|------------------------------------------|
| GET    | /analytics/                 | Yes  | Cycle trends, mood trends, symptom stats |
| GET    | /analytics/period-status    | Yes  | Current phase, cycle day, days until next|

### Other

| Method | Endpoint                    | Auth | Description                    |
|--------|-----------------------------|------|--------------------------------|
| GET    | /diet/                      | Yes  | Phase-based diet recommendations|
| GET    | /notifications/             | Yes  | Get all notifications          |
| PUT    | /notifications/{id}/read    | Yes  | Mark notification as read      |
| GET    | /export/report              | Yes  | Download PDF health report     |

---

## ML Prediction System

The predictor uses a `RandomForestRegressor` from scikit-learn.

### Feature vector (7 features)

| Index | Feature               | Description                                      |
|-------|-----------------------|--------------------------------------------------|
| 0     | prev_cycle_length     | Most recent known cycle length in days           |
| 1     | avg_last3             | Rolling mean of last 3 cycle lengths             |
| 2     | std_last3             | Rolling std deviation of last 3 cycle lengths    |
| 3     | period_length         | Days of bleeding (defaults to 5 if unknown)      |
| 4     | flow_encoded          | light=1, medium=2, heavy=3                       |
| 5     | avg_symptom_severity  | Average symptom severity for that cycle window   |
| 6     | avg_mood_score        | Average mood score for that cycle window         |

### Prediction rules

- Requires at least 2 completed cycles (with both start and end date logged)
- Ongoing cycles (no end date) are excluded from training but their start date is used as the prediction base
- Cycle lengths outside 21-45 days are treated as outliers and excluded
- With fewer than 4 valid cycles, falls back to a rolling mean
- With 4 or more cycles, trains a fresh RandomForest on the user's own data
- Final prediction blends the ML output with the user's rolling mean 50/50 for stability
- Confidence is derived from variance across decision trees

### Confidence labels

| Score     | Label              |
|-----------|--------------------|
| >= 0.85   | High confidence    |
| >= 0.65   | Moderate confidence|
| >= 0.45   | Low confidence     |
| < 0.45    | Irregular cycle    |

### Training on population data (optional)

A pre-trained population prior can be generated from the FedCycleData dataset:

```bash
cd backend
python scripts/train_from_csv.py
```

This saves a model to `backend/ml_models/cycle_rf_model.joblib`. The user's own data always takes precedence once they have 4 or more cycles.

---

## Email Notifications

Email alerts are optional. If SMTP credentials are not configured, the app works fully without them — alerts are still stored as in-app notifications.

### Supported alert types

| Alert              | Trigger                                              |
|--------------------|------------------------------------------------------|
| Period countdown   | 3, 2, and 1 day before predicted period              |
| PMS alert          | 7 days before predicted period                       |
| Mood alert         | Average mood score below 4 over the last 3 days      |
| Symptom alert      | Any symptom logged with severity 8 or above          |
| Weekly summary     | Every Monday at 09:00 UTC                            |

### Gmail setup

1. Enable 2-Step Verification on your Google account
2. Go to Google Account > Security > App Passwords
3. Generate an app password for "Mail"
4. Set `SMTP_USER` to your Gmail address and `SMTP_PASSWORD` to the generated app password in `.env`

Users can configure a separate notification email address and name in the Settings page. If not set, alerts go to their account email.

---

## Seeding Test Data

To populate a user account with realistic synthetic cycle, symptom, and journal data for testing:

```bash
cd backend

# Activate virtual environment first
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# Seed 24 cycles for an existing user
python scripts/seed_data.py --user-email your@email.com --cycles 24

# Or create a new demo account automatically
python scripts/seed_data.py --user-email demo@example.com --cycles 24
```

The script generates:
- The specified number of cycles with realistic length variation (Normal distribution, mean 28 days)
- 3-6 symptom logs per cycle, phase-aware (more cramps during menstrual phase, etc.)
- Journal entries every 2-3 days with phase-correlated mood scores
- Automatically trains the ML model after seeding

---

## Security Notes

- Passwords are hashed with bcrypt (cost factor 12)
- JWT tokens expire after 24 hours by default (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- All routes except `/auth/register` and `/auth/login` require a valid JWT
- Change `SECRET_KEY` to a random 32+ character string before any deployment
- Never commit `.env` to version control — it is listed in `.gitignore`
- The `.env.example` file contains only placeholder values and is safe to commit

---

## Disclaimer

This application is for personal health tracking purposes only. It does not provide medical advice, diagnosis, or treatment. Cycle predictions are statistical estimates and may not be accurate for all users. Always consult a qualified healthcare professional for medical concerns.
