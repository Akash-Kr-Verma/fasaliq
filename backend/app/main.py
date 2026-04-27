from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.buyer import router as buyer_router
from app.api.admin import router as admin_router
from app.api.data import router as data_router


from app.api.farmer import router as farmer_router

from app.models import (
    users,
    farmer_profiles,
    crops,
    recommendations,
    market_prices,
    anomalies,
    surplus_alerts,
    buyer_interests,
    chat_sessions
)

from app.api.auth import router as auth_router
from app.api.crisp import router as crisp_router
from app.api.chat import router as chat_router
from app.api.harvest import router as harvest_router

app = FastAPI(
    title="FasalIQ API",
    description="AI-powered farming co-pilot backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("Database connected and tables ready.")

app.include_router(auth_router)
app.include_router(crisp_router)
app.include_router(farmer_router)
app.include_router(buyer_router)
app.include_router(admin_router)
app.include_router(data_router)
app.include_router(chat_router)
app.include_router(harvest_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to FasalIQ API",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}