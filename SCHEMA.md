# 📊 TunisParк AI — Business Logic & Schema Reference
### Pre-Coding Explanation Document — Read This Before Writing a Single Line

> This document explains **what the system does and why** at the business logic level.  
> Use it to explain the project to supervisors, teammates, or judges before the demo.

> **Implementation note (Feb 2026):** The schema described here is fully implemented in
> `backend/app/models/`. All 8 tables are created via Alembic migrations.
> See [CURRENT_IMPLEMENTATION.md](CURRENT_IMPLEMENTATION.md) for live status.

---

## Table of Contents

1. [What Is This System Doing, Simply Explained](#1-what-is-this-system-doing-simply-explained)
2. [The 5 Core Concepts](#2-the-5-core-concepts)
3. [Vehicle Categories — Who Is Who](#3-vehicle-categories--who-is-who)
4. [The Decision Tree — What Happens When a Car Arrives](#4-the-decision-tree--what-happens-when-a-car-arrives)
5. [Session Lifecycle — From Entry to Exit](#5-session-lifecycle--from-entry-to-exit)
6. [How Pricing Works — The Tariff Logic](#6-how-pricing-works--the-tariff-logic)
7. [The Rule Engine — Why We Don't Hardcode Anything](#7-the-rule-engine--why-we-dont-hardcode-anything)
8. [The AI Assistant — What It Actually Does](#8-the-ai-assistant--what-it-actually-does)
9. [Data Flow — From Camera Pixel to Dashboard Update](#9-data-flow--from-camera-pixel-to-dashboard-update)
10. [Database Relationships Explained](#10-database-relationships-explained)
11. [Alert Logic — When the System Raises Flags](#11-alert-logic--when-the-system-raises-flags)
12. [User Roles & Permissions Map](#12-user-roles--permissions-map)
13. [Edge Cases & How They Are Handled](#13-edge-cases--how-they-are-handled)
14. [What the Admin Can Change Without a Developer](#14-what-the-admin-can-change-without-a-developer)

---

## 1. What Is This System Doing, Simply Explained

Imagine a parking lot at a hospital. Every day, 300 cars enter and exit. The security guard manually:

- Writes down plate numbers on a paper register
- Issues paper tickets
- Tries to remember which car is blacklisted
- Argues with drivers about exact entry times
- Struggles to answer "how much do I owe?"

This system **replaces all of that** with:

1. A camera reads every plate automatically as the car approaches the barrier
2. The system looks up the plate in its database in less than 1 second
3. The barrier opens or stays closed based on business rules the admin configured
4. A session timer starts automatically
5. When the car exits, billing is calculated automatically
6. Any staff member can ask the AI assistant "why was that car refused?" and get an answer citing the exact regulation

**No more paper. No more arguments. No more errors. No more manual work.**

---

## 2. The 5 Core Concepts

### Concept 1: The Plate is the Identity

In this system, **the license plate number is the primary identity of a vehicle**. There are no physical tickets, no RFID cards, no QR codes. The camera reads the plate, and everything else follows from that.

A plate like `202 تونس 5256` maps to a vehicle record in the database that says: "This car belongs to Dr. Ahmed Ben Ali, it's a subscriber, and its subscription expires March 31, 2025."

### Concept 2: Every Action is an Event

Every time the camera detects a plate — whether the car is entering or exiting — it creates an **Event** record. Events are never deleted. They are the permanent audit trail. If there is ever a dispute ("I entered at 14:00, not 14:45!"), the system shows the exact event with a camera snapshot.

### Concept 3: A Session is an Entry-Exit Pair

A **Session** is opened when a car enters and closed when that car exits. The session holds:
- Entry time (from the entry Event)
- Exit time (from the exit Event)
- Duration
- Cost (calculated from the active Tariff)
- Payment status

Sessions are what get billed.

### Concept 4: Rules Live in the Database

Unlike traditional systems where a developer hardcodes pricing ("first hour = 2 TND"), this system stores all rules in the database. The admin can open the dashboard, change "first hour = 3 TND", save, and the new price takes effect immediately — no developer needed, no redeployment, no downtime.

### Concept 5: Every Decision is Explainable

When the system allows or denies entry to a car, it doesn't just open/close the barrier silently. It creates a **Decision** record that says:
- What was decided (allow / deny)
- Why (reason code: BLACKLIST, VIP, EXPIRED_SUBSCRIPTION, etc.)
- Which rule was applied (e.g., "Article 3.2")
- A snapshot of the rule at that moment

The AI assistant reads these decision records to answer staff questions without making anything up.

---

## 3. Vehicle Categories — Who Is Who

```
┌─────────────────────────────────────────────────────────────┐
│                    VEHICLE CATEGORIES                        │
├──────────────┬──────────────────────────────────────────────┤
│  VISITOR     │ Unknown car. No prior registration.          │
│              │ → Allowed in as paying customer              │
│              │ → Session starts, billing applies            │
│              │ → No special privileges                      │
├──────────────┼──────────────────────────────────────────────┤
│  SUBSCRIBER  │ Registered vehicle with active subscription  │
│              │ → Allowed in based on subscription validity  │
│              │ → No hourly billing while subscription valid │
│              │ → Gets flagged if subscription expired       │
│              │ → Grace period applies (configurable)        │
├──────────────┼──────────────────────────────────────────────┤
│  VIP         │ Special access vehicles (executives, VIPs)   │
│              │ → Always allowed                             │
│              │ → No billing                                 │
│              │ → May have access to restricted zones        │
│              │ → Logged but not billed                      │
├──────────────┼──────────────────────────────────────────────┤
│  BLACKLIST   │ Banned vehicles                              │
│              │ → Always denied                              │
│              │ → Alert triggered immediately                │
│              │ → Barrier never opens                        │
│              │ → Reason stored in vehicle notes             │
├──────────────┼──────────────────────────────────────────────┤
│  CONDITIONAL │ Vehicles with access restrictions            │
│              │ → May only enter during specific hours       │
│              │ → May only use specific gates                │
│              │ → May require manual confirmation            │
└──────────────┴──────────────────────────────────────────────┘
```

**Who decides the category?**
An admin or authorized staff member assigns a category to a vehicle through the Vehicle Registry page. Visitors who are never registered remain "unknown" and are treated as standard visitors.

---

## 4. The Decision Tree — What Happens When a Car Arrives

```
Car approaches gate
        │
        ▼
Camera detects car → YOLO model finds plate
        │
        ▼
OCR reads plate number
        │
        ├─── Confidence < 70%? ──────────────────► Flag for human review
        │                                           (don't make automated decision)
        ▼
Plate normalized: "1234TN5678"
        │
        ▼
Look up plate in database
        │
        ├─── Not found ──────────────────────────► Check rule: unknown_plate
        │                                           ├── "allow_visitor" → Allow + start session
        │                                           └── "deny" → Deny + alert
        │
        ├─── BLACKLIST ──────────────────────────► DENY + Critical alert + snapshot saved
        │
        ├─── VIP ────────────────────────────────► ALLOW + Log (no billing)
        │
        ├─── SUBSCRIBER ─────────────────────────► Check subscription_expires date
        │                                           ├── Valid → ALLOW + log entry
        │                                           └── Expired → Check grace period
        │                                                         ├── Within grace → ALLOW + warn
        │                                                         └── Beyond grace → DENY
        │
        └─── VISITOR (known) ────────────────────► ALLOW + start billing session
                │
                ▼
        Decision record saved:
        { decision, reason_code, rule_ref, rule_data, gate_action, timestamp }
                │
                ▼
        WebSocket event → Frontend dashboard updates in real time
                │
                ▼
        Gate command: OPEN or STAY CLOSED
```

---

## 5. Session Lifecycle — From Entry to Exit

### Opening a Session

When an unknown visitor or registered visitor enters:

```
Event: ENTRY detected (plate: 1234TN5678, gate: gate_A, time: 14:23:11)
        │
        ▼
Session created:
{
  plate: "1234TN5678",
  entry_event_id: <event uuid>,
  entry_time: "2025-03-15 14:23:11",
  status: "open",
  tariff_id: <active visitor tariff>,
  exit_time: null,
  duration: null,
  total_price: null
}
```

### Active Session (Car is Parked)

The session exists in "open" status. The frontend shows it in Active Sessions with:
- A live timer counting up
- Running estimated cost (recalculated every minute)
- Alert if approaching overstay threshold

### Closing a Session

When the same plate is detected at an EXIT gate:

```
Event: EXIT detected (plate: 1234TN5678, gate: gate_A_exit, time: 17:05:44)
        │
        ▼
Find last OPEN session for plate 1234TN5678
        │
        ▼
Calculate duration:
17:05:44 - 14:23:11 = 2 hours, 42 minutes = 162 minutes
        │
        ▼
Apply tariff:
- First hour: 2.000 TND
- Remaining 1h42m (rounded up to 2h): 2 × 1.000 TND = 2.000 TND
- Total: 4.000 TND
- Daily max check: 4.000 < 20.000 → no cap applied
        │
        ▼
Session updated:
{
  exit_event_id: <exit event uuid>,
  exit_time: "2025-03-15 17:05:44",
  duration_minutes: 162,
  total_price: 4.000,
  status: "closed"
}
        │
        ▼
Gate opens → Car exits
```

### Session Edge Cases

**Car exits without being detected entering:**
The system creates a session with `entry_time = null`. Admin is alerted. The session can be manually edited.

**Car detected entering twice (re-entry):**
The system checks if the plate has an open session. If yes, it logs a warning but doesn't create a second session. The existing session continues.

**Car stays overnight:**
The session remains open. Night rate multiplier applies to the nighttime portion of the stay. Overstay alert fires after the configured threshold.

---

## 6. How Pricing Works — The Tariff Logic

### Standard Tariff Calculation

```
Given:
- Entry: 14:00
- Exit: 18:30
- Duration: 4.5 hours
- Vehicle type: car
- Active tariff: { first_hour: 2 TND, extra_hour: 1 TND, daily_max: 20 TND }

Calculation:
Step 1 → First hour: 2.000 TND
Step 2 → Remaining time: 3.5 hours → ceil to 4 hours → 4 × 1.000 = 4.000 TND
Step 3 → Subtotal: 6.000 TND
Step 4 → Daily max check: 6.000 < 20.000 → no cap
Step 5 → Night multiplier check: 14:00–18:30 → no night hours crossed → multiplier = 1.0
Final: 6.000 TND
```

### Night Rate Example

```
Entry: 20:00 | Exit: 23:30 | Night hours: 22:00–06:00 | Night multiplier: 1.5

Time segments:
- 20:00 → 22:00 = 2 hours at standard rate
- 22:00 → 23:30 = 1.5 hours at night rate (× 1.5)

Calculation:
Standard portion: first hour (2 TND) + 1 extra hour (1 TND) = 3.000 TND
Night portion: 1.5 hours × 1 TND × 1.5 = 2.250 TND
Total: 5.250 TND
```

### Truck vs. Car

Different vehicle types have separate tariff rows. A truck might have:
- First hour: 4 TND (instead of car's 2 TND)
- Extra hour: 2 TND

The system automatically selects the tariff that matches the vehicle type detected by the vision model.

---

## 7. The Rule Engine — Why We Don't Hardcode Anything

### The Problem with Hardcoding

If a developer writes `first_hour_price = 2.0` directly in Python code, then:
- Changing the price requires a developer
- Changing the price requires redeployment
- The system goes offline during update
- Non-technical admins can't make changes
- No audit trail of who changed what

### The Solution: Rules as Data

This system stores all rules in a database table called `rules`. Each rule has:
- A key (e.g., `billing.visitor.first_hour_tnd`)
- A value (e.g., `2.0`)
- A description
- A category
- Last updated by (who changed it)
- Last updated at (when it was changed)

The rule engine code **reads from this table at runtime**, never from hardcoded values.

### Rule Categories

**Access Rules** — Who can enter, who gets denied, edge cases:
- `unknown_plate` → "allow_visitor" or "deny"
- `subscriber_grace_minutes` → 60
- `blacklist_action` → "deny_and_alert" or "deny_silently"
- `low_confidence_threshold` → 0.70

**Billing Rules** — How much to charge:
- `visitor.first_hour_tnd` → 2.0
- `visitor.extra_hour_tnd` → 1.0
- `visitor.daily_max_tnd` → 20.0
- `truck.first_hour_tnd` → 4.0
- `night.multiplier` → 1.5
- `night.start` → "22:00"
- `weekend.multiplier` → 1.2

**Alert Rules** — When to trigger alarms:
- `overstay_hours` → 24
- `duplicate_plate_detection` → true
- `revenue_drop_alert_pct` → 40

**Schedule Rules** — Time-based behavior:
- `gate_a_operating_hours` → "07:00–22:00"
- `weekend_tariff_active` → true

### How the Admin Changes Rules

1. Admin logs into the dashboard
2. Navigates to Admin Panel → Rule Engine tab
3. Sees a JSON editor or form fields for each rule
4. Changes a value
5. Clicks Save
6. The change is written to the `rules` table with their user ID and timestamp
7. The rule engine reads the new value on the **next event** — no restart needed

---

## 8. The AI Assistant — What It Actually Does

### The Core Problem It Solves

Staff often face questions they can't quickly answer:
- "Why was this car denied? I need to explain it to the driver."
- "What is the tariff for trucks after 18:00?"
- "Which vehicles have been here for more than 5 hours?"
- "Can subscribers use Gate B?"

Without AI: Staff would need to read printed regulation documents, call a supervisor, or manually query the database.

With AI: They type the question in French, and the assistant answers in under 3 seconds, citing the exact rule it's using.

### What RAG Means (Simply Explained)

RAG = Retrieval-Augmented Generation

**Step 1 — Knowledge Base Preparation (done once at setup)**
The admin uploads parking regulation PDFs to the system. The system reads these PDFs, splits them into small chunks (paragraphs), and converts each chunk into a mathematical vector (a list of numbers that captures its meaning). All these vectors are stored in a fast search index called FAISS.

**Step 2 — Answering a Question**
When a staff member asks "Why was TN-9999 denied?":
1. The question is also converted into a vector
2. FAISS searches for the regulation chunks most similar to this question
3. The top 4 most relevant chunks are retrieved
4. The system also fetches the actual decision record from the database: `{ decision: "deny", reason_code: "BLACKLIST", rule_ref: "Article 3.2" }`
5. All of this context (retrieved regulations + real decision data) is combined into one big prompt
6. The LLM (Mistral) reads this context and writes a coherent answer in French

### Why It Doesn't Hallucinate

Most AI chatbots make up information because they're working from memory alone. This system is different:

- **Decision data comes from the database** — it's a fact, not generated
- **Regulation quotes come from retrieved documents** — retrieved, not invented
- **The LLM is only used to compose readable French** from real facts

If no relevant regulation chunk is found, the AI says "Je n'ai pas trouvé d'information précise dans les documents disponibles" — not invent something.

---

## 9. Data Flow — From Camera Pixel to Dashboard Update

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Camera captures frame (25–30 fps)                       │
│  Raw pixel data → Vision service                                │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓ every frame
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: YOLO detects if a plate is visible                      │
│  If no plate found → discard frame, continue                    │
│  If plate found → extract bounding box                          │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓ when plate detected
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: DeepSORT tracker checks if this is a new vehicle        │
│  If already tracked → use cached plate text (skip OCR)          │
│  If new vehicle → run OCR pipeline                              │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓ new vehicle
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: OCR reads the plate                                     │
│  Preprocessing (deskew, enhance contrast)                       │
│  OCR model outputs: "١٢٣٤ تونس ٥٦٧٨"                           │
│  Post-processing normalizes to: "1234TN5678"                    │
│  Confidence score computed: 0.91                                │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Redis debounce check                                    │
│  Has "1234TN5678 + gate_A" been posted in last 30 seconds?      │
│  YES → skip (same car still at barrier)                         │
│  NO → proceed + set Redis key (expires in 30s)                  │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓ new event
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: POST to Backend API                                     │
│  { plate: "1234TN5678", gate: "gate_A", confidence: 0.91,       │
│    camera_id: "cam_01", vehicle_type: "car", timestamp: now }   │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Backend processes event                                 │
│  a. Save Event record to PostgreSQL                             │
│  b. Rule Engine checks vehicle status                           │
│  c. Decision made: ALLOW / DENY                                 │
│  d. Decision record saved with rule reference                   │
│  e. Session opened (if applicable)                              │
│  f. Alert created (if applicable)                               │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: Real-time update to Frontend                            │
│  Backend sends WebSocket message to all connected dashboards    │
│  { type: "gate_event", plate, decision, gate_id, timestamp }    │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: Dashboard updates without page refresh                  │
│  Activity feed shows new event                                  │
│  Gate card shows last detected plate + decision color           │
│  If denied: alert banner appears                                │
│  If session opened: new card in Active Sessions                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 10: Gate hardware receives command                         │
│  ALLOW → GPIO signal / API call to barrier controller → OPEN    │
│  DENY → no signal → barrier stays CLOSED                        │
└─────────────────────────────────────────────────────────────────┘

Total time from pixel to decision: < 500ms
```

---

## 10. Database Relationships Explained

```
┌──────────────────────────────────────────────────────────────────┐
│                    ENTITY RELATIONSHIPS                           │
│                                                                  │
│   vehicles                                                       │
│   ┌────────────────────┐                                         │
│   │ id (PK)            │◄──────────────────────────────────┐    │
│   │ plate (unique)     │                                   │    │
│   │ category           │                                   │    │
│   │ vehicle_type       │                                   │    │
│   │ owner_name         │                                   │    │
│   │ subscription_ends  │                                   │    │
│   └─────────┬──────────┘                                   │    │
│             │ (plate = foreign key by value, not UUID)      │    │
│             │                                               │    │
│        ┌────▼────────────────────┐   ┌─────────────────┐   │    │
│        │ events                  │   │ sessions         │   │    │
│        │ id (PK)                 │   │ id (PK)          │   │    │
│        │ plate                   │   │ plate            │   │    │
│        │ event_type (entry/exit) │   │ entry_event_id ──┼───┘   │
│        │ gate_id                 │   │ exit_event_id  ──┼───┐   │
│        │ camera_id               │   │ entry_time       │   │    │
│        │ confidence              │   │ exit_time        │   │    │
│        │ image_path              │   │ duration_minutes │   │    │
│        │ timestamp               │   │ total_price      │   │    │
│        └────────┬────────────────┘   │ tariff_id ───────┼───┐   │
│                 │                    │ status           │   │   │
│        ┌────────▼────────────────┐   └──────────────────┘   │   │
│        │ decisions               │                           │   │
│        │ id (PK)                 │   tariffs                 │   │
│        │ event_id (FK)           │   ┌────────────────────┐  │   │
│        │ plate                   │   │ id (PK) ◄──────────┼──┘   │
│        │ decision (allow/deny)   │   │ name               │      │
│        │ reason_code             │   │ vehicle_type       │      │
│        │ rule_ref                │   │ first_hour_price   │      │
│        │ rule_data (JSONB)       │   │ extra_hour_price   │      │
│        │ gate_action             │   │ daily_max          │      │
│        │ timestamp               │   │ night_multiplier   │      │
│        └─────────────────────────┘   └────────────────────┘      │
│                                                                  │
│   rules                              alerts                      │
│   ┌────────────────────┐             ┌────────────────────────┐  │
│   │ id (PK)            │             │ id (PK)                │  │
│   │ rule_key (unique)  │             │ alert_type             │  │
│   │ rule_value (JSONB) │             │ plate                  │  │
│   │ description        │             │ event_id (FK)          │  │
│   │ is_active          │             │ severity               │  │
│   │ updated_by (FK)    │             │ message                │  │
│   │ updated_at         │             │ is_resolved            │  │
│   └────────────────────┘             └────────────────────────┘  │
│                                                                  │
│   users                                                          │
│   ┌────────────────────┐                                         │
│   │ id (PK)            │◄── updated_by in rules                 │
│   │ email              │◄── resolved_by in alerts               │
│   │ password_hash      │                                         │
│   │ role               │                                         │
│   │ is_active          │                                         │
│   └────────────────────┘                                         │
└──────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions Explained

**Why is `plate` stored as a string everywhere instead of a foreign key to vehicles?**

Because not every plate in `events` will be in the `vehicles` table. Unknown visitors generate events without having a vehicle record. If we used a foreign key, we'd need to create a dummy vehicle record for every unknown plate — that gets messy. Storing plate as text allows any plate to generate events.

**Why is `rule_data` stored as JSONB in decisions?**

Because rules change over time. If we only store `rule_ref = "Article 3.2"`, and then Article 3.2 gets updated, we'd lose what the rule actually said when the decision was made. By snapshotting the full rule JSON at decision time, we have a complete audit trail.

**Why are tariffs a separate table from rules?**

Tariffs have structured fields (prices, multipliers, validity dates) that benefit from typed columns and query filters. The generic `rules` table is for flexible, rarely-queried configuration. The split keeps both clean.

---

## 11. Alert Logic — When the System Raises Flags

### Alert Types and Their Triggers

```
ALERT TYPE              TRIGGER                             SEVERITY
──────────────────────────────────────────────────────────────────────
BLACKLIST_ENTRY       → Blacklisted plate detected          CRITICAL
DUPLICATE_PLATE       → Same plate at 2 gates <2min apart   HIGH
PLATE_MISMATCH        → Registered as car, detected as truck HIGH
LOW_CONFIDENCE        → OCR confidence < threshold          LOW
OVERSTAY              → Session open > max_hours            MEDIUM
EXPIRED_SUBSCRIPTION  → Subscriber allowed on grace period  LOW
REVENUE_ANOMALY       → Daily revenue drops > threshold%    MEDIUM
GATE_OFFLINE          → Camera not responding               HIGH
```

### Alert Lifecycle

```
Trigger condition met
        ↓
Alert created: { type, plate, severity, message, is_resolved: false }
        ↓
Dashboard shows red banner (CRITICAL) or orange notification badge
        ↓
Staff sees alert in Alerts page
        ↓
Staff investigates (can click "View Event" to see snapshot)
        ↓
Staff clicks "Resolve" + optional note
        ↓
Alert updated: { is_resolved: true, resolved_by: user_id, resolved_at: now }
        ↓
Alert moves to history (no longer in active list)
```

### Background Job Alerts

Some alerts can't be triggered by a single event — they need background monitoring:

**Overstay check** (runs every 30 minutes via Celery):
```
For each OPEN session:
  hours_parked = now - entry_time
  if hours_parked > rules["overstay_hours"]:
    create OVERSTAY alert (only if not already alerted for this session)
```

**Revenue anomaly check** (runs daily at midnight):
```
today_revenue = sum of closed session prices today
same_day_last_week_revenue = sum from 7 days ago
if today_revenue < same_day_last_week_revenue * (1 - threshold):
  create REVENUE_ANOMALY alert
```

---

## 12. User Roles & Permissions Map

```
ACTION                          VIEWER  STAFF   ADMIN   SUPERADMIN
──────────────────────────────────────────────────────────────────
View live dashboard               ✓       ✓       ✓         ✓
View event log                    ✓       ✓       ✓         ✓
View session history              ✓       ✓       ✓         ✓
Use AI assistant                  ✗       ✓       ✓         ✓
Search vehicles                   ✓       ✓       ✓         ✓
Add/edit vehicles                 ✗       ✓       ✓         ✓
Blacklist a vehicle               ✗       ✗       ✓         ✓
Manually close a session          ✗       ✓       ✓         ✓
Mark session as disputed          ✗       ✓       ✓         ✓
View analytics                    ✓       ✓       ✓         ✓
Export reports                    ✗       ✓       ✓         ✓
Change tariff rules               ✗       ✗       ✓         ✓
Change access rules               ✗       ✗       ✓         ✓
Change gate configuration         ✗       ✗       ✓         ✓
Upload AI knowledge documents     ✗       ✗       ✓         ✓
Manage users                      ✗       ✗       ✗         ✓
View system settings              ✗       ✗       ✓         ✓
Change system settings            ✗       ✗       ✗         ✓
Access raw rule JSON editor       ✗       ✗       ✗         ✓
```

---

## 13. Edge Cases & How They Are Handled

### Edge Case 1: Car exits without a recorded entry
**Scenario:** The entry camera missed the car (bad angle, camera was offline).
**Handling:** 
- Exit event is created normally
- System searches for an open session for that plate → none found
- A "ghost session" is created with `entry_time = null`
- Alert is raised: "Exit without matching entry detected for [plate]"
- Admin can manually set the entry time if known

### Edge Case 2: Same plate appears at entry and exit gates simultaneously
**Scenario:** Two cars with the same plate number (cloned plates, common fraud).
**Handling:**
- Second detection triggers DUPLICATE_PLATE alert
- System allows both but flags both events
- Decision records both have `reason_code: "POSSIBLE_FRAUD"`
- Admin reviews the snapshot images to identify which plate is real

### Edge Case 3: OCR reads the plate wrong (e.g., 1O34 instead of 1034)
**Scenario:** Camera reads "O" instead of "0".
**Handling:**
- Post-processor applies correction rules (O→0, I→1, B→8)
- Corrected plate is stored as `plate`, original as `raw_plate`
- Confidence score reflects OCR uncertainty
- If confidence < threshold, event is flagged for human review

### Edge Case 4: Subscriber renewal — system hasn't been updated yet
**Scenario:** A subscriber renewed their subscription but the admin hasn't updated the expiry date in the system yet.
**Handling:**
- Grace period rule applies (configurable, default 60 minutes)
- Car is allowed with a LOW warning alert
- Alert says: "Subscriber subscription expired but within grace period — please verify renewal"

### Edge Case 5: Power failure or camera goes offline
**Scenario:** Camera disconnects. Barrier is stuck.
**Handling:**
- Gate is configured with "Fail mode" in admin panel
- "Fail-open" → barrier opens automatically (used in hospital/emergency settings)
- "Fail-closed" → barrier stays closed, staff must open manually
- System creates a GATE_OFFLINE alert
- All events during the outage are marked with `camera_id: "cam_OFFLINE"`

### Edge Case 6: Night rate spans two days (e.g., entry 23:00, exit 02:00)
**Scenario:** Session crosses midnight.
**Handling:**
- Duration is calculated from absolute timestamps (not clock positions)
- Night rate applies to the portion between 22:00–06:00
- The billing engine splits the session into daytime and nighttime segments and applies multipliers to each

### Edge Case 7: Admin changes pricing mid-session
**Scenario:** A car entered at 14:00. At 16:00, admin changes the tariff. Car exits at 18:00.
**Handling:**
- The tariff applied to a session is locked at the **time the session opens**
- `tariff_id` is set when the session is created and never changes
- The car pays the tariff that was active when it entered

---

## 14. What the Admin Can Change Without a Developer

This is what makes this system production-grade. **Everything below can be changed from the dashboard with zero technical knowledge, zero code changes, and zero downtime.**

### ✅ Pricing
- First hour price (per vehicle type)
- Extra hour price (per vehicle type)
- Daily maximum cap
- Night rate multiplier and hours
- Weekend rate multiplier
- Creating a new seasonal tariff (holiday pricing)
- Enabling/disabling any tariff

### ✅ Access Policies
- What to do with unknown plates (allow or deny)
- Subscriber grace period duration
- Which gates VIPs can access
- Low confidence threshold for auto-flagging

### ✅ Alerts
- Who gets email notifications for each alert type
- Overstay threshold
- Revenue drop threshold
- Toggle duplicate plate detection on/off

### ✅ Gate Configuration
- Camera IP addresses
- Gate operating hours
- Barrier fail mode (open vs. closed)
- Auto-open duration

### ✅ AI Assistant
- Upload new regulation documents (they auto-embed)
- Change response language (French / Arabic / English)
- Change AI detail level

### ✅ Vehicle Registry
- Add new subscribers, VIPs, blacklisted vehicles
- Update subscription expiry dates
- Bulk import vehicles via CSV

### ❌ What Still Needs a Developer

- Adding a new page to the frontend UI
- Integrating a new payment gateway
- Adding a new type of alert that doesn't exist yet
- Changing the plate OCR model
- Database schema changes

Everything else: admin-controlled. ✅

---

*This document should be read before any coding begins. It defines what the system is, how it works, and why every design choice was made the way it was.*

*For implementation details, see PROJECT.md*
