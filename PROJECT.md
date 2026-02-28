# 🚗 TunisParк AI — Smart Tunisian Parking System
### Full Project Blueprint — From Zero to Production

> **Competition:** Institut International de Technologie / NAU  
> **Prize:** 500 TND + PFE Stage at NAU  
> **Contact:** taoufik.benabdallah@iit.ens.tn  
> **Deliverables:** Prototype · Video Demo · Script

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Full System Architecture](#2-full-system-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Database Schema](#4-database-schema)
5. [Backend API Design](#5-backend-api-design)
6. [Frontend Pages & UI](#6-frontend-pages--ui)
7. [Admin Dashboard — Every Setting Explained](#7-admin-dashboard--every-setting-explained)
8. [Vision Pipeline (ALPR)](#8-vision-pipeline-alpr)
9. [AI Assistant with RAG](#9-ai-assistant-with-rag)
10. [Rule Engine (Zero Hardcoding)](#10-rule-engine-zero-hardcoding)
11. [Smart Detection Features](#11-smart-detection-features)
12. [Step-by-Step Build Plan (Week by Week)](#12-step-by-step-build-plan-week-by-week)
13. [Evaluation & Metrics](#13-evaluation--metrics)
14. [Demo Video Script](#14-demo-video-script)
15. [Folder Structure](#15-folder-structure)

---

## 1. Project Overview

### Problem

Parking lots in Tunisia (hospitals, malls, industrial zones, companies) manage hundreds of vehicle entries/exits daily. Manual systems — physical tickets, badge checks, human verification — cause:

- Long queues at entry/exit gates
- Human error in recording entry/exit times
- Disputes over billing (exact time entered/exited)
- No audit trail for blacklisted or unauthorized vehicles
- Staff unable to instantly answer "why was this car rejected?"

### Solution

A fully automated, AI-powered parking management system that:

1. **Sees** — Detects Tunisian license plates via camera using a fine-tuned YOLO model
2. **Reads** — OCRs the plate number with a custom CRNN model handling Arabic + digits
3. **Decides** — Applies configurable business rules from an admin dashboard (no code changes needed)
4. **Explains** — Uses an AI assistant backed by RAG to answer staff questions in natural language
5. **Tracks** — Logs every event, computes billing, detects anomalies

### What Makes This Different

Most ALPR projects stop at "detect plate + read text." This system adds:

- **Zero-hardcode rule engine** — admins change pricing/rules from a dashboard
- **Explainable AI** — every barrier decision is logged with the rule that triggered it
- **RAG assistant** — staff can ask "why was this car refused?" and get a regulation-cited answer
- **Fraud detection** — duplicate plates, mismatched vehicle types, suspicious timing
- **Analytics** — peak hours, revenue, occupancy heatmaps

---

## 2. Full System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HARDWARE LAYER                               │
│  IP Camera (Entry) ──────────────────── IP Camera (Exit)           │
│       │                                        │                    │
│  Raspberry Pi 5 / Edge PC                 Same setup               │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ RTSP Video Stream
┌─────────────────────────▼───────────────────────────────────────────┐
│                      VISION PIPELINE                                │
│                                                                     │
│  Frame Capture → Plate Detector (YOLOv8) → Plate Crop              │
│       ↓                                        ↓                   │
│  Vehicle Tracker (DeepSORT)          OCR Engine (CRNN/TrOCR)       │
│  [avoid re-reading same car]          [Arabic + digits]             │
│       ↓                                        ↓                   │
│  Vehicle Type Classifier            Post-Processor (regex validate) │
│  [car/truck/moto/bus]                                               │
│                          ↓                                          │
│                  Plate Result JSON                                  │
│        { plate, confidence, vehicle_type, camera_id }              │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ HTTP POST
┌─────────────────────────▼───────────────────────────────────────────┐
│                       BACKEND CORE (FastAPI)                        │
│                                                                     │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │  Event Handler  │  │ Rule Engine  │  │   Session Manager     │  │
│  │  (entry/exit)   │  │ (JSON rules) │  │   (duration, billing) │  │
│  └────────┬────────┘  └──────┬───────┘  └───────────┬───────────┘  │
│           │                  │                       │              │
│           └──────────────────▼───────────────────────┘             │
│                         Decision Engine                             │
│           { ALLOW | DENY | ALERT } + reason_code + rule_ref        │
│                              │                                      │
│                    ┌─────────▼──────────┐                          │
│                    │    PostgreSQL DB    │                          │
│                    │  + Redis Cache     │                          │
│                    └─────────┬──────────┘                          │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      AI ASSISTANT LAYER                             │
│                                                                     │
│  Staff Question → LangChain → FAISS Vector DB ← Embedded PDFs      │
│                      ↓           (parking rules, tariffs,           │
│               Context Builder     access policies)                  │
│                      ↓                                              │
│               Mistral / Llama 3 → Natural Language Answer           │
│               + Decision Log (facts, not hallucination)            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                       FRONTEND (React+TS+Tailwind+Shadcn)           │
│                                                                     │
│  Live Gate Dashboard │ Vehicle Registry │ Session Manager           │
│  Admin Panel         │ Reports/Analytics│ AI Chat Interface         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tech Stack

### Backend
| Component | Technology | Why |
|---|---|---|
| API Framework | **FastAPI (Python)** | Async, fast, auto-docs |
| Database | **PostgreSQL** | Relations, transactions |
| Cache | **Redis** | Recent plate cache, debounce |
| Task Queue | **Celery** | Async billing, alerts |
| Auth | **JWT + bcrypt** | Role-based access |

### Vision
| Component | Technology | Why |
|---|---|---|
| Plate Detection | **YOLOv8** | Fast, accurate, edge-ready |
| OCR | **CRNN** (custom) or **TrOCR** | Handles Arabic + digits |
| Tracking | **DeepSORT** | Avoid re-reading same car |
| Vehicle Type | **YOLOv8 multi-class** | Car/truck/moto |

### AI / RAG
| Component | Technology | Why |
|---|---|---|
| LLM | **Mistral 7B** (local) or **Llama 3** | Privacy, no API cost |
| RAG Framework | **LangChain** | Mature, well-documented |
| Vector DB | **FAISS** | Fast, local |
| Embeddings | **sentence-transformers** | French/Arabic support |

### Frontend
| Component | Technology | Why |
|---|---|---|
| Framework | **React + Vite + TypeScript** | Fast SPA with type safety |
| UI Components | **ShadCN + Tailwind** | Clean, professional |
| Charts | **Recharts** | Analytics dashboards |
| Real-time | **WebSocket (Socket.IO)** | Live gate updates |
| State | **Zustand** | Simple state management |

---

## 4. Database Schema

### vehicles
```sql
CREATE TABLE vehicles (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plate       VARCHAR(20) UNIQUE NOT NULL,       -- normalized: "123TN4567"
  category    VARCHAR(20) NOT NULL,               -- visitor | subscriber | vip | blacklist
  vehicle_type VARCHAR(20) DEFAULT 'car',         -- car | truck | moto | bus
  owner_name  VARCHAR(100),
  owner_phone VARCHAR(20),
  subscription_expires DATE,                      -- null if visitor
  notes       TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### events
```sql
CREATE TABLE events (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plate       VARCHAR(20) NOT NULL,
  event_type  VARCHAR(10) NOT NULL,               -- entry | exit
  gate_id     VARCHAR(20) NOT NULL,               -- gate_A | gate_B
  camera_id   VARCHAR(20) NOT NULL,
  raw_plate   VARCHAR(20),                        -- before normalization
  confidence  FLOAT,                              -- OCR confidence 0-1
  vehicle_type VARCHAR(20),
  image_path  TEXT,                               -- snapshot saved
  timestamp   TIMESTAMPTZ DEFAULT NOW()
);
```

### sessions
```sql
CREATE TABLE sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plate           VARCHAR(20) NOT NULL,
  entry_event_id  UUID REFERENCES events(id),
  exit_event_id   UUID REFERENCES events(id),
  entry_time      TIMESTAMPTZ NOT NULL,
  exit_time       TIMESTAMPTZ,
  duration_minutes INT,
  tariff_id       UUID REFERENCES tariffs(id),
  base_price      DECIMAL(10,3),
  extra_charges   DECIMAL(10,3) DEFAULT 0,
  total_price     DECIMAL(10,3),
  status          VARCHAR(20) DEFAULT 'open',     -- open | closed | disputed
  payment_method  VARCHAR(20),                    -- cash | card | subscription
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### decisions
```sql
CREATE TABLE decisions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id    UUID REFERENCES events(id),
  plate       VARCHAR(20) NOT NULL,
  decision    VARCHAR(10) NOT NULL,               -- allow | deny | alert
  reason_code VARCHAR(50),                        -- BLACKLIST | VIP | VISITOR | EXPIRED_SUB
  rule_ref    VARCHAR(100),                       -- "Article 3.2" | "tariff_visitor_v2"
  rule_data   JSONB,                              -- snapshot of rule applied
  gate_action VARCHAR(20),                        -- open | close | hold
  timestamp   TIMESTAMPTZ DEFAULT NOW()
);
```

### tariffs
```sql
CREATE TABLE tariffs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            VARCHAR(100) NOT NULL,
  vehicle_type    VARCHAR(20) DEFAULT 'car',
  first_hour_price DECIMAL(10,3),
  extra_hour_price DECIMAL(10,3),
  daily_max        DECIMAL(10,3),
  night_multiplier FLOAT DEFAULT 1.0,             -- e.g. 1.5 for night rate
  night_start      TIME DEFAULT '22:00',
  night_end        TIME DEFAULT '06:00',
  weekend_multiplier FLOAT DEFAULT 1.0,
  is_active       BOOLEAN DEFAULT true,
  valid_from      DATE,
  valid_until     DATE,
  created_by      UUID REFERENCES users(id),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### rules
```sql
CREATE TABLE rules (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_key    VARCHAR(100) UNIQUE NOT NULL,       -- "max_stay_hours", "vip_zones"
  rule_value  JSONB NOT NULL,
  description TEXT,
  category    VARCHAR(50),                        -- access | billing | alert | schedule
  is_active   BOOLEAN DEFAULT true,
  updated_by  UUID REFERENCES users(id),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### users (staff)
```sql
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name   VARCHAR(100),
  role        VARCHAR(20) DEFAULT 'staff',        -- superadmin | admin | staff | viewer
  is_active   BOOLEAN DEFAULT true,
  last_login  TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### alerts
```sql
CREATE TABLE alerts (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_type  VARCHAR(50) NOT NULL,               -- BLACKLIST_ENTRY | DUPLICATE_PLATE | LONG_STAY | FRAUD
  plate       VARCHAR(20),
  event_id    UUID REFERENCES events(id),
  severity    VARCHAR(10) DEFAULT 'medium',       -- low | medium | high | critical
  message     TEXT,
  is_resolved BOOLEAN DEFAULT false,
  resolved_by UUID REFERENCES users(id),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 5. Backend API Design

### Authentication
```
POST /api/auth/login         → JWT token
POST /api/auth/refresh       → refresh token
POST /api/auth/logout
GET  /api/auth/me            → current user profile
```

### Vision Events (called by camera systems)
```
POST /api/vision/plate-event
  Body: { plate, raw_plate, confidence, camera_id, gate_id, vehicle_type, image_base64 }
  Returns: { decision, reason, gate_action, session_id }
```

### Vehicles
```
GET    /api/vehicles                      → list with filters
POST   /api/vehicles                      → create
GET    /api/vehicles/:id
PUT    /api/vehicles/:id
DELETE /api/vehicles/:id
GET    /api/vehicles/search?plate=...
POST   /api/vehicles/:id/blacklist
POST   /api/vehicles/:id/whitelist
```

### Sessions
```
GET  /api/sessions                        → list with date filters
GET  /api/sessions/:id
POST /api/sessions/:id/close              → manual close + billing
GET  /api/sessions/open                   → all currently parked vehicles
GET  /api/sessions/export?format=csv
```

### Events
```
GET  /api/events                          → full audit log
GET  /api/events?plate=...&from=...&to=...
GET  /api/events/:id
```

### Rules (Admin Only)
```
GET  /api/rules                           → all rules
PUT  /api/rules/:key                      → update rule value
GET  /api/rules/:key/history              → change history
```

### Tariffs (Admin Only)
```
GET  /api/tariffs
POST /api/tariffs
PUT  /api/tariffs/:id
DELETE /api/tariffs/:id
GET  /api/tariffs/simulate?duration=90&vehicle_type=car  → price preview
```

### Analytics
```
GET  /api/analytics/occupancy             → current occupancy %
GET  /api/analytics/revenue?from=&to=    → revenue totals
GET  /api/analytics/peak-hours           → heatmap data
GET  /api/analytics/top-vehicles         → most frequent
GET  /api/analytics/decisions            → allow/deny breakdown
```

### AI Assistant
```
POST /api/assistant/chat
  Body: { message, context: { plate?, session_id? } }
  Returns: { answer, sources, confidence }

GET  /api/assistant/explain/:decision_id  → why was this decision made
```

### Alerts
```
GET  /api/alerts                          → unresolved alerts
PUT  /api/alerts/:id/resolve
GET  /api/alerts/history
```

---

## 6. Frontend Pages & UI

### Page 1 — Live Gate Dashboard (`/dashboard`)
**Purpose:** Real-time view of all gates. Main screen for security staff.

**What it shows:**
- **Gate status cards** (Entry Gate A, Exit Gate A, etc.) — each shows:
  - Last detected plate
  - Timestamp
  - Decision: ALLOWED / DENIED / ALERT (color-coded: green / red / orange)
  - Reason in plain French (e.g., "Visiteur — Session ouverte")
  - Vehicle snapshot thumbnail
- **Activity feed** — scrolling list of all events (last 50)
- **Occupancy bar** — e.g., "82/200 places occupées"
- **Active alert banner** — if a blacklisted car was just detected
- **Quick search bar** — type any plate, get instant status

**Real-time:** WebSocket connection — updates automatically without page refresh.

---

### Page 2 — Vehicle Registry (`/vehicles`)
**Purpose:** Manage all known vehicles (subscribers, VIPs, blacklist).

**What it shows:**
- **Filterable table:** All vehicles with columns: Plate | Category | Type | Owner | Status | Expires | Actions
- **Status badges:** Subscriber (blue) | VIP (gold) | Blacklist (red) | Visitor (grey)
- **Add Vehicle button** → modal form:
  - Plate number (with format validation)
  - Category selector
  - Vehicle type
  - Owner name + phone
  - Subscription expiry date (for subscribers)
  - Notes
- **Bulk import via CSV**
- **Quick blacklist button** per row
- **View history button** → shows all sessions for that vehicle
- **Search/filter:** by plate, category, status, expiry date

---

### Page 3 — Active Sessions (`/sessions/active`)
**Purpose:** See who is currently parked, running duration, estimated cost.

**What it shows:**
- Cards for each open session:
  - Plate number
  - Entry time
  - Running duration (live counter)
  - Current estimated cost
  - Vehicle category
  - Gate used
- **Over-limit highlights** — cards turn orange if vehicle exceeded max stay
- **Manual close session button** (for lost tickets / edge cases)
- **Force exit button** for emergency situations

---

### Page 4 — Session History (`/sessions`)
**Purpose:** Full billing and history for all completed sessions.

**What it shows:**
- Searchable, filterable table
- Columns: Plate | Entry | Exit | Duration | Tariff | Total | Payment | Actions
- **Dispute button** → mark a session as disputed, log reason
- **Receipt print button**
- **Export to CSV / PDF**
- **Date range picker** for filtering
- **Revenue summary bar** at top (day/week/month totals)

---

### Page 5 — Event Log (`/events`)
**Purpose:** Full audit trail — every camera detection, every decision.

**What it shows:**
- Table: Timestamp | Plate | Gate | Event Type | OCR Confidence | Decision | Rule Applied | Snapshot
- Click any row → Decision Detail modal showing:
  - Full decision log
  - Rule snapshot that was active at that moment
  - Vehicle status at that moment
  - "Ask AI" button → pre-fills assistant with that event
- **Export full log**

---

### Page 6 — AI Assistant (`/assistant`)
**Purpose:** Natural language interface for staff to query rules, explain decisions, understand billing.

**What it shows:**
- Chat-style interface (like WhatsApp / Claude)
- Sidebar with quick prompts:
  - "Pourquoi ce véhicule a été refusé ?"
  - "Quel est le tarif après 3 heures ?"
  - "Quels véhicules sont en dépassement ?"
  - "Combien de revenus ce mois-ci ?"
- Context injection: paste a plate number to focus context
- AI responses include:
  - Plain French answer
  - Source citation (e.g., "Selon l'Article 3.2 du règlement intérieur")
  - Confidence indicator
- History of past questions
- **No hallucination design** — answers are grounded in retrieved documents + real DB data

---

### Page 7 — Analytics (`/analytics`)
**Purpose:** Management reporting — revenue, occupancy, patterns.

**What it shows:**
- **Top row KPIs:** Today's revenue | Active sessions | Total entries today | Denied entries
- **Occupancy Over Time** — line chart (24h, 7d, 30d)
- **Peak Hours Heatmap** — hour vs. day of week grid, color intensity = traffic
- **Revenue Chart** — daily bars, category breakdown (visitors vs. subscribers)
- **Decision Breakdown** — pie chart: % allowed / denied / alerted
- **Top 10 Vehicles** — most frequent visitors this month
- **Gate Performance** — entries/exits per gate
- **Export as PDF Report button**

---

### Page 8 — Admin Panel (`/admin`)
**Purpose:** Full control center. Admins configure everything here. No code changes needed.

_(Detailed in Section 7 below)_

---

### Page 9 — Alerts (`/alerts`)
**Purpose:** Actionable security alerts.

**What it shows:**
- List of unresolved alerts sorted by severity
- Alert types:
  - 🔴 CRITICAL: Blacklisted vehicle entered
  - 🟠 HIGH: Duplicate plate detected at two gates simultaneously
  - 🟡 MEDIUM: Vehicle exceeded maximum stay
  - 🔵 LOW: Low OCR confidence (plate couldn't be read clearly)
- Each alert: Timestamp | Type | Plate | Gate | Message | Resolve button
- Resolved alerts archive

---

### Page 10 — User Management (`/admin/users`)
**Purpose:** Manage staff accounts and roles.

**Roles:**
- **SuperAdmin** — full access including user management and system config
- **Admin** — access to all except user management
- **Staff** — live dashboard, vehicle lookup, assistant chat
- **Viewer** — read-only analytics

**What it shows:**
- User list with role badges
- Add user form
- Reset password
- Deactivate/reactivate account
- Activity log per user

---

## 7. Admin Dashboard — Every Setting Explained

### Tab 1: Access Rules

All settings below are editable via form inputs. No backend code changes.

| Setting | Type | Description | Default |
|---|---|---|---|
| Max stay (hours) | Number | After this, vehicle flagged as overstay | 24 |
| VIP access zones | Multi-select | Which gates VIPs can use | All gates |
| Visitor auto-session | Toggle | Auto-create session when visitor enters | ON |
| Subscriber grace period | Minutes | Extra time after subscription expires before denying | 60 min |
| Unknown plate behavior | Dropdown | Allow as visitor / Deny / Alert staff | Allow as visitor |
| Blacklist auto-alert | Toggle | Trigger alert when blacklisted car detected | ON |
| Low confidence threshold | % slider | Below this OCR confidence, flag for human review | 70% |

### Tab 2: Tariff Builder

Visual rule builder — no SQL, no code.

**Tariff Profiles:** Create multiple named tariff profiles (e.g., "Weekend", "Night", "Standard").

Per profile:
| Setting | Type | Description |
|---|---|---|
| Tariff name | Text | e.g., "Tarif Standard Visiteur" |
| Vehicle types covered | Checkboxes | car / moto / truck / bus |
| First hour price | Number (TND) | Price for the first hour |
| Extra hour price | Number (TND) | Price per additional hour |
| Daily maximum | Number (TND) | Cap on total daily charge |
| Night surcharge | Multiplier (%) | e.g., 150% = 1.5x rate |
| Night hours | Time range | e.g., 22:00 → 06:00 |
| Weekend surcharge | Multiplier (%) | e.g., 120% |
| Valid from / until | Date range | Seasonal pricing |
| Active toggle | Toggle | Enable/disable this tariff |

**Tariff Preview Calculator:** Enter a duration + vehicle type, get instant price simulation using active tariffs.

### Tab 3: Gate Configuration

| Setting | Type | Description |
|---|---|---|
| Gate name | Text | e.g., "Gate A — Entrée Principale" |
| Gate type | Dropdown | Entry / Exit / Both |
| Camera IP | Text | RTSP stream URL |
| Active hours | Time range | When gate is operational |
| Auto-open delay | Seconds | How long barrier stays open |
| Fail mode | Dropdown | Fail-open (always allow) / Fail-closed (block) |

### Tab 4: Alert Rules

| Setting | Type | Description |
|---|---|---|
| Blacklist alert channel | Multi-select | In-app / Email / SMS |
| Overstay alert threshold | Hours | Trigger alert after X hours |
| Duplicate plate detection | Toggle | Alert if same plate at 2 gates simultaneously |
| Low confidence auto-flag | Toggle | Flag events below confidence threshold |
| Revenue anomaly alert | Toggle | Alert if daily revenue drops > 40% vs same day last week |
| Alert recipients | Email list | Who gets emailed for each alert type |

### Tab 5: AI Assistant Settings

| Setting | Type | Description |
|---|---|---|
| Knowledge base documents | File upload | Upload parking regulation PDFs, rule documents |
| Re-embed knowledge base | Button | Triggers re-indexing of all documents |
| LLM temperature | Slider 0-1 | Higher = more creative, lower = more precise |
| Response language | Dropdown | French / Arabic / English |
| Max answer length | Number | Characters limit on AI responses |
| Show source citations | Toggle | Show which document the answer came from |

### Tab 6: System Settings

| Setting | Type | Description |
|---|---|---|
| Parking name | Text | Shown in header and receipts |
| Total capacity | Number | Used for occupancy % calculation |
| Logo upload | File | Appears in dashboard header |
| Timezone | Dropdown | Affects all timestamps |
| Date format | Dropdown | DD/MM/YYYY vs MM/DD/YYYY |
| Currency | Text | Default: TND |
| Session timeout (staff) | Minutes | Auto-logout inactive staff |
| Snapshot retention | Days | How long to keep vehicle photos |
| Database backup schedule | Cron | e.g., "Every day at 02:00" |

### Tab 7: Rule Engine (Advanced — JSON Editor)

For power users. Shows the current rules.json with a syntax-highlighted editor. Changes are validated before saving. An audit log shows who changed what and when.

```json
{
  "access": {
    "unknown_plate": "allow_visitor",
    "expired_subscription_grace_minutes": 60,
    "blacklist_action": "deny_and_alert",
    "vip_zones": ["gate_A", "gate_B", "gate_C"]
  },
  "billing": {
    "visitor": {
      "first_hour_tnd": 2.0,
      "extra_hour_tnd": 1.0,
      "daily_max_tnd": 20.0
    },
    "truck": {
      "first_hour_tnd": 4.0,
      "extra_hour_tnd": 2.0,
      "daily_max_tnd": 30.0
    },
    "night": {
      "start": "22:00",
      "end": "06:00",
      "multiplier": 1.5
    }
  },
  "alerts": {
    "overstay_hours": 24,
    "duplicate_plate_detection": true,
    "low_confidence_threshold": 0.70
  }
}
```

---

## 8. Vision Pipeline (ALPR)

### Step 1: Data Collection

**Target:** At minimum 2,000 labeled Tunisian plate images.

Sources:
- Parking lot cameras (get permission)
- Dashcam footage
- Photographs in parking areas
- Public datasets augmented with Tunisian plates

**Labeling Tool:** Use **Roboflow** (free tier) or **LabelImg**.
Label format: YOLO format (class + bounding box normalized).
Class: `plate` (just one class)

**Augmentation (apply all of these to 10x your dataset):**
```python
# Using albumentations library
transforms = [
    A.MotionBlur(p=0.3),
    A.GaussNoise(p=0.2),
    A.RandomBrightness(limit=0.4, p=0.4),
    A.RandomShadow(p=0.3),       # simulate night/shade
    A.Perspective(scale=0.05, p=0.3),  # angle variation
    A.ImageCompression(quality_lower=50, p=0.2),  # low resolution
    A.HueSaturationValue(p=0.2),  # lighting changes
]
```

### Step 2: Train Plate Detector (YOLOv8)

```bash
# Install
pip install ultralytics

# Train
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=plates.yaml \
  epochs=100 \
  imgsz=640 \
  batch=16
```

**plates.yaml:**
```yaml
path: /data/plates
train: images/train
val: images/val
nc: 1
names: ['plate']
```

**Target metrics:**
- mAP@50 > 0.90
- Inference time < 30ms per frame on laptop GPU

### Step 3: Plate OCR

**Tunisian plate format:**
```
[1-4 digits] تونس [1-4 digits]
```
Or for government/special plates, different formats exist.

**Pipeline:**
```
Detected plate crop → Preprocess → OCR Model → Regex Validate → Normalize
```

**Preprocessing:**
```python
def preprocess_plate(img):
    # Deskew (fix rotation)
    img = deskew(img)
    # Resize to fixed height
    h, w = img.shape[:2]
    new_w = int(w * 64 / h)
    img = cv2.resize(img, (new_w, 64))
    # CLAHE for contrast enhancement (works great at night)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img = clahe.apply(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    return img
```

**OCR Options (choose one):**

Option A — EasyOCR fine-tuned (easier to implement):
```python
import easyocr
reader = easyocr.Reader(['ar', 'en'], gpu=True)
result = reader.readtext(plate_img)
```

Option B — TrOCR (more accurate, requires fine-tuning):
```python
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
# Fine-tune on Tunisian plate dataset
```

**Post-processing & normalization:**
```python
import re

def normalize_plate(raw_text):
    # Fix common OCR mistakes
    raw_text = raw_text.replace('O', '0').replace('I', '1').replace('B', '8')
    # Remove spaces
    digits_only = re.sub(r'[^\d\u0600-\u06FF]', '', raw_text)
    # Validate Tunisian format: digits + تونس + digits
    pattern = r'^\d{1,4}[\u062A\u0648\u0646\u0633]{2,4}\d{1,4}$'
    if re.match(pattern, digits_only):
        return digits_only, True
    return digits_only, False  # (text, is_valid)
```

### Step 4: Vehicle Type Detection

Add a second YOLO model (or multi-class) detecting:
- car
- truck
- motorcycle
- bus

This enables different tariff rates per vehicle type — a key business feature.

### Step 5: Tracking (DeepSORT)

Without tracking, a camera capturing 30fps would try to OCR the plate 30 times per second — wasteful and slow.

DeepSORT assigns a **track ID** to each detected vehicle. Once a plate is read with high confidence for track ID 42, all future frames for that track skip OCR.

```python
from deep_sort_realtime.deepsort_tracker import DeepSort
tracker = DeepSort(max_age=5)

tracks = tracker.update_tracks(detections, frame=frame)
for track in tracks:
    if not track.is_confirmed():
        continue
    track_id = track.track_id
    if track_id not in plate_cache:
        # OCR this plate
        plate_text = run_ocr(track.bbox)
        plate_cache[track_id] = plate_text
    # Use cached plate
    plate = plate_cache[track_id]
```

### Step 6: Event Trigger Logic

```python
def on_vehicle_detected(plate, camera_id, confidence):
    # Debounce: same plate at same gate within 30 seconds = skip
    cache_key = f"{plate}:{camera_id}"
    if redis.get(cache_key):
        return
    redis.setex(cache_key, 30, "1")
    
    # Post event to backend
    event_data = {
        "plate": plate,
        "camera_id": camera_id,
        "confidence": confidence,
        "timestamp": datetime.utcnow().isoformat()
    }
    requests.post("http://backend:8000/api/vision/plate-event", json=event_data)
```

---

## 9. AI Assistant with RAG

### Architecture

```
User Question
     ↓
[Query] → Retrieve from FAISS → [Top-K Relevant Chunks]
                ↓
     Build Context Prompt:
     - Vehicle current status (from DB)
     - Decision log (from DB)
     - Relevant rule chunks (from FAISS)
                ↓
     LLM (Mistral/Llama3) → French language answer
                ↓
     Response with source citations
```

### Knowledge Base Setup

Documents to embed:
1. `reglement_parking.pdf` — Internal parking regulation
2. `tarifs_2025.pdf` — Pricing document
3. `procedures_incidents.pdf` — How to handle disputes, accidents
4. `droits_acces.pdf` — Access categories and their rights

Embedding script:
```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Load and split documents
loader = PyPDFLoader("reglement_parking.pdf")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# Embed (multilingual model for French/Arabic)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("faiss_parking_kb")
```

### RAG Query Handler

```python
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

def answer_question(question: str, plate: str = None):
    # Get vehicle context if plate provided
    vehicle_context = ""
    if plate:
        vehicle = db.get_vehicle(plate)
        last_decision = db.get_last_decision(plate)
        vehicle_context = f"""
        Véhicule: {plate}
        Statut: {vehicle.category if vehicle else 'Inconnu'}
        Dernière décision: {last_decision.decision} — Raison: {last_decision.reason_code}
        Règle appliquée: {last_decision.rule_ref}
        """
    
    # Load vector store
    vectorstore = FAISS.load_local("faiss_parking_kb", embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # Build prompt
    llm = Ollama(model="mistral")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    
    full_question = f"{vehicle_context}\n\nQuestion: {question}"
    result = qa_chain({"query": full_question})
    
    return {
        "answer": result["result"],
        "sources": [doc.metadata for doc in result["source_documents"]]
    }
```

### Example Interactions

**Question:** "Pourquoi la voiture TN1234 a été refusée ?"
**System retrieves:**
- Decision log: `{ decision: "deny", reason_code: "BLACKLIST", rule_ref: "Article 3.2" }`
- Regulation chunk: Article 3.2 — Véhicules blacklistés…

**Response:** "Le véhicule TN1234 a été refusé car sa plaque figure sur la liste noire du parking, conformément à l'Article 3.2 du règlement intérieur. Cette liste inclut les véhicules ayant commis des infractions graves ou impayés."

---

## 10. Rule Engine (Zero Hardcoding)

The rule engine reads from the database (table: `rules`) at runtime. Admins change rules from the UI. The engine never needs redeployment.

### How Pricing is Calculated

```python
class RuleEngine:
    def __init__(self):
        self.rules = self.load_rules_from_db()
    
    def get_tariff(self, vehicle_type: str, entry_time: datetime, exit_time: datetime):
        duration_minutes = (exit_time - entry_time).seconds // 60
        
        tariff = self.rules["billing"].get(vehicle_type, self.rules["billing"]["visitor"])
        
        # Base calculation
        hours = duration_minutes / 60
        if hours <= 1:
            price = tariff["first_hour_tnd"]
        else:
            price = tariff["first_hour_tnd"] + (hours - 1) * tariff["extra_hour_tnd"]
        
        # Apply daily cap
        price = min(price, tariff["daily_max_tnd"])
        
        # Night multiplier
        if self.is_night_period(entry_time, exit_time):
            price *= self.rules["billing"]["night"]["multiplier"]
        
        return round(price, 3)
    
    def check_access(self, plate: str) -> dict:
        vehicle = db.get_vehicle(plate)
        
        if not vehicle:
            action = self.rules["access"]["unknown_plate"]
            return {"decision": "allow" if action == "allow_visitor" else "deny",
                    "reason_code": "VISITOR_UNKNOWN",
                    "rule_ref": "Rule: unknown_plate"}
        
        if vehicle.category == "blacklist":
            return {"decision": "deny", "reason_code": "BLACKLIST", "rule_ref": "Article 3.2"}
        
        if vehicle.category == "vip":
            return {"decision": "allow", "reason_code": "VIP", "rule_ref": "Article 2.1"}
        
        if vehicle.category == "subscriber":
            if vehicle.subscription_expires < datetime.today().date():
                grace = self.rules["access"]["expired_subscription_grace_minutes"]
                # Check if within grace period
                ...
        
        return {"decision": "allow", "reason_code": "VISITOR", "rule_ref": "Standard tariff"}
```

---

## 11. Smart Detection Features

### Feature 1: Duplicate Plate Detection

If the same plate is detected entering through Gate A and Gate B simultaneously (or within 2 minutes), raise a FRAUD alert.

```python
def check_duplicate(plate: str, gate_id: str, timestamp: datetime):
    recent_events = db.get_recent_events(plate, minutes=2)
    for event in recent_events:
        if event.gate_id != gate_id and event.event_type == "entry":
            alerts.create("DUPLICATE_PLATE", plate, severity="high",
                         message=f"Plaque détectée à {event.gate_id} et {gate_id} en même temps")
```

### Feature 2: Plate-Vehicle Mismatch

If a plate registered as belonging to a "car" is detected on a vehicle that the vision model classifies as a "truck" — flag it.

### Feature 3: Long Stay Alert

A background Celery task runs every 30 minutes:
```python
@celery.task
def check_overstay():
    max_hours = rules_engine.get("alerts.overstay_hours")
    open_sessions = db.get_open_sessions()
    for session in open_sessions:
        hours_parked = (datetime.utcnow() - session.entry_time).seconds / 3600
        if hours_parked > max_hours:
            alerts.create("OVERSTAY", session.plate, severity="medium",
                         message=f"Véhicule garé depuis {hours_parked:.1f}h")
```

### Feature 4: Low Confidence Flagging

If OCR confidence < threshold (configurable in admin panel), don't make an automated decision. Instead, flag the event for human review with the plate snapshot.

### Feature 5: Revenue Anomaly

Daily revenue is compared to the same day last week. If it drops by more than the configured threshold (e.g., 40%), send an alert.

### Feature 6: Peak Hour Prediction (Bonus)

Train a simple time-series model (Prophet or ARIMA) on historical entry data to predict when parking will be full. Display on analytics page.

---

## 12. Step-by-Step Build Plan (Week by Week)

### Week 1 — Foundation & Data

**Days 1–2: Project Setup**
- Initialize git repo with this structure
- Set up Docker Compose: FastAPI + PostgreSQL + Redis
- Create all database tables (use Alembic for migrations)
- Basic FastAPI skeleton with health check endpoint

**Days 3–5: Data Collection & Preparation**
- Collect minimum 500 raw Tunisian plate images
- Label with Roboflow
- Apply augmentations to reach 2,000+ images
- Split: 80% train / 10% val / 10% test
- Run augmentation pipeline and verify labels

**Days 6–7: Train Plate Detector**
- Train YOLOv8n on labeled dataset
- Evaluate on validation set (target mAP > 0.85)
- Export to ONNX format for deployment
- Test on sample video

---

### Week 2 — OCR & Backend Core

**Days 8–10: OCR Pipeline**
- Set up EasyOCR with Arabic + English
- Build preprocessing pipeline (deskew, CLAHE, resize)
- Build post-processing (regex validation, normalization)
- Create evaluation script: test on 100 plate images, measure accuracy
- Target: > 85% correct reads

**Days 11–12: Backend API Core**
- Implement all database models with SQLAlchemy
- `/api/vision/plate-event` endpoint
- `/api/vehicles` CRUD
- `/api/sessions` management
- `/api/events` audit log
- JWT authentication for all routes

**Days 13–14: Integration Test**
- Run YOLO + OCR on video file
- POST results to backend
- Verify database entries
- Test session open/close logic

---

### Week 3 — Rule Engine & Admin Panel

**Days 15–17: Rule Engine**
- Build RuleEngine class (reads from DB rules table)
- Implement access check logic (blacklist, VIP, subscriber, visitor)
- Implement tariff calculation
- Write unit tests for all rule scenarios:
  - Visitor enters → session created
  - Subscriber expired → grace period applied
  - Blacklisted → denied + alert created
  - VIP → allowed immediately

**Days 18–19: Frontend Scaffold**
- Set up React + TypeScript + Vite + ShadCN
- Build routing structure
- Implement JWT login flow
- Live Dashboard page (mock data first)
- WebSocket connection to backend

**Days 20–21: Admin Panel**
- Build all admin settings tabs
- Rule editor with live preview
- Tariff builder with price simulation
- Gate configuration form
- Connect all forms to `/api/rules` and `/api/tariffs` endpoints

---

### Week 4 — AI, Polish & Demo

**Days 22–23: RAG Assistant**
- Set up Ollama locally with Mistral 7B
- Create parking knowledge base documents (or use sample PDFs)
- Build embedding pipeline
- Implement `/api/assistant/chat` endpoint
- Build chat UI page

**Days 24–25: Advanced Features**
- Duplicate plate detection
- Long stay alerts
- Analytics page with real data
- Alert system

**Days 26–27: Full Integration & Testing**
- End-to-end test with real camera or video file
- Verify entire flow: camera → plate read → decision → dashboard update → AI explanation
- Fix bugs, edge cases
- Performance testing (latency per event)

**Days 28: Demo Preparation**
- Record demo video (see script in Section 14)
- Prepare presentation slides
- Write final report
- Package everything for submission

---

## 13. Evaluation & Metrics

### ALPR Metrics

| Metric | Target | How to Measure |
|---|---|---|
| Plate Detection mAP@50 | > 0.90 | YOLO validation output |
| Plate Detection mAP@50:95 | > 0.75 | YOLO validation output |
| OCR Accuracy (exact match) | > 85% | Compare OCR output vs ground truth |
| OCR Character Accuracy | > 95% | Per-character correctness |
| Processing time per frame | < 100ms | Benchmark on demo machine |
| End-to-end latency (camera → decision) | < 500ms | Timed event pipeline |

### System Metrics

| Metric | Target |
|---|---|
| Decision accuracy (correct allow/deny) | > 99% |
| False positive rate (allowed when should deny) | < 0.1% |
| False negative rate (denied when should allow) | < 1% |
| API response time (p95) | < 200ms |

### AI Assistant Metrics

| Metric | Target | How to Measure |
|---|---|---|
| Retrieval precision (relevant chunks retrieved) | > 80% | Manual evaluation of 20 questions |
| Answer factual accuracy | > 90% | Cross-check with source documents |
| Response time | < 3 seconds | Benchmark |

---

## 14. Demo Video Script

**Duration:** 3–5 minutes

**Scene 1 (0:00–0:30) — Introduction**
Show parking lot context. Brief problem statement in voiceover.

**Scene 2 (0:30–1:30) — Normal Visitor Entry**
- Camera detects car entering
- Dashboard shows real-time: plate detected, bounding box visible
- System shows: "Visiteur — TN-5842 — Session ouverte — Barrière levée"
- Session card appears in Active Sessions page

**Scene 3 (1:30–2:00) — VIP Entry**
- Different car detected
- Dashboard: "VIP — TN-0001 — Accès autorisé — Priorité"
- Instant barrier open

**Scene 4 (2:00–2:30) — Blacklisted Car**
- Car enters gate
- Dashboard turns RED instantly
- Alert popup: "⚠️ VÉHICULE BLACKLISTÉ — TN-9999"
- Barrier stays CLOSED
- Alert appears in alerts page

**Scene 5 (2:30–3:00) — Staff asks AI: "Pourquoi refusé?"**
- Staff types in AI assistant: "Pourquoi TN-9999 a été refusé ?"
- AI responds: "TN-9999 est inscrit sur la liste noire conformément à l'Article 3.2 du règlement intérieur. Cette décision a été prise automatiquement le [timestamp]."
- Show source citation highlighted

**Scene 6 (3:00–3:30) — Billing Question to AI**
- Staff asks: "Quel est le tarif pour un visiteur après 3 heures ?"
- AI: "Selon le tarif visiteur en vigueur : 2 TND la première heure + 1 TND par heure supplémentaire. Pour 3 heures = 4 TND. Plafond journalier : 20 TND."

**Scene 7 (3:30–4:00) — Admin Changes Rule**
- Open admin panel
- Change "first_hour_price" from 2 TND to 3 TND
- Save
- AI immediately answers with new tariff

**Scene 8 (4:00–4:30) — Analytics**
- Show occupancy chart, revenue dashboard, peak hour heatmap

**Closing:** System logo, team name, contact.

---

## 15. Folder Structure

```
tunipark-ai/
│
├── backend/                          # FastAPI application
│   ├── app/
│   │   ├── main.py                   # App entry point
│   │   ├── config.py                 # Environment config
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── vehicle.py
│   │   │   ├── event.py
│   │   │   ├── session.py
│   │   │   ├── decision.py
│   │   │   ├── tariff.py
│   │   │   ├── rule.py
│   │   │   └── user.py
│   │   ├── routers/                  # API route handlers
│   │   │   ├── auth.py
│   │   │   ├── vision.py
│   │   │   ├── vehicles.py
│   │   │   ├── sessions.py
│   │   │   ├── events.py
│   │   │   ├── rules.py
│   │   │   ├── tariffs.py
│   │   │   ├── analytics.py
│   │   │   ├── assistant.py
│   │   │   └── alerts.py
│   │   ├── services/                 # Business logic
│   │   │   ├── rule_engine.py        # Core decision engine
│   │   │   ├── billing.py            # Tariff calculation
│   │   │   ├── alert_service.py
│   │   │   └── session_service.py
│   │   ├── ai/                       # RAG assistant
│   │   │   ├── embedder.py           # Document embedding
│   │   │   ├── retriever.py          # FAISS retrieval
│   │   │   └── chat_handler.py       # LLM query builder
│   │   └── db.py                     # Database connection
│   ├── alembic/                      # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── vision/                           # Computer vision pipeline
│   ├── detector/
│   │   ├── yolo_detector.py          # Plate detection
│   │   └── vehicle_classifier.py     # Car/truck/moto
│   ├── ocr/
│   │   ├── preprocessor.py           # Image preprocessing
│   │   ├── ocr_engine.py             # EasyOCR / TrOCR
│   │   └── postprocessor.py          # Regex, normalization
│   ├── tracker/
│   │   └── deepsort_tracker.py       # Vehicle tracking
│   ├── camera/
│   │   └── stream_handler.py         # RTSP camera reader
│   ├── event_poster.py               # Posts to backend API
│   ├── main.py                       # Vision pipeline entry point
│   └── requirements.txt
│
├── training/                         # Model training scripts
│   ├── data/
│   │   ├── raw/                      # Raw collected images
│   │   ├── labeled/                  # After labeling
│   │   └── augmented/                # After augmentation
│   ├── augment.py                    # Augmentation pipeline
│   ├── train_detector.py             # YOLOv8 training
│   ├── train_ocr.py                  # OCR fine-tuning
│   ├── evaluate.py                   # Metric evaluation
│   └── plates.yaml                   # YOLO dataset config
│
├── knowledge_base/                   # RAG documents
│   ├── reglement_parking.pdf
│   ├── tarifs_2025.pdf
│   ├── procedures_incidents.pdf
│   └── droits_acces.pdf
│
├── frontend/                         # React application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx         # Live gate view
│   │   │   ├── Vehicles.tsx          # Vehicle registry
│   │   │   ├── ActiveSessions.tsx
│   │   │   ├── SessionHistory.tsx
│   │   │   ├── EventLog.tsx
│   │   │   ├── Assistant.tsx         # AI chat
│   │   │   ├── Analytics.tsx
│   │   │   ├── Alerts.tsx
│   │   │   └── Admin/
│   │   │       ├── AdminPanel.tsx
│   │   │       ├── AccessRules.tsx
│   │   │       ├── TariffBuilder.tsx
│   │   │       ├── GateConfig.tsx
│   │   │       ├── AlertRules.tsx
│   │   │       ├── AISettings.tsx
│   │   │       ├── SystemSettings.tsx
│   │   │       ├── RuleEditor.tsx
│   │   │       └── UserManagement.tsx
│   │   ├── components/               # Reusable UI components
│   │   ├── store/                    # Zustand state
│   │   ├── hooks/                    # Custom React hooks
│   │   └── api/                      # API client functions
│   └── package.json
│
├── docker-compose.yml                # Full stack orchestration
├── nginx.conf                        # Reverse proxy config
└── README.md
```

---

*Built for the IIT/NAU Smart Parking AI Competition — Tunisia 2025*
