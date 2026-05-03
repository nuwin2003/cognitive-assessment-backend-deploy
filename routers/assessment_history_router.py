from fastapi import APIRouter

from schemas import AssessmentHistoryRequest, AssessmentHistoryResponse
from services.assessment_history_service import assessment_history_service

router = APIRouter()


@router.post("/save", response_model=AssessmentHistoryResponse)
def save_assessment(request: AssessmentHistoryRequest):
    return assessment_history_service.save_assessment(request)


@router.post("/list", response_model=AssessmentHistoryResponse)
def fetch_assessment_history(request: AssessmentHistoryRequest):
    return assessment_history_service.get_assessment_history(request)
