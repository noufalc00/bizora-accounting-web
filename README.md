# Bizora Accounting Web Application

Standalone web application for Bizora Accounting - full feature parity with desktop app.

## Tech Stack

- **Backend:** Python FastAPI
- **Frontend:** React + TypeScript + TailwindCSS
- **Database:** PostgreSQL
- **Deployment:** Render

## Features

Complete accounting system with:
- Multi-company management
- User authentication & role-based access
- Double-entry accounting engine
- Sales, Purchase, Returns, Quotations, Orders
- Cash/Bank vouchers, Journal entries
- Stock management with movements
- 40+ financial reports
- GST compliance reports
- Barcode management
- Print settings
- Backup/Restore
- Audit logs

## Project Structure

```
accounting_web_app/
├── backend/          # FastAPI backend
├── frontend/        # React frontend
├── database/        # PostgreSQL schema
└── render.yaml      # Render deployment config
```

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Deployment

This app is configured for Render deployment. Push to GitHub and connect to Render.

## Database

Uses PostgreSQL with complete schema matching desktop app structure.
