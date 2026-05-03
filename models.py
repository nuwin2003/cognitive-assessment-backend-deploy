import enum
from datetime import datetime
from mongoengine import Document, StringField, FloatField, DateTimeField, BooleanField, ReferenceField, EnumField


class UserRole(str, enum.Enum):
    THERAPIST = "THERAPIST"
    ADMIN = "ADMIN"
    CHILD = "CHILD"


class User(Document):
    email = StringField(unique=True, required=True)
    password = StringField(required=True)
    user_name = StringField()
    user_role = EnumField(UserRole)
    is_deleted = StringField(default="N")
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'user',
        'indexes': ['email', 'is_deleted']
    }


class AssessmentHistory(Document):
    user = ReferenceField(User, required=True)
    accuracy = FloatField(required=True)
    completion_rate = FloatField(required=True)
    response_time = FloatField(required=True)
    satisfaction_score = FloatField(required=True)
    assessment_date = DateTimeField(required=True)
    assessment_type = StringField()
    notes = StringField(max_length=1000)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    is_deleted = StringField(default="N")
    
    meta = {
        'collection': 'assessment_history',
        'indexes': ['user', 'is_deleted', 'assessment_date']
    }


class Otp(Document):
    email = StringField(required=True)
    otp = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    
    meta = {
        'collection': 'otp',
        'indexes': ['email']
    }
