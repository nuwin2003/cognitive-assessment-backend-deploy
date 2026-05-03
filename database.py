import os
from mongoengine import connect, disconnect

# MongoDB Connection - Use environment variable or default to localhost
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "dyslexia_app")

def connect_db():
    """Connect to MongoDB"""
    connect(db=DATABASE_NAME, host=MONGODB_URI)

def disconnect_db():
    """Disconnect from MongoDB"""
    disconnect()

def get_db():
    """Dependency for FastAPI to ensure DB connection"""
    try:
        connect_db()
        yield
    finally:
        pass
