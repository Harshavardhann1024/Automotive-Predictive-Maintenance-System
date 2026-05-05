# 🚗 Automotive Predictive Maintenance System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**An AI-powered fleet management platform that predicts vehicle failures before they happen.**

*Real-time telemetry monitoring • ML-based failure prediction • Professional PDF reporting*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Screenshots](#-screenshots)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [PDF Report System](#-pdf-report-system)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

The **Automotive Predictive Maintenance System** is a full-stack web application designed to monitor vehicle fleet health in real-time and predict potential failures using machine learning models. It provides fleet managers with actionable insights, automated alerts, and professional analytics reports to minimize downtime and optimize maintenance schedules.

### Problem Statement

Fleet operators face significant costs from unplanned vehicle breakdowns. Traditional reactive maintenance leads to:
- **40% higher** repair costs vs. preventive approaches
- **Unexpected downtime** causing operational delays
- **Safety risks** from undetected component degradation

### Solution

This system leverages **IoT sensor data** and **predictive ML models** to:
- Continuously monitor vehicle health scores
- Predict component failures **before** they occur
- Prioritize maintenance based on risk severity
- Generate professional reports for stakeholders

---

## ✨ Key Features

### 📊 Executive Dashboard
- Real-time fleet KPI cards (Total Vehicles, Active Alerts, Avg Health Score, High Risk Count)
- Interactive Fleet Health Trend and Risk Forecast charts (Recharts)
- Recent Critical Alerts feed with severity indicators
- One-click PDF report generation

### 🚘 Vehicle Management
- Comprehensive vehicle registry with health scores, risk levels, and status
- Individual vehicle detail pages with telemetry data
- Search and filter by registration, model, or VIN
- Real-time mileage, fuel level, and location tracking

### 🔮 Predictive Analytics
- ML-powered failure probability predictions per vehicle
- Remaining Useful Life (RUL) estimation
- Risk categorization (Low / Medium / High)
- Suggested maintenance priority scheduling

### 🔔 Smart Alerts
- Automated alerts based on sensor anomaly detection
- Severity classification: Critical, High, Medium, Low
- Alert lifecycle management (Active → Acknowledged → Resolved)
- Searchable alert history with vehicle-level filtering

### 📄 Professional PDF Reports
- **7-page** executive-quality PDF reports generated on demand
- Cover page, KPI summary, vehicle health tables, alerts analysis
- Matplotlib-generated charts embedded directly into PDF
- Recommendations & insights section with actionable items
- CSV export option for raw data analysis

### 👤 User Authentication & Profiles
- JWT-based secure authentication (login / register)
- Role-based access (Admin, Engineer, Viewer)
- User profile page with account details

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | High-performance async REST API framework |
| **SQLAlchemy** | Async ORM for database operations |
| **PostgreSQL** | Primary relational database |
| **Alembic** | Database migration management |
| **ReportLab** | Professional PDF report generation |
| **Matplotlib** | Chart/graph generation for reports |
| **JWT (PyJWT)** | Secure token-based authentication |
| **Uvicorn** | ASGI server for production deployment |

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | Component-based UI framework |
| **Vite 5** | Lightning-fast build tool & dev server |
| **React Router v6** | Client-side routing & navigation |
| **Recharts** | Interactive data visualization charts |
| **Lucide React** | Modern icon library |
| **Axios** | HTTP client for API communication |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │Dashboard │ │Vehicles  │ │ Alerts   │ │  Reports  │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │
│       │             │            │              │        │
│       └─────────────┴────────────┴──────────────┘        │
│                         │ Axios                          │
└─────────────────────────┼────────────────────────────────┘
                          │ REST API (JSON / PDF Blob)
┌─────────────────────────┼────────────────────────────────┐
│                    Backend (FastAPI)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │Auth      │ │Dashboard │ │ Alerts   │ │  Reports  │  │
│  │Router    │ │Router    │ │ Router   │ │  Router   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └─────┬─────┘  │
│       │             │            │              │        │
│  ┌────┴─────────────┴────────────┴──────────────┴─────┐  │
│  │              Service Layer                         │  │
│  │  MLService · SensorService · ReportGenerator       │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │ SQLAlchemy (Async)                │
└───────────────────────┼──────────────────────────────────┘
                        │
               ┌────────┴────────┐
               │   PostgreSQL    │
               │   Database      │
               └─────────────────┘
```

---

## 📸 Screenshots

> *Login → Dashboard → Vehicles → Alerts → Reports → PDF Download*

The application features a modern, professional UI with:
- **Dark sidebar navigation** with active state indicators
- **Card-based dashboard** with real-time metrics
- **Interactive charts** (Fleet Health Trend, Risk Forecast, Alert Frequency)
- **Color-coded tables** with severity badges
- **One-click PDF generation** with loading spinners

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **PostgreSQL 14+** (running locally or remote)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/MayurKk777/Automotive-Predictive-Maintenance-System.git
cd Automotive-Predictive-Maintenance-System
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt
pip install reportlab matplotlib  # For PDF report generation

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials:
#   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/automotive_db
#   SECRET_KEY=your-secret-key

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**
Interactive docs at **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
# Navigate to frontend (from project root)
cd frontend-vite

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at **http://localhost:5173**

### 4. Login

Use the Registration page to create a new account, or use existing test credentials if seeded.

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login-json` | Login and receive JWT token |
| `GET` | `/users/me` | Get current user profile |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/dashboard/api/dashboard/summary` | Fleet summary KPIs |
| `GET` | `/dashboard/reports` | Generate executive PDF report |

### Vehicles
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/vehicles/` | List all vehicles |
| `POST` | `/vehicles/` | Register a new vehicle |
| `GET` | `/viz/vehicle-overview/{id}` | Vehicle detail with telemetry |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/alerts` | List all alerts |
| `PATCH` | `/alerts/{id}/acknowledge` | Acknowledge an alert |
| `PATCH` | `/alerts/{id}/resolve` | Resolve an alert |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/reports/generate?format=pdf&type=general` | Generate PDF report |
| `GET` | `/reports/generate?format=csv&type=general` | Generate CSV export |
| `GET` | `/reports/export/zip` | Export all data as ZIP |

### Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/predictions/` | Get failure predictions |

---

## 📁 Project Structure

```
Automotive-Predictive-Maintenance-System/
│
├── backend/                          # FastAPI Backend
│   ├── agents/                       # Master, Prediction, Action agents
│   ├── api/                          # Routers and endpoints
│   ├── core/                         # Database, auth, and central logic
│   ├── models/                       # SQLAlchemy/DB models
│   ├── schemas/                      # Pydantic schemas
│   ├── services/                     # Business logic
│   ├── templates/                    # Email/Notification templates
│   └── main.py                       # FastAPI app entrypoint
│
├── frontend/                         # React Frontend (Vite)
│
├── ml/                               # Machine Learning
│   ├── training/                     # Training scripts (v3, v4)
│   ├── inference/                    # Prediction logic
│   ├── models/                       # Saved models (.pkl)
│   └── notebooks/                    # Jupyter notebooks
│
├── data/                             # Data files
│   ├── raw/                          # Original CSV files
│   └── processed/                    # Cleaned/Augmented data
│
├── database/                         # Database files
│   └── maintenance.db
│
├── scripts/                          # Utility scripts
│   ├── seed_data.py
│   ├── test_email.py
│   └── trigger_alert.py
│
├── config/                           # Configuration
├── tests/                            # Unit & integration tests
├── docs/                             # Documentation
├── .env                              # Environment variables
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

### 🧹 Reorganizing Existing Projects

If you are upgrading from an older version of this system with scattered files, run the provided reorganization script:

```bash
python3 reorganize.py
```

This script will automatically move files into the new structure and update Python imports accordingly.

---

## 📄 PDF Report System

The system generates **professional, 7-page PDF reports** using ReportLab and Matplotlib.

### Report Structure

| Page | Content |
|------|---------|
| **1** | **Cover Page** — Title, report metadata, date, confidentiality notice |
| **2** | **Executive Summary** — 8 KPI cards, fleet condition overview, urgency notes |
| **3** | **Vehicle Health Overview** — Full data table, top risky & healthiest vehicles |
| **4** | **Alerts & Predictions** — Alert summary table, prediction insights with priority |
| **5** | **Visual Analytics** — Health bar chart, risk distribution pie, failure probability chart |
| **6** | **Charts (cont.)** — Alerts severity breakdown pie chart |
| **7** | **Recommendations** — Immediate attention items, maintenance priorities, monitoring actions |

### How It Works

1. **User clicks** "Generate Report" (Dashboard) or "PDF" button (Reports page)
2. **Frontend** sends `GET /reports/generate?format=pdf` with auth token
3. **Backend** runs `report_generator.py`:
   - Builds page layouts with ReportLab Platypus
   - Generates 4 matplotlib charts as temporary PNG images
   - Inserts charts into the PDF document
   - Applies color-coded tables, KPI cards, and styled sections
4. **Response** returns as `application/pdf` blob with `Content-Disposition` header
5. **Frontend** creates a download link via `URL.createObjectURL()` and triggers browser download

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---


