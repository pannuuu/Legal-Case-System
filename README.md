# AI-Assisted Legal Case Guidance and Prediction System

Initial project scaffold for the **AI-Assisted Legal Case Guidance and Prediction System**.

## Technology Stack

### Frontend
- React 19
- Vite 6
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- Uvicorn

### AI & Machine Learning
- Google Gemini API
- Sentence Transformers
- Existing Experiment 3 Random Forest model (to be integrated in later phases)
- NumPy & Pandas
- Scikit-learn

## Project Structure

```text
AI-Legal-Guidance-System/
├── frontend/
│   ├── public/assets/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   └── schemas/
│   │   ├── services/
│   │   ├── models/
│   │   ├── utils/
│   │   ├── config/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── data/
│   │   ├── models/random_forest_exp3/
│   │   ├── retrieval/
│   │   └── retrieval_index/
│   ├── requirements.txt
│   └── .env.example
├── reference/
├── docs/
├── .gitignore
└── README.md
```

## Initial Setup

### 1. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **macOS / Linux:** `source .venv/bin/activate`

Install dependencies and configure environment variables:

```bash
pip install -r requirements.txt
cp .env.example .env
```

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

## Status

Phase 0 (Project Initialization) complete. Model integration, retrieval indexing, API endpoints, and UI implementation will follow in subsequent phases.
