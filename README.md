# TunisPark AI — Intelligent Parking Management System

<p align="center">
  <img src="https://img.shields.io/badge/YOLOv8-mAP%4050%3A%2097.3%25-brightgreen?style=for-the-badge&logo=opencv" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi" />
  <img src="https://img.shields.io/badge/React-19-61dafb?style=for-the-badge&logo=react" />
  <img src="https://img.shields.io/badge/Mistral_7B-RAG_Assistant-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" />
</p>

> **AI-powered smart parking for Tunisia** — automatic license plate recognition via YOLOv8 + EasyOCR, real-time dashboard, rules engine, LangChain RAG assistant, and full parking lifecycle management.

**Competition:** Institut International de Technologie / NAU — Prize: 500 TND + PFE Stage

---

## 📹 Demo Videos

> Full system walkthrough, live gate simulation, and AI assistant demo:

**[▶ Watch Demo Videos on Google Drive](https://drive.google.com/drive/folders/1f_bxNKLpTsFLCM2dyNkaKFXeaCcJnDHh?usp=sharing)**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **License Plate Detection** | YOLOv8n fine-tuned on 6176 images — mAP\@50 = **97.3%** |
| 🔤 **Arabic + Latin OCR** | EasyOCR with preprocessing (CLAHE, deskew) + Tunisian plate normalization |
| 🚗 **Vehicle Tracking** | DeepSORT multi-object tracker with per-track plate cache |
| 🚦 **Access Rules Engine** | DB-driven rule evaluation — allow / deny / alert per vehicle category |
| 💰 **Billing Engine** | Configurable tariffs: first hour, extra hours, daily cap, night & weekend multipliers |
| ⚡ **Real-time Dashboard** | Socket.IO live event feed, occupancy gauge, KPI cards |
| 🤖 **RAG AI Assistant** | Mistral 7B (Ollama) + FAISS — answers parking questions in French / Arabic / English |
| 🔔 **Alert System** | 7 alert types, 4 severity levels, auto-resolve, history log |
| 📊 **Analytics** | Revenue charts, peak-hours heatmap, decision breakdown pie |
| 🛡️ **Role-based Access** | superadmin / admin / staff / viewer roles with JWT |
| ⚙️ **Admin Panel** | 7 config tabs: Access Rules, Tariffs, Gates, Alert Rules, AI Settings, System, Rule Editor |

---

## 🏗️ Architecture

```
SmartParkTN/
├── frontend/          React 19 + Vite + TypeScript + Tailwind CSS v4 + shadcn/ui
│   └── src/
│       ├── pages/     11 pages (Dashboard, Vehicles, Sessions, Events, Analytics…)
│       ├── api/       Typed Axios wrappers for every backend endpoint
│       ├── store/     Zustand (auth + dashboard live state)
│       └── hooks/     useWebSocket (Socket.IO), useAssistant (chat state)
│
├── backend/           FastAPI + SQLAlchemy 2.0 + LangChain RAG
│   └── app/
│       ├── routers/   11 routers: auth, vehicles, sessions, events, rules,
│       │              tariffs, analytics, alerts, admin, assistant, vision
│       ├── models/    8 ORM models (Vehicle, Event, Session, Decision,
│       │              Tariff, Rule, User, Alert)
│       ├── services/  rule_engine, session_service, alert_service, plate_utils
│       └── ai/        embedder (FAISS), retriever, chat_handler (Ollama)
│
├── vision/            Real-time computer vision pipeline
│   ├── detector/      YOLOv8 plate detector
│   ├── ocr/           EasyOCR + pre/post-processing
│   ├── tracker/       DeepSORT multi-object tracker
│   ├── camera/        Thread-safe RTSP/webcam stream handler
│   ├── event_poster.py  Redis-debounced gate event HTTP poster
│   └── models/        plate_detector.pt (trained weights — mAP@50 = 97.3%)
│
├── training/          Model training pipeline
│   ├── download_hf_data.py  Downloads & converts HuggingFace dataset → YOLO
│   ├── train_detector.py    YOLOv8n fine-tuning with auto GPU detection
│   ├── augment.py           Albumentations augmentation pipeline
│   ├── evaluate.py          mAP (detector) + CER/exact-match (OCR)
│   └── data/labeled/        6176 YOLO-formatted images
│
├── knowledge_base/    PDF parking regulations (RAG source documents)
└── docker-compose.yml PostgreSQL 16 + Redis 7 (everything else runs locally)
```

---

## 🔄 System Flow

```
Camera / RTSP Stream
        │
        ▼
 YOLOv8 Plate Detector  ◄─── plate_detector.pt  (mAP@50 = 97.3%)
        │  bounding box
        ▼
 EasyOCR Engine  (Arabic + Latin chars)
        │  raw OCR text
        ▼
 Postprocessor  (normalize Tunisian plate format, Arabic digit mapping)
        │  clean plate string
        ▼
 DeepSORT Tracker  (debounce per-vehicle, suppress duplicates)
        │  confident plate ID
        ▼
 event_poster.py  ──►  Redis 5-second deduplication key
        │  POST /api/vision/plate-event
        ▼
 FastAPI Backend
        ├── Rule Engine ────────► allow / deny / alert
        ├── Session Service ────► open session / close + billing
        ├── Alert Service ──────► blacklist / overstay / low-confidence
        └── Socket.IO broadcast ► React Dashboard  (live updates)
```

---

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** — PostgreSQL + Redis containers
- **Python 3.11** — backend & vision
- **Node.js 20+** — frontend
- **[Ollama](https://ollama.ai)** — local LLM (`ollama pull mistral`)

### Step 1 — Start Infrastructure
```bash
docker compose up -d
# PostgreSQL 16 on :5432  |  Redis 7 on :6379
```

### Step 2 — Backend API
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head        # creates all 8 database tables
python init_admin.py        # creates superadmin  (admin / admin123)
python seed_data.py         # populates vehicles, events, sessions, alerts
uvicorn app.main:socket_app --reload --port 8000
```
→ **API:** `http://localhost:8000`  
→ **Swagger UI:** `http://localhost:8000/docs`

### Step 3 — Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
→ **Dashboard:** `http://localhost:5173`

### Step 4 — Vision Pipeline *(optional — needs webcam or RTSP)*
```bash
cd vision
venv\Scripts\activate
pip install -r requirements.txt
set GATE_ID=gate_01
set STREAM_SOURCE=0          # 0 = webcam  |  rtsp://host/stream  |  video.mp4
python main.py
```

Trained weights are already at `vision/models/plate_detector.pt`.

### Step 5 — AI Assistant *(optional — needs Ollama)*
```bash
ollama pull mistral           # ~4 GB download, one-time

# Add regulation PDFs to knowledge_base/, then build the FAISS index:
cd backend
python -m app.ai.embedder
```

The assistant is then live at `/assistant` and `POST /api/assistant/chat`.

---

## 🔑 Default Login

| Field | Value |
|-------|-------|
| URL | `http://localhost:5173` |
| Username | `admin` |
| Password | `admin123` |
| Role | superadmin (full access to all pages) |

> Change credentials via **Admin Panel → User Management** after first login.

---

## 📡 API Reference

All endpoints are prefixed `/api/`. Interactive docs: `http://localhost:8000/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | JWT authentication |
| GET | `/api/auth/me` | Current user profile |
| POST | `/api/vision/plate-event` | Ingest a plate detection event |
| GET | `/api/vehicles` | List / search vehicles |
| POST | `/api/vehicles` | Register a vehicle |
| PUT | `/api/vehicles/{id}/blacklist` | Blacklist a vehicle |
| PUT | `/api/vehicles/{id}/whitelist` | Remove from blacklist |
| GET | `/api/sessions` | Full session history |
| GET | `/api/sessions/open` | Currently active sessions |
| POST | `/api/sessions/{id}/close` | Manually close a session |
| GET | `/api/events` | Filtered event log (plate, gate, decision, date) |
| GET | `/api/analytics/occupancy` | Live occupancy |
| GET | `/api/analytics/revenue` | Daily revenue data |
| GET | `/api/analytics/peak-hours` | Traffic heatmap (day × hour) |
| GET | `/api/analytics/decisions` | Allow / deny / alert breakdown |
| GET | `/api/alerts` | Active unresolved alerts |
| GET | `/api/alerts/history` | All alerts including resolved |
| PUT | `/api/alerts/{id}/resolve` | Resolve an alert |
| GET | `/api/rules` | All system rules (key / value) |
| PUT | `/api/rules/{key}` | Update a rule value |
| GET | `/api/tariffs` | List tariff profiles |
| POST | `/api/tariffs` | Create a tariff profile |
| GET | `/api/tariffs/simulate` | Simulate billing for a duration |
| POST | `/api/assistant/chat` | AI assistant (RAG + Mistral) |
| GET | `/api/assistant/explain/{event_id}` | AI explanation for an event |
| GET | `/api/admin/users` | List all staff users (superadmin only) |
| POST | `/api/admin/users` | Create a staff user (superadmin only) |
| PUT | `/api/admin/users/{id}` | Update / deactivate a user |

---

## 🧠 AI Training Results

**Model:** YOLOv8n fine-tuned on `keremberke/license-plate-object-detection`  
**Dataset:** 6176 images — train / val / test splits, COCO → YOLO converted  
**Hardware:** NVIDIA GeForce GTX 1660 Ti (6 GB VRAM), CUDA 11.8, PyTorch 2.7+cu118  
**Run:** 25 epochs (early stop at patience = 15), batch = 16, imgsz = 640

| Metric | Score |
|--------|-------|
| Precision | **99.1%** |
| Recall | **94.3%** |
| mAP\@0.50 | **97.3%** |
| mAP\@[0.50:0.95] | **70.1%** |

### Training Loss & Metrics

![Training Results](docs/training/results.png)

### F1–Confidence Curve

![F1 Confidence Curve](docs/training/BoxF1_curve.png)

### Validation Batch Predictions

![Validation Predictions](docs/training/val_batch0_pred.jpg)

### Normalized Confusion Matrix

![Confusion Matrix](docs/training/confusion_matrix_normalized.png)

---

## 🏋️ Retrain the Model

```bash
cd training
venv\Scripts\activate
pip install -r requirements.txt

# 1. Download & convert HuggingFace dataset to YOLO format
python download_hf_data.py

# 2. (Optional) Augment training images
python augment.py --input data/labeled --output data/augmented --count 5

# 3. Train — GPU is auto-detected (falls back to CPU)
python train_detector.py --epochs 50 --batch 16 --imgsz 640

# 4. Evaluate
python evaluate.py --mode detector --model models/plate_detector.pt --data plates.yaml
python evaluate.py --mode ocr --images data/ocr/test/images --labels data/ocr/test/labels
```

Best weights are saved to `training/models/plate_detector.pt` and copied to `vision/models/plate_detector.pt`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19, Vite 6, TypeScript, Tailwind CSS v4, shadcn/ui, Zustand, Recharts, Socket.IO-client |
| **Backend** | FastAPI 0.115, SQLAlchemy 2.0, Alembic, Pydantic v2, python-socketio |
| **Database** | PostgreSQL 16, Redis 7 (deduplication + pub/sub) |
| **Auth** | JWT (python-jose), bcrypt, role-based access control (4 roles) |
| **AI / RAG** | LangChain 0.3, FAISS-cpu, sentence-transformers (all-MiniLM-L6-v2), Ollama (Mistral 7B — local) |
| **Vision** | YOLOv8n (ultralytics 8.4), EasyOCR, DeepSORT (deep-sort-realtime), OpenCV |
| **Training** | PyTorch 2.7+cu118, ultralytics, Albumentations, HuggingFace Hub |
| **Infra** | Docker Compose, local Ollama |

---

## 📋 Implementation Status

| Component | Status |
|-----------|--------|
| PostgreSQL + Redis (Docker) | ✅ Running |
| FastAPI Backend — 11 routers | ✅ Complete |
| 8 Database models + Alembic migrations | ✅ Complete |
| Rule Engine + Billing Engine | ✅ Complete |
| JWT Auth + RBAC (4 roles) | ✅ Complete |
| Socket.IO real-time events | ✅ Complete |
| React Frontend — 11 pages | ✅ Complete |
| Admin Panel — 7 config tabs wired to rules API | ✅ Complete |
| LangChain RAG Assistant | ✅ Complete (needs PDFs + embedder run) |
| YOLOv8 Plate Detector | ✅ Trained — 97.3% mAP\@50 |
| EasyOCR Pipeline + postprocessor | ✅ Complete (base model) |
| DeepSORT Tracker | ✅ Complete |
| Vision Pipeline (end-to-end) | ✅ Complete |
| Superadmin seed (`init_admin.py`) | ✅ Complete |
| Mock data seed (`seed_data.py`) | ✅ Complete |
| Celery background tasks | ⚠️ Not wired — overstay/revenue checks |
| OCR fine-tuning data | ⚠️ Needs plate crop + text pairs |
| Payment gateway | ⚠️ Out of scope for demo |

Full details: [CURRENT_IMPLEMENTATION.md](CURRENT_IMPLEMENTATION.md)

---

## ⚠️ Known Limitations

- **Celery not wired** — overstay and revenue anomaly periodic checks are not running automatically. Trigger manually through the API or create `backend/app/celery_app.py`.
- **Knowledge base empty** — the RAG assistant returns generic answers until PDFs are added to `knowledge_base/` and `python -m app.ai.embedder` is run.
- **OCR fine-tuning** — EasyOCR runs with the base model. Performance on degraded or non-standard Tunisian plates may vary.
- **Single camera** — the vision pipeline is validated with one webcam/RTSP stream. Multi-gate setups need one vision process per gate.

---

## 📁 Key Files Reference

```
backend/
├── app/main.py                FastAPI app + Socket.IO ASGI mount
├── app/auth.py                JWT decode, bcrypt, require_roles()
├── app/routers/vision.py      POST /api/vision/plate-event — full ingestion
├── app/services/rule_engine.py  check_access() + calculate_tariff()
├── app/ai/chat_handler.py     LangChain context builder + Ollama HTTP call
├── init_admin.py              Creates superadmin user on first run
└── seed_data.py               Populates test vehicles, sessions, events

frontend/src/
├── pages/Dashboard.tsx        Live gate feed, KPIs, Socket.IO events
├── pages/Admin.tsx            7-tab config panel (all tabs save to rules API)
├── pages/Assistant.tsx        RAG chat UI with quick-prompt buttons
├── pages/Analytics.tsx        Revenue / peak-hours / decisions charts
├── hooks/useWebSocket.ts      Socket.IO client with auto-reconnect
└── store/dashboardStore.ts    Live state (events, alerts, occupancy)

vision/
├── main.py                    Pipeline entry point (RTSP/webcam loop)
├── detector/yolo_detector.py  YOLOv8 wrapper — returns plate crops
├── ocr/ocr_engine.py          EasyOCR singleton (Arabic + English)
├── tracker/deepsort_tracker.py  Per-track plate cache + dedup
└── models/plate_detector.pt   Trained weights (mAP@50 = 97.3%)
```

---

## 📜 License

MIT — free to use, modify, and distribute.

**Competition:** Institut International de Technologie / NAU · Prize: **500 TND + PFE Stage**

---

<p align="center">Built with ❤️ for smart Tunisian parking · TunisPark AI 2026</p>
