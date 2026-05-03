from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import UserRole


# ─── Auth ────────────────────────────────────────────────────────────────────

class AuthRequest(BaseModel):
    email: str
    password: str
    user_name: Optional[str] = None
    user_role: Optional[UserRole] = None


class UserDTO(BaseModel):
    id: Optional[str] = None
    email: str
    user_name: Optional[str]
    user_role: Optional[UserRole]

    class Config:
        arbitrary_types_allowed = True


class AuthResponse(BaseModel):
    status: Optional[str] = None
    response_code: Optional[str] = None
    message: Optional[str] = None
    user: Optional[UserDTO] = None


# ─── Assessment History ──────────────────────────────────────────────────────

class AssessmentHistoryRequest(BaseModel):
    user_id: Optional[int] = None
    accuracy: Optional[float] = None
    completion_rate: Optional[float] = None
    response_time: Optional[float] = None
    satisfaction_score: Optional[float] = None
    assessment_date: Optional[datetime] = None
    assessment_type: Optional[str] = None
    notes: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: Optional[int] = 0
    size: Optional[int] = 10


class AssessmentHistoryDTO(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    accuracy: float
    completion_rate: float
    response_time: float
    satisfaction_score: float
    assessment_date: datetime
    assessment_type: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]

    class Config:
        arbitrary_types_allowed = True


class AssessmentHistoryResponse(BaseModel):
    status: Optional[str] = None
    response_code: Optional[str] = None
    message: Optional[str] = None
    assessment: Optional[AssessmentHistoryDTO] = None
    assessments: Optional[list[AssessmentHistoryDTO]] = None
