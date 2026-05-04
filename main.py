from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, assessment_history_router
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

# Try to include the movement prediction router - it's optional
try:
    from movement_predict_api import router as predict_router
    app.include_router(predict_router)
    print("Movement prediction API loaded successfully")
except ImportError as e:
    print(f"Warning: Movement prediction API could not be loaded: {e}")
    print("Main backend will continue to run without /predict endpoint")
