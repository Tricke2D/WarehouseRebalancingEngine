# 🏭 Multi-Warehouse Inventory + Rebalancing Engine

**Production-Grade Inventory Management | Smart Rebalancing | FastAPI | PostgreSQL | Redis | React Dashboard**

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?logo=redis&logoColor=white)
![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Daftar Isi

- [📍 Studi Kasus](#-studi-kasus)
- [✨ Fitur Utama](#-fitur-utama)
- [🏗️ Arsitektur Sistem](#️-arsitektur-sistem)
- [🛠️ Tech Stack](#️-tech-stack)
- [💻 Requirements](#-requirements)
- [🚀 Instalasi & Menjalankan](#-instalasi--menjalankan)
- [📝 API Reference](#-api-reference)
- [🧪 Testing & Load Testing](#-testing--load-testing)
- [📊 Dashboard](#-dashboard)
- [📁 Struktur Project](#-struktur-project)
- [⚠️ Batasan & Roadmap](#️-batasan--roadmap)
- [📞 Kontribusi](#-kontribusi)

---

## 📍 Studi Kasus

Bayangkan kamu memiliki data pipeline inventory di perusahaan **e-commerce atau retail dengan banyak gudang tersebar di berbagai kota**. Setiap hari, ribuan SKU harus dikelola dan didistribusikan secara efisien.

### Masalah yang Dipecahkan

Tanpa sistem inventory yang cerdas, terjadi:

- ❌ **Stock Imbalance** — Gudang A kelebihan stok, Gudang B kekurangan
- ❌ **Manual Allocation** — Operator harus menentukan gudang mana yang memenuhi order
- ❌ **Oversell** — Stok yang sama dipesan oleh banyak customer bersamaan
- ❌ **No Demand Visibility** — Tidak tahu gudang mana yang perlu di-replenish
- ❌ **Manual Transfer** — Transfer stock antar gudang dilakukan tanpa data

### Solusi: Smart Warehouse Rebalancing Engine

Sistem manajemen inventory **multi-gudang dengan smart rebalancing otomatis** (production-grade):

✅ **Smart Allocation** — Pilih gudang terdekat dengan stok cukup untuk setiap order  
✅ **SELECT FOR UPDATE** — Atomic stock reservation, anti-oversell di bawah 500 concurrent request  
✅ **Demand Velocity** — Hitung rata-rata permintaan per SKU per gudang (7-day window)  
✅ **Auto Rebalancing** — Deteksi oversupply/undersupply dan suggest transfer otomatis  
✅ **Transfer State Machine** — SUGGESTED → APPROVED → IN_TRANSIT → COMPLETED  
✅ **500 Concurrent Support** — Terbukti dengan Locust stress test  
✅ **React Dashboard** — Heatmap stock + transfer review UI  
✅ **Chaos Test** — Atomicity terjamin walau connection drop di tengah transaksi  

**Hasil:** Database-backed inventory system yang **scalable, fault-tolerant, dan real-time**.

---

## ✨ Fitur Utama

### 🎯 Core Features

| Fitur | Deskripsi |
|-------|-----------|
| **Smart Allocation** | Pilih gudang terdekat (Haversine distance) dengan stock cukup |
| **Atomic Reservation** | `SELECT FOR UPDATE` mencegah oversell |
| **Split Order** | Jika 1 gudang tidak cukup, split ke 2 gudang |
| **Demand Velocity** | Hitung rata-rata permintaan per SKU per gudang (7 hari) |
| **Auto Rebalancing** | Deteksi oversupply/undersupply dan suggest transfer |
| **Transfer State Machine** | SUGGESTED → APPROVED → IN_TRANSIT → COMPLETED |
| **Real-time Dashboard** | Heatmap + transfer review UI (React + Tailwind) |

### 📊 Business Logic

| Komponen | Deskripsi |
|----------|-----------|
| **Oversupply Threshold** | Stock > 2x avg_demand → kelebihan stok |
| **Undersupply Threshold** | Stock < 0.5x avg_demand → kekurangan stok |
| **Transfer Quantity** | MIN(excess, shortage) dari gudang oversupply ke undersupply |
| **Nightly Rebalance Job** | Auto-run tiap jam 02:00 via APScheduler |
| **Active Expiry** | Background cleanup untuk key yang expired (mirip Redis TTL) |

### 🔒 Concurrency & Safety

| Fitur | Deskripsi |
|-------|-----------|
| **SELECT FOR UPDATE** | Row-level locking di PostgreSQL |
| **Optimistic Locking** | `version` column untuk race condition detection |
| **Chaos Test** | 20x connection kill before commit → atomicity terjamin |
| **Locust Stress Test** | 500 concurrent users → 0 oversell |

### 📈 Dashboard Read Models

| Endpoint | Deskripsi |
|----------|-----------|
| `/v1/dashboard/heatmap` | Data stock matrix (gudang x SKU) untuk heatmap |
| `/v1/dashboard/summary` | Total warehouse, SKU, stock units, pending transfers |

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────────┐
│           Warehouse Rebalancing Engine — Architecture                  │
└─────────────────────────────────────────────────────────────────────────┘

            ┌─────────────────────────────────────────────────┐
            │         Frontend (React + Tailwind)             │
            │  • Stock Heatmap                                │
            │  • Transfer Review                              │
            │  • Real-time Summary                            │
            └────────────────┬────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   HTTP/REST     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐
   │  FastAPI    │   │   Celery     │   │   APScheduler    │
   │  (Async)    │   │   Workers    │   │   (Scheduled)    │
   │ • Orders    │   │ • Async jobs │   │ • Nightly job    │
   │ • Transfers │   │ • Events     │   │   02:00 UTC      │
   │ • Dashboard │   │              │   │                  │
   └────────┬────┘   └──────┬───────┘   └─────────┬────────┘
            │               │                     │
            └───────────────┼─────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   ┌──────────────┐  ┌─────────────┐  ┌───────────────────┐
   │  PostgreSQL  │  │   Redis     │  │  File System      │
   │   (Metadata) │  │   (Broker)  │  │  (Logs, Backups)  │
   │              │  │             │  │                   │
   │ • warehouses │  │ Celery task │  └───────────────────┘
   │ • skus       │  │   queue     │
   │ • stock_lvl  │  │             │
   │ • orders     │  │ Job status  │
   │ • transfers  │  │             │
   └──────────────┘  └─────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Flow                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Order Allocation:                                                    │
│     Customer → POST /allocate → AllocationService →                      │
│     SELECT FOR UPDATE → Reserve Stock → Response                         │
│                                                                          │
│  2. Nightly Rebalancing:                                                 │
│     APScheduler (02:00) → Rebalancing Job →                             │
│     DemandVelocity → Detect Oversupply/Undersupply →                    │
│     Generate Transfer Suggestions → Store in DB                         │
│                                                                          │
│  3. Transfer Approval & Execution:                                       │
│     Admin → Approve → Ship → IN_TRANSIT →                               │
│     Receive → COMPLETED → Update Stock                                  │
│                                                                          │
│  4. Dashboard:                                                           │
│     Frontend → GET /heatmap → Stock Matrix →                            │
│     React Heatmap Visualization                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### System Components

**Frontend Layer**
- React 18 + Vite untuk development cepat
- Tailwind CSS + Recharts untuk UI yang responsive
- Real-time updates setiap 3 detik

**API Layer**
- FastAPI async untuk high-throughput request handling
- Pydantic validation untuk type safety
- Swagger documentation auto-generated

**Business Logic**
- AllocationService: Smart gudang selection
- ReservationService: Atomic stock locking
- RebalancingService: Oversupply/undersupply detection
- TransferService: State machine management

**Persistence**
- PostgreSQL: Main data store (ACID guarantees)
- Redis: Celery broker + caching
- Alembic: Database versioning

**Scheduled Tasks**
- APScheduler: Nightly rebalance job (02:00 UTC)
- Celery: Async event processing
- Background cleanup: Expired records

---

## 🛠️ Tech Stack

| Komponen | Teknologi | Rationale |
|----------|-----------|-----------|
| **Backend** | Python 3.12 + FastAPI | Async I/O, type hints, fast development |
| **ORM** | SQLAlchemy 2.0 (async) | Type-safe queries, relationship management |
| **Database** | PostgreSQL 16 | ACID, row-level locking, JSON support |
| **Message Broker** | Redis 7.0 | Fast, in-memory, Celery compatible |
| **Task Queue** | Celery 5.6 | Distributed async task processing |
| **Scheduler** | APScheduler | Timezone-aware job scheduling |
| **Frontend** | React 18 + TypeScript + Vite | Modern, type-safe, fast dev server |
| **Styling** | TailwindCSS 3 + Recharts | Utility-first CSS, charting library |
| **Testing** | Pytest + pytest-asyncio + Locust | Unit, integration, load testing |
| **Containerization** | Docker + Docker Compose | Reproducible environments |
| **CLI** | Typer | Type-annotated CLI |

---

## 💻 Requirements

- **Python** v3.12 atau lebih baru
- **Docker** v20.x atau lebih baru (PostgreSQL + Redis)
- **Node.js** v18.x atau lebih baru (Frontend)
- **npm** v9.x atau lebih baru

---

## 🚀 Instalasi & Menjalankan

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Tricke2D/WarehouseRebalancingEngine.git
cd WarehouseRebalancingEngine
```

### 2️⃣ Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Setup Infrastructure (Docker Compose)

```bash
# Start PostgreSQL + Redis
docker-compose up -d

# Verify containers running
docker-compose ps
```

### 4️⃣ Initialize Database

```bash
# Create migrations
alembic init migrations

# Edit alembic.ini with your database URL
# sqlalchemy.url = postgresql+asyncpg://wh_user:wh_pass@localhost:5432/warehouse_db

# Run migrations
alembic upgrade head

# Seed test data
docker exec -it wh_postgres psql -U wh_user -d warehouse_db << EOF
INSERT INTO warehouses (code, name, latitude, longitude, city, is_active) VALUES
('WH-JKT-01', 'Gudang Jakarta', -6.2088, 106.8456, 'Jakarta', true),
('WH-SBY-01', 'Gudang Surabaya', -7.2575, 112.7521, 'Surabaya', true),
('WH-BDG-01', 'Gudang Bandung', -6.9175, 107.6191, 'Bandung', true);

INSERT INTO skus (code, name, unit_price, weight_kg) VALUES
('SKU-LAPTOP-PRO', 'Laptop Pro 15"', 15000000, 2.1),
('SKU-MOUSE-USB', 'Mouse USB Wireless', 250000, 0.1);

INSERT INTO stock_levels (warehouse_id, sku_id, quantity, reserved_quantity, version) VALUES
(1, 1, 50, 0, 1),
(1, 2, 200, 0, 1),
(2, 1, 30, 0, 1),
(2, 2, 150, 0, 1),
(3, 1, 10, 0, 1),
(3, 2, 80, 0, 1);
EOF
```

### 5️⃣ Run Backend Services

**Terminal 1: FastAPI Server**

```bash
uvicorn src.main:app --reload --port 8000
```

**Terminal 2: Scheduler (APScheduler)**

```bash
python -m src.scheduler
```

**Terminal 3: Celery Workers (Optional)**

```bash
celery -A src.celery_app worker --loglevel=info
```

### 6️⃣ Run Frontend

```bash
cd frontend
npm install
npm run dev

# Access dashboard at http://localhost:5173
```

### 7️⃣ Verify Setup

| Service | URL | Check |
|---------|-----|-------|
| Backend API | `http://localhost:8000` | Should respond with FastAPI docs |
| Swagger Docs | `http://localhost:8000/api/docs` | Interactive API documentation |
| Health Check | `http://localhost:8000/health` | Should return `{"status": "ok"}` |
| Frontend | `http://localhost:5173` | React dashboard loaded |

---

## 📝 API Reference

### Allocation Endpoints

#### POST `/v1/orders/allocate`

Allocate order ke gudang terbaik berdasarkan distance & availability.

**Request:**

```json
{
  "sku_id": 1,
  "quantity": 5,
  "delivery_latitude": -6.4025,
  "delivery_longitude": 106.7942
}
```

**Response (Success - 200):**

```json
{
  "success": true,
  "allocations": [
    {
      "warehouse_id": 1,
      "warehouse_code": "WH-JKT-01",
      "quantity": 5,
      "distance_km": 25.3
    }
  ],
  "is_split": false,
  "message": "Stock berhasil di-reserve"
}
```

**Response (Split Order - 200):**

```json
{
  "success": true,
  "allocations": [
    {
      "warehouse_id": 1,
      "warehouse_code": "WH-JKT-01",
      "quantity": 3,
      "distance_km": 25.3
    },
    {
      "warehouse_id": 2,
      "warehouse_code": "WH-SBY-01",
      "quantity": 2,
      "distance_km": 450.0
    }
  ],
  "is_split": true,
  "message": "Order split across 2 warehouses"
}
```

**Response (Insufficient Stock - 409):**

```json
{
  "detail": {
    "error_code": "NO_STOCK",
    "message": "Tidak ada gudang dengan stock cukup untuk 5 unit",
    "requested": 5,
    "available": 2
  }
}
```

---

### Transfer Endpoints

#### GET `/v1/transfers`

List semua transfer order dengan filter.

**Query Params:**

```
status=SUGGESTED          # Filter by status
warehouse_id=1            # Filter by warehouse
limit=10                  # Pagination
offset=0
```

**Response (200):**

```json
[
  {
    "id": 1,
    "transfer_number": "TRF-20260806045037350168",
    "from_warehouse_id": 1,
    "from_warehouse_code": "WH-JKT-01",
    "to_warehouse_id": 2,
    "to_warehouse_code": "WH-SBY-01",
    "sku_id": 1,
    "sku_code": "SKU-LAPTOP-PRO",
    "quantity": 1,
    "status": "SUGGESTED",
    "suggestion_reason": "Gudang 1 oversupply (stock 50 > 2x demand 15)",
    "created_at": "2026-08-06T04:50:37.336091Z",
    "updated_at": "2026-08-06T04:50:37.336091Z"
  }
]
```

#### PATCH `/v1/transfers/{id}/approve`

Approve transfer suggestion (SUGGESTED → APPROVED).

**Response (200):**

```json
{
  "id": 1,
  "status": "APPROVED",
  "updated_at": "2026-08-06T05:00:00.000Z"
}
```

#### PATCH `/v1/transfers/{id}/reject`

Reject transfer suggestion (SUGGESTED → REJECTED).

**Request:**

```json
{
  "rejection_reason": "Stock sudah cukup setelah re-evaluasi"
}
```

**Response (200):**

```json
{
  "id": 1,
  "status": "REJECTED",
  "rejection_reason": "Stock sudah cukup setelah re-evaluasi",
  "updated_at": "2026-08-06T05:00:00.000Z"
}
```

#### PATCH `/v1/transfers/{id}/ship`

Ship transfer (APPROVED → IN_TRANSIT). Stock dikurangi dari gudang asal.

**Response (200):**

```json
{
  "id": 1,
  "status": "IN_TRANSIT",
  "shipped_at": "2026-08-06T05:00:00.000Z"
}
```

#### PATCH `/v1/transfers/{id}/receive`

Receive transfer (IN_TRANSIT → COMPLETED). Stock ditambahkan ke gudang tujuan.

**Response (200):**

```json
{
  "id": 1,
  "status": "COMPLETED",
  "received_at": "2026-08-06T06:00:00.000Z"
}
```

---

### Dashboard Endpoints

#### GET `/v1/dashboard/heatmap`

Data stock matrix untuk heatmap visualization.

**Response (200):**

```json
{
  "warehouses": [
    {"id": 1, "code": "WH-JKT-01", "name": "Gudang Jakarta", "city": "Jakarta"},
    {"id": 2, "code": "WH-SBY-01", "name": "Gudang Surabaya", "city": "Surabaya"}
  ],
  "skus": [
    {"id": 1, "code": "SKU-LAPTOP-PRO", "name": "Laptop Pro", "unit_price": 15000000},
    {"id": 2, "code": "SKU-MOUSE-USB", "name": "Mouse USB", "unit_price": 250000}
  ],
  "cells": [
    {
      "warehouse_id": 1,
      "sku_id": 1,
      "quantity": 50,
      "reserved_quantity": 5,
      "available": 45,
      "utilization_pct": 10.0,
      "demand_velocity_7d": 15,
      "status": "healthy"
    }
  ]
}
```

#### GET `/v1/dashboard/summary`

Summary statistics untuk dashboard overview.

**Response (200):**

```json
{
  "total_warehouses": 3,
  "total_skus": 2,
  "total_stock_units": 520,
  "total_reserved_units": 5,
  "pending_transfer_suggestions": 1,
  "oversupply_count": 2,
  "undersupply_count": 1
}
```

---

### Testing Endpoints (Development Only)

#### POST `/v1/testing/reset-stock`

Reset stock untuk keperluan testing. **Hanya aktif dalam development mode!**

**Query Params:**

```
warehouse_id=1   # ID gudang (required)
sku_id=1         # ID SKU (required)
quantity=100     # Target quantity (required)
```

**Example:**

```bash
curl -X POST "http://localhost:8000/v1/testing/reset-stock?warehouse_id=1&sku_id=1&quantity=100"
```

**Response (200):**

```json
{
  "warehouse_id": 1,
  "sku_id": 1,
  "quantity_before": 50,
  "quantity_after": 100
}
```

---

## 🧪 Testing & Load Testing

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Specific test module
pytest tests/unit/test_geolocation.py -v

# With coverage report
pytest --cov=src tests/ --cov-report=html
```

### Integration Tests

```bash
# Race condition test (SELECT FOR UPDATE)
pytest tests/integration/test_stock_reservation.py -v -s

# Transfer state machine tests
pytest tests/integration/test_transfer_state_machine.py -v

# All integration tests
pytest tests/integration/ -v
```

### Stress Test (Locust)

```bash
# 1. Reset stock to 1 unit
curl -X POST "http://localhost:8000/v1/testing/reset-stock?warehouse_id=1&sku_id=1&quantity=1"

# 2. Run Locust with 500 concurrent users
locust -f loadtests/locustfile.py \
  --headless \
  -u 500 \
  -r 100 \
  --run-time 30s \
  --host http://localhost:8000

# Or with web UI (access http://localhost:8089)
locust -f loadtests/locustfile.py --host http://localhost:8000
```

**Expected Results:**

```
============================================================
STRESS TEST SUMMARY
============================================================
Successful allocations   : 1
Rejected (insufficient)  : 499
Unexpected errors        : 0
Response time (95%)      : 45ms
Requests/sec            : ~1500
============================================================

✅ All requests ended gracefully (200 or 409)
✅ No data corruption or race conditions
```

### Chaos Test (Atomicity Verification)

```bash
# Test database atomicity under connection failures
python loadtests/chaos_test.py

# Expected output:
# Simulating 20x connection kill before commit...
# ✅ PASS: Stock tidak berubah setelah 20x simulasi crash
# ✅ PASS: Hanya transaksi yang commit yang tercatat
# ✅ PASS: Crash transactions rollback bersih
# 🎉 ALL CHAOS TESTS PASSED
```

---

## 📊 Dashboard

### Setup Frontend

```bash
cd frontend
npm install
npm run dev

# Access at http://localhost:5173
```

### Dashboard Features

| Feature | Deskripsi |
|---------|-----------|
| **Stock Heatmap** | Visualisasi stock per gudang per SKU (warna = utilization %) |
| **Transfer Review** | List transfer suggestions dengan tombol Approve/Reject/Ship/Receive |
| **Summary Cards** | Total warehouse, SKU, stock units, pending transfers, oversupply count |
| **Real-time Updates** | Auto-refresh setiap 3 detik |
| **Responsive Design** | Mobile-friendly dengan Tailwind CSS |

### Heatmap Color Legend

| Utilization | Color | Meaning |
|------------|-------|---------|
| **0-20%** | 🟢 Hijau | Aman, stock cukup |
| **20-50%** | 🟡 Kuning | Moderate utilization |
| **50-80%** | 🟠 Orange | High utilization |
| **80-100%** | 🔴 Merah | Kritis, perlu replenish |

### Dashboard Sections

**1. Summary Cards (Top)**
- Total Warehouses
- Total SKUs
- Total Stock Units
- Pending Transfer Suggestions
- Oversupply Count
- Undersupply Count

**2. Stock Heatmap (Center)**
- X-axis: SKU codes
- Y-axis: Warehouse codes
- Cell color: Utilization percentage
- Cell hover: Show quantity details

**3. Transfer Review Table (Bottom)**
- Sortable columns: Transfer #, Status, From→To, Quantity, Reason
- Action buttons: Approve, Reject, Ship, Receive
- Status badges: Color-coded by state

---

## 📁 Struktur Project

```
WarehouseRebalancingEngine/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── pytest.ini
├── README.md
│
├── src/
│   ├── main.py                             # FastAPI entry point
│   ├── scheduler.py                        # APScheduler bootstrap
│   ├── celery_app.py                       # Celery configuration
│   │
│   ├── api/v1/
│   │   ├── __init__.py
│   │   ├── routes_allocation.py            # POST /orders/allocate
│   │   ├── routes_transfer.py              # Transfer CRUD + state machine
│   │   ├── routes_dashboard.py             # Heatmap + summary
│   │   └── routes_testing.py               # Testing endpoints (dev only)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                       # Pydantic settings
│   │   ├── database.py                     # Async SQLAlchemy engine
│   │   └── redis_client.py                 # Redis connection pool
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── enums.py                        # OrderStatus, TransferStatus
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── warehouse.py                # ORM model
│   │   │   ├── sku.py
│   │   │   ├── stock_level.py
│   │   │   ├── order.py
│   │   │   └── transfer_order.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── allocation.py               # Request/response schemas
│   │       └── transfer.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── allocation_service.py           # Smart allocation strategy
│   │   ├── reservation_service.py          # SELECT FOR UPDATE logic
│   │   ├── demand_velocity_service.py      # 7-day velocity calculation
│   │   ├── rebalancing_service.py          # Oversupply/undersupply detection
│   │   ├── transfer_service.py             # Transfer state machine
│   │   └── geolocation_service.py          # Haversine distance calc
│   │
│   ├── jobs/
│   │   ├── __init__.py
│   │   └── nightly_rebalance_job.py        # Scheduled job (02:00 UTC daily)
│   │
│   └── messaging/
│       ├── __init__.py
│       └── events.py                       # Event publishing (RabbitMQ/Redis)
│
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       └── 001_initial_schema.py           # Initial database schema
│
├── tests/
│   ├── conftest.py                         # Pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_geolocation.py
│   │   ├── test_demand_velocity.py
│   │   ├── test_rebalancing_logic.py
│   │   └── test_allocation_strategy.py
│   │
│   └── integration/
│       ├── __init__.py
│       ├── test_stock_reservation.py       # Race condition tests
│       ├── test_transfer_state_machine.py
│       └── test_end_to_end.py              # Full workflow test
│
├── loadtests/
│   ├── locustfile.py                       # Locust load test scenarios
│   ├── chaos_test.py                       # Connection failure test
│   └── docker_kill_test.sh                 # Container kill simulation
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js                   # Axios HTTP client
│   │   ├── components/
│   │   │   ├── StockHeatmap.jsx            # Recharts heatmap
│   │   │   ├── TransferReviewTable.jsx
│   │   │   └── SummaryCards.jsx
│   │   ├── pages/
│   │   │   └── DashboardPage.jsx
│   │   ├── hooks/
│   │   │   └── usePolling.js              # Real-time polling
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── scripts/
│   ├── init_db.sh                          # Database initialization
│   ├── seed_data.sql                       # Test data
│   └── docker_kill_test.sh                 # Chaos test
│
└── docs/
    ├── ARCHITECTURE.md                     # Detailed architecture
    ├── API_REFERENCE.md                    # Full API docs
    ├── DEPLOYMENT.md                       # Production deployment guide
    └── TROUBLESHOOTING.md                  # FAQ & common issues
```

---

## ⚠️ Batasan & Roadmap

### Batasan Saat Ini

| Batasan | Penjelasan | Solusi Future |
|---------|-----------|----------------|
| **No Authentication** | API tanpa auth, hanya untuk development | JWT + role-based access control |
| **No Webhook** | Belum ada webhook untuk integrasi third-party | Webhook support (Stripe, Shopify) |
| **Single Instance** | Belum di-scale dengan Kubernetes | K8s deployment dengan HPA |
| **No CI/CD** | Belum ada pipeline otomatis | GitHub Actions / GitLab CI |
| **RDBMS Only** | Hanya PostgreSQL, tidak support SQLite/MySQL | Multi-database support |
| **No Caching Layer** | Semua query ke database | Redis caching untuk read-heavy queries |
| **Manual Deployment** | Docker Compose lokal saja | Fly.io / Railway / AWS deployment |

### Roadmap Pengembangan

- ☐ **Authentication** — JWT login/register dengan multi-tenant support
- ☐ **Webhook Support** — Trigger external systems (Stripe, Shopify, custom)
- ☐ **Kubernetes** — Helm charts, HPA, service mesh (Istio)
- ☐ **CI/CD Pipeline** — GitHub Actions: lint, test, deploy
- ☐ **Multi-Database** — SQLite/MySQL support with database abstraction
- ☐ **Caching Strategy** — Redis caching untuk read-heavy queries
- ☐ **E2E Testing** — Playwright for UI automation
- ☐ **WebSocket Support** — Live dashboard updates (Socket.IO)
- ☐ **Monitoring & Observability** — Prometheus + Grafana + ELK
- ☐ **Production Deployment** — Fly.io / Railway / AWS setup guide
- ☐ **Advanced Analytics** — SKU trends, warehouse performance reports
- ☐ **Multi-language** — i18n support (EN, ID, ZH)
- ☐ **Mobile App** — React Native companion app

---

## 📞 Kontribusi

**Repository:** https://github.com/Tricke2D/WarehouseRebalancingEngine

**Issues:** https://github.com/Tricke2D/WarehouseRebalancingEngine/issues

**Discussions:** https://github.com/Tricke2D/WarehouseRebalancingEngine/discussions

Contributions are welcome! 🎉 

### How to Contribute

1. Fork repository ini
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request dengan deskripsi yang jelas

### Development Guidelines

- Write tests untuk setiap fitur baru
- Follow PEP 8 untuk Python code
- Keep commit history clean (rebase sebelum PR)
- Update documentation sesuai perubahan

---

## 📜 License

**MIT License** — Silakan digunakan untuk keperluan belajar, pengembangan, dan produksi.

```
Made with ❤️ by [Your Name]
© 2024 Warehouse Rebalancing Engine
```

---

## 🤝 Support

Jika ada pertanyaan atau butuh bantuan:

- 📧 Email: `your-email@example.com`
- 💬 GitHub Discussions: https://github.com/Tricke2D/WarehouseRebalancingEngine/discussions
- 🐛 Report Bugs: https://github.com/Tricke2D/WarehouseRebalancingEngine/issues/new

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [PostgreSQL SELECT FOR UPDATE](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR)
- [Celery Task Queue](https://docs.celeryproject.org/)
- [React Hooks](https://react.dev/reference/react)
- [TailwindCSS](https://tailwindcss.com/)

---

**Last Updated:** August 2026  
**Version:** 1.0.0
