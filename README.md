# AI-CDSS — Explainable AI Clinical Decision Support System

> An end-to-end, doctor-in-the-loop web application combining patient EMR management, OCR medical report extraction, rules-based laboratory interpretation, 30-day hospital readmission risk prediction (XGBoost), Explainable AI (SHAP), and RAG-grounded clinical guideline retrieval with LLM-generated, citation-backed answers.

> [!IMPORTANT]
> **Clinical Decision Support Disclaimer**
> This system is a **decision support prototype** for certified clinicians. It does **not** autonomously diagnose disease or prescribe medication. All generated summaries, risk scores, and statistical outputs require final physician review and validation before any clinical use.

---

## Features

- **Patient EMR Management** — searchable patient directory, registration, editing, and medical history timeline, secured behind JWT-authenticated doctor accounts.
- **OCR Report Extraction** — upload PDF/image medical reports; text is extracted automatically (Tesseract OCR + pdf2image) and linked to the patient record.
- **Rules-Based Lab Analysis** — numeric lab values (glucose, HbA1c, lipids, etc.) are compared against explicit clinical reference ranges to flag Normal / Elevated / Low — deterministic, not LLM-guessed.
- **30-Day Readmission Risk Prediction** — an XGBoost classifier trained on the UCI Diabetes 130-US Hospitals dataset estimates a patient's readmission risk.
- **Explainable AI (SHAP)** — local (per-patient) and global feature-importance explanations for every risk prediction, so clinicians can see *why*, not just *what*.
- **RAG Clinical Evidence Assistant** — semantic search (FAISS + Sentence-Transformers) over curated clinical guidelines, with an LLM generating citation-grounded answers only from retrieved evidence — never from model memory alone.
- **Clinical Safety Disclaimer** — persistent doctor-in-the-loop banner across every clinical view.

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, JavaScript (ES6+), Tailwind CSS, React Router v6, Axios, Lucide React |
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy 2.0, Pydantic v2, PostgreSQL, Uvicorn |
| **Auth** | JWT, Passlib, Bcrypt |
| **Machine Learning** | Scikit-learn, XGBoost, Pandas, NumPy, Joblib |
| **Explainable AI** | SHAP |
| **RAG / NLP** | Sentence-Transformers, FAISS |
| **OCR** | Tesseract OCR, pdf2image, Poppler |

## Architecture

```
                  +-----------------------------------+
                  |        Doctor / Clinician         |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |  React + Vite Frontend (JS)       |
                  |  Healthcare / Medical Green UI    |
                  +-----------------+-----------------+
                                    | REST APIs (Axios + JWT)
                                    v
                  +-----------------------------------+
                  |    FastAPI Python Backend         |
                  |  Auth, CRUD, Service Integrator   |
                  +--------+-----------------+--------+
                           |                 |
        +------------------+                 +------------------+
        |                                                       |
        v                                                       v
+-------------------------------+               +-------------------------------+
|     PostgreSQL Database       |               |     Clinical AI Subsystems    |
| • users (doctors)             |               | • XGBoost Readmission Risk    |
| • patients                    |               | • SHAP / XAI Engine           |
| • medical_history              |               | • Tesseract OCR Reports       |
| • reports                     |               | • Rules Lab Engine            |
| • lab_results                 |               | • RAG Vector DB (FAISS)       |
| • predictions & logs           |               | • Clinical LLM Assistant      |
+-------------------------------+               +-------------------------------+
```

## Project Structure

```
ai-cdss-clean/
├── backend/
│   ├── app/
│   │   ├── api/          # auth, patients, reports, lab_results, rag, xai, assistant
│   │   ├── core/         # config, security (JWT / bcrypt)
│   │   ├── database/     # SQLAlchemy session/engine
│   │   ├── models/       # ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   └── services/     # OCR/NLP, rules engine, RAG retrieval, SHAP/XAI
│   ├── tests/            # pytest suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Navbar, Sidebar, forms, charts, evidence search, XAI viz
│   │   ├── context/      # Auth context (JWT session)
│   │   ├── pages/        # Dashboard, Patients, Laboratory, Readmission,
│   │   │                 # Explainability, MedicalEvidence, ClinicalAssistant, Reports
│   │   └── services/     # Axios API client
│   └── package.json
├── ml/
│   ├── scripts/          # dataset fetch/generate, preprocess, train, predict
│   ├── models/           # trained XGBoost model + preprocessor (joblib)
│   └── outputs/          # metrics.json, feature_list.json
├── rag/
│   ├── documents/        # curated clinical guideline excerpts
│   └── vector_db/        # FAISS index + metadata
├── docs/                 # module-by-module demo guides
└── docker-compose.yml    # local PostgreSQL service
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL (optional — SQLite fallback works out of the box for local testing)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and [Poppler](https://poppler.freedesktop.org/) installed and on your `PATH` (required for OCR report extraction; not bundled in this repo)

### 1. Database (optional, recommended)
```bash
docker compose up -d postgres
```
Copy `.env.example` to `.env`. Default: `postgresql://postgres:postgres@localhost:5432/ai_cdss`.
No Postgres available? Set `DATABASE_URL=sqlite:///./ai_cdss.db` instead.

To use the RAG assistant's LLM-generated answers, also set in `backend/.env`:
```
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
python run_backend.py
# or: uvicorn app.main:app --reload --port 8000
```
API docs: `http://localhost:8000/docs`

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
App: `http://localhost:5173`

### 4. Machine Learning Pipeline (optional — trained model artifacts are already included)
```bash
python ml/scripts/download_or_generate_dataset.py
python ml/scripts/train.py
python ml/scripts/predict_sample.py
```

### 5. Tests
```bash
cd backend
pytest
```

## Medical Safety & Ethical Guidelines

1. **Doctor-in-the-loop, always.** The system is an analytical aid — it never replaces a qualified clinician's judgment.
2. **Clear separation of concerns.** Numerical risk comes from XGBoost, explanations come from SHAP, guideline evidence comes from RAG retrieval over verified documents, and natural-language text is LLM-generated *only* from that retrieved evidence — the LLM is never asked to diagnose or invent a number.
3. **Transparent limitations.** Uncertainty, low-confidence retrieval, and missing data are surfaced explicitly rather than hidden.

## License

Developed as a Final-Year Computer Science & Engineering capstone project, for academic and decision-support research demonstration only.
