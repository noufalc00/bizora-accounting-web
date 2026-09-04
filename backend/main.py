"""
Bizora Accounting Web Application - Main FastAPI Backend
Standalone web application with full feature parity to desktop app
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.database import init_db
from api import (
    auth,
    companies,
    accounts,
    parties,
    products,
    sales,
    purchases,
    vouchers,
    reports,
    stock,
    settings,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield


app = FastAPI(
    title="Bizora Accounting Web API",
    description="Complete accounting system - web version of desktop app",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(parties.router, prefix="/api/parties", tags=["Parties"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["Purchases"])
app.include_router(vouchers.router, prefix="/api/vouchers", tags=["Vouchers"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(stock.router, prefix="/api/stock", tags=["Stock"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])


@app.get("/")
async def root():
    return {
        "message": "Bizora Accounting Web API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
