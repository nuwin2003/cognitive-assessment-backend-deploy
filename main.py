from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, assessment_history_router
from movement_predict_api import router as predict_router
from database import connect_db, disconnect_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db():
    """Initialize MongoDB connection on startup"""
    connect_db()
    print("MongoDB connected successfully")

@app.on_event("shutdown")
def shutdown_db():
    """Disconnect MongoDB on shutdown"""
    disconnect_db()
    print("MongoDB disconnected")

app.include_router(auth_router.router, prefix="/auth")
app.include_router(assessment_history_router.router, prefix="/assessment-history")
app.include_router(predict_router)
