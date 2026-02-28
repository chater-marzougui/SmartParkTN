# TunisPark AI — Intelligent Parking Management System

> AI-powered Tunisian parking management: YOLOv8 plate detection · EasyOCR · RAG AI assistant · Real-time dashboard

**Competition:** Institut International de Technologie / NAU — Prize: 500 TND + PFE Stage

---

## Architecture

```
SmartParkTN/
├── frontend/          React 19 + Vite + TypeScript + shadcn/ui dashboard
├── backend/           FastAPI + SQLAlchemy 2.0 + LangChain RAG API
├── vision/            YOLOv8 · EasyOCR · DeepSORT pipeline
├── training/          Detector & OCR training scripts
├── knowledge_base/    PDF parking regulations (RAG source)
└── docker-compose.yml PostgreSQL + Redis only (everything else runs locally)
```

---

## Quick Start

### 1. Start infrastructure (PostgreSQL + Redis)
```bash
docker compose up -d
```

### 2. Backend
```bash
cd backend
venv\Scripts\activate          # venv already created
pip install -r requirements.txt
alembic upgrade head           # creates all tables
uvicorn app.main:socket_app --reload --port 8000
```

### 3. Create first superadmin user
```bash
python -c "
from app.db import SessionLocal
from app.models.user import User, UserRole
from app.auth import hash_password
db = SessionLocal()
u = User(username='admin', full_name='Admin', email='admin@tunispark.tn',
         hashed_password=hash_password('admin123'), role=UserRole.superadmin, active=True)
db.add(u); db.commit(); print('Done')
"
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 5. API docs
```
http://localhost:8000/docs
```

---

## AI Assistant Setup (RAG)

Ollama with Mistral is already installed locally.

```bash
# 1. Add regulation PDFs to knowledge_base/

# 2. Build FAISS index from backend venv
cd backend
python -m app.ai.embedder
```

The assistant is then live at the `/assistant` page and `POST /api/assistant/chat`.

---

## Vision Pipeline

```bash
cd vision
venv\Scripts\activate
pip install -r requirements.txt
set GATE_ID=gate_01
set STREAM_SOURCE=0       # 0 = webcam, or rtsp://...
python main.py
```

Requires `vision/models/plate_detector.pt`. For demo, set `PLATE_MODEL_PATH=yolov8n.pt` to use the generic COCO model.

---

## Training

```bash
cd training
venv\Scripts\activate
pip install -r requirements.txt

# Augment labeled data
python augment.py --input data/labeled --output data/augmented --count 5

# Train plate detector
python train_detector.py --epochs 100 --batch 16

# Evaluate
python evaluate.py --mode detector --model models/plate_detector.pt --data plates.yaml
python evaluate.py --mode ocr --images data/ocr/test/images --labels data/ocr/test/labels
```

---

## Default Login

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | superadmin |

> Change via Admin → User Management after first login.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 8, TypeScript, Tailwind CSS v4, shadcn/ui, Zustand, Recharts, Socket.IO |
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL 16, Redis 7, JWT, bcrypt |
| AI / RAG | LangChain 0.3, FAISS-cpu, sentence-transformers, Ollama (Mistral 7B — local) |
| Vision | YOLOv8 (ultralytics), EasyOCR, DeepSORT, OpenCV |
| Infra | Docker Compose (postgres + redis), local Ollama |

---

## Implementation Status

See [CURRENT_IMPLEMENTATION.md](CURRENT_IMPLEMENTATION.md) for a detailed breakdown of every component, what's working, and what's pending.

