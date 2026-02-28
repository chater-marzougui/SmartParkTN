# TunisPark AI — Intelligent Parking Management System

> AI-powered Tunisian parking management: YOLOv8 plate detection · EasyOCR · RAG AI assistant · Real-time dashboard

---

## Architecture

```
SmartParkTN/
├── frontend/          React 19 + Vite + shadcn/ui dashboard
├── backend/           FastAPI + SQLAlchemy + LangChain RAG API
├── vision/            YOLOv8 · EasyOCR · DeepSORT pipeline
├── training/          Detector & OCR training scripts
├── knowledge_base/    PDF parking regulations (used by RAG)
└── docker-compose.yml Full-stack orchestration
```

---

## Quick Start (Docker)

```bash
# 1. Clone and enter the project
cd SmartParkTN

# 2. Copy and configure env files
cp .env .env.local          # edit POSTGRES_PASSWORD, SECRET_KEY

# 3. Pull & build all services
docker compose up --build

# 4. Access the dashboard
open http://localhost          # via nginx
open http://localhost:5173     # direct Vite dev server
open http://localhost:8000/docs  # FastAPI Swagger UI
```

---

## Local Development (no Docker)

### Backend
```bash
cd backend
python -m venv venv && venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env-example .env                    # edit DATABASE_URL, SECRET_KEY
alembic upgrade head             # run migrations
uvicorn app.main:socket_app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Vision pipeline
```bash
cd vision
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
# Set stream source (0 = webcam, or RTSP URL):
set STREAM_SOURCE=0             # Windows
python main.py
```

---

## AI Assistant Setup

The assistant uses Ollama + Mistral + FAISS RAG:

```bash
# 1. Install Ollama: https://ollama.ai
ollama pull mistral

# 2. Add PDFs (regulations, tariffs, rules) to:
knowledge_base/

# 3. Build the FAISS index:
cd backend
python -m app.ai.embedder
```

---

## Training

```bash
cd training
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# 1. Augment labeled dataset
python augment.py --input data/labeled --output data/augmented --count 5

# 2. Train detector (requires GPU recommended)
python train_detector.py --epochs 100 --batch 16

# 3. Evaluate
python evaluate.py --mode detector --model models/plate_detector.pt --data plates.yaml
python evaluate.py --mode ocr --images data/ocr/test/images --labels data/ocr/test/labels
```

---

## Default Credentials

| Role       | Username | Password   |
|------------|----------|------------|
| Superadmin | admin    | admin123   |

> **Change passwords immediately in production via Admin → User Management.**

---

## Tech Stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | React 19, Vite 8, TypeScript, Tailwind CSS v4, shadcn/ui, Zustand, Recharts, Socket.IO |
| Backend   | FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Redis, Celery |
| AI / RAG  | LangChain 0.3, FAISS-cpu, sentence-transformers, Ollama (Mistral) |
| Vision    | YOLOv8 (ultralytics), EasyOCR, DeepSORT, OpenCV |
| Infra     | Docker Compose, Nginx, Ollama |
