from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Apple Store Review Insights API",
    description="Collects app-store reviews and generates metrics & insights",
    version="1.0.0",
)

app.include_router(router)