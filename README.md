# WindSight - Renewable Generation Forecast Accuracy Portal

WindSight is a professional analytics portal designed for UK electricity procurement analysts. It allows users to evaluate the accuracy of wind generation forecasts relative to actual generation, specifically focusing on the "As-Of" decision window for day-ahead market purchases.

## 🎯 Problem Statement
Electricity procurement analysts must decide how much power to buy from the wholesale market one day before delivery. Since wind generation is volatile, they rely on forecasts. WindSight provides a quantitative way to evaluate these forecasts, allowing analysts to understand the error margin and bias of available forecasts at the exact moment a decision must be made.

## 🚀 Features
- **Forecast Explorer**: Time-series visualization of Actual vs. As-Of Forecasts.
- **Accuracy Analytics**: Quantitative evaluation using MAE, RMSE, Bias, WAPE, and P90 absolute error.
- **Decision Insights**: Convergence analysis showing how forecast error (MAE) typically decreases as the decision cutoff approaches delivery.
- **As-Of Selection**: Strict temporal filtering to ensure no look-ahead bias in historical evaluations.
- **Direct API Integration**: Real-time data fetching from the Elexon Insights Solution API.

## 🛠️ Tech Stack
- **Frontend**: React 18, TypeScript, Tailwind CSS, TanStack Query, Recharts.
- **Backend**: Python 3.12, FastAPI, Uvicorn.
- **Infrastructure**: Docker, Docker Compose.
- **Data Source**: Elexon BMRS API (FUELHH and WINDFOR datasets).

## 📦 Installation & Setup

### Option 1: Using Docker (Recommended)
```bash
docker-compose up --build
```
The application will be available at:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

### Option 2: Local Manual Setup
**Backend:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:.
python3 -m uvicorn src.api,main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📊 API Endpoints
- `GET /health`: System health check.
- `GET /accuracy`: Returns aggregated accuracy metrics for a target date and decision cutoff.
- `GET /accuracy/intervals`: Returns a detailed hourly error breakdown.

## 🔍 Verification & Testing
- **Unit Tests**: Run `pytest tests/` to verify accuracy calculations and API logic.
- **Integration**: The frontend is fully integrated with the FastAPI backend using Axios and TanStack Query.
- **Accuracy**: Validated against Elexon data using the a-priori a-posteriori temporal filter.

## 🤖 AI Disclosure
This project was developed with the assistance of AI tools (Claude) for rapid prototyping, boilerplate generation, and technical auditing.
