# MySQL to MongoDB Migration Guide

## Overview
This project has been successfully converted from MySQL with SQLAlchemy ORM to MongoDB with MongoEngine ODM.

## Changes Made

### 1. **database.py**
- Replaced SQLAlchemy engine with MongoEngine connection
- Changed from `create_engine()` and `sessionmaker` to `connect()`
- Updated MongoDB connection string format
- Removed session management (MongoDB handles this automatically)

### 2. **models.py**
- Converted SQLAlchemy models to MongoEngine Document classes
- Replaced `Column` definitions with MongoEngine field types:
  - `Column(String)` → `StringField()`
  - `Column(Double)` → `FloatField()`
  - `Column(DateTime)` → `DateTimeField()`
  - `Column(BigInteger)` → Auto-generated ObjectId
  - `Column(Enum)` → `EnumField()`
- Changed from relationships to `ReferenceField()` for foreign keys
- Added automatic indexes via `meta` class

### 3. **services/auth_service.py**
- Removed `Session` parameter from methods
- Changed queries from `db.query(User).filter()` to `User.objects().filter()`
- Replaced `db.add()` and `db.commit()` with `.save()`
- Used `first()` instead of SQLAlchemy's `.first()`
- User IDs now returned as strings (ObjectId converted to str)

### 4. **services/assessment_history_service.py**
- Removed `Session` dependency
- Updated query syntax to MongoEngine QuerySet methods
- Used `skip()` and `limit()` instead of `offset()` and `limit()`
- MongoEngine query operators like `assessment_date__gte` instead of `>=`

### 5. **otp_service.py**
- Removed database session parameter
- Updated OTP queries to MongoEngine syntax
- `.delete()` method instead of `db.delete()`
- Methods now return boolean values for better error handling

### 6. **Routers** (auth_router.py, assessment_history_router.py)
- Removed `Depends(get_db)` dependencies
- Simplified endpoint signatures - no Session parameter needed
- Services are now called directly without database session

### 7. **schemas.py**
- Updated UserDTO and AssessmentHistoryDTO to use `arbitrary_types_allowed = True`
- Changed id field type from `int` to `Optional[str]` (MongoDB ObjectId)
- Removed `from_attributes` in favor of `arbitrary_types_allowed`

### 8. **requirements.txt**
- Removed: `sqlalchemy`, `pymysql`
- Added: `mongoengine`, `pymongo`

## Setup Instructions

### Prerequisites
- Python 3.7+
- MongoDB server running (locally or remote)

### 1. Install MongoDB
**Local Installation:**
- **Windows:** Download from https://www.mongodb.com/try/download/community
- **Mac:** `brew install mongodb-community`
- **Linux:** Follow the official MongoDB installation guide

**Or use MongoDB Atlas (Cloud):**
1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free tier cluster
3. Get your connection string

### 2. Update Connection String
Edit `database.py` and update the MongoDB URI:

```python
# For local MongoDB
MONGODB_URI = "mongodb://localhost:27017"

# For MongoDB Atlas (replace with your credentials)
MONGODB_URI = "mongodb+srv://<username>:<password>@<cluster>.<region>.mongodb.net/?retryWrites=true&w=majority"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Update Main Application
If you have a main.py that initializes the app, add MongoDB connection:

```python
from database import connect_db, disconnect_db
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
def startup_db():
    connect_db()

@app.on_event("shutdown")
def shutdown_db():
    disconnect_db()
```

## Key Differences: SQL vs MongoDB Queries

### User Login Query
**SQL (Before):**
```python
user = db.query(User).filter(
    User.email == email,
    User.is_deleted == "N"
).first()
```

**MongoDB (After):**
```python
user = User.objects(email=email, is_deleted="N").first()
```

### Assessment History Query
**SQL (Before):**
```python
query = db.query(AssessmentHistory).filter(
    AssessmentHistory.user_id == user_id,
    AssessmentHistory.assessment_date >= from_date
).offset(page * size).limit(size).all()
```

**MongoDB (After):**
```python
query = AssessmentHistory.objects(
    user=user_id,
    assessment_date__gte=from_date
).skip(page * size).limit(size).all()
```

## MongoEngine Query Operators
- `__eq` or `=` : Equal to
- `__ne` : Not equal to
- `__gt` : Greater than
- `__gte` : Greater than or equal to
- `__lt` : Less than
- `__lte` : Less than or equal to
- `__in` : In array
- `__nin` : Not in array
- `__exists` : Field exists

## Data Migration (If you have existing MySQL data)

To migrate existing data from MySQL to MongoDB:

1. Export MySQL data as JSON
2. Use MongoDB import tools or write a migration script
3. Update any foreign key references to use ObjectId references

Example migration script:
```python
import pymongo
from pymongo import MongoClient
import json

client = MongoClient("mongodb://localhost:27017")
db = client["dyslexia_app"]

# Import collections
# db.user.insert_many(json_data)
```

## Testing Endpoints

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Sign Up
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"password123","user_name":"John","user_role":"CHILD"}'
```

### Save Assessment
```bash
curl -X POST "http://localhost:8000/assessment/save" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"<user_id>","accuracy":0.95,"completion_rate":0.9,"response_time":2.5,"satisfaction_score":8.5,"assessment_date":"2024-01-01T10:00:00","assessment_type":"GESTURE"}'
```

## Troubleshooting

### Connection Error
```
pymongo.errors.ServerSelectionTimeoutError
```
**Solution:** Ensure MongoDB is running and connection string is correct

### Import Error
```
ModuleNotFoundError: No module named 'mongoengine'
```
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Field Type Error
**Solution:** Ensure field types in requests match the schema definitions

## Performance Considerations

1. **Indexing:** Indexes are automatically created on fields marked in `meta`
2. **Query Optimization:** Use `.select_related()` and `.only()` for performance
3. **Pagination:** Always use `skip()` and `limit()` for large datasets
4. **Connection Pooling:** MongoEngine handles connection pooling automatically

## Next Steps

1. Test all endpoints thoroughly
2. Create integration tests for MongoDB operations
3. Set up monitoring and logging
4. Consider implementing data validation at the application level

## Additional Resources

- MongoEngine Documentation: http://docs.mongoengine.org/
- MongoDB Documentation: https://docs.mongodb.com/
- FastAPI with MongoDB: https://fastapi.tiangolo.com/
