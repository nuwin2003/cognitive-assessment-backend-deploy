import logging

from models import AssessmentHistory, User
from schemas import AssessmentHistoryRequest, AssessmentHistoryResponse, AssessmentHistoryDTO
from utils import Constant, RequestStatus, ResponseCodes, get_message

logger = logging.getLogger(__name__)


class AssessmentHistoryService:

    def save_assessment(self, request: AssessmentHistoryRequest) -> AssessmentHistoryResponse:
        response = AssessmentHistoryResponse()

        try:
            user = User.objects(id=request.user_id, is_deleted=Constant.DB_FALSE).first()

            if not user:
                response.status = RequestStatus.FAILURE
                response.response_code = ResponseCodes.USER_NOT_FOUND_FOR_ASSESSMENT
                response.message = get_message(ResponseCodes.USER_NOT_FOUND_FOR_ASSESSMENT)
                return response

            assessment = AssessmentHistory(
                user=user,
                accuracy=request.accuracy,
                completion_rate=request.completion_rate,
                response_time=request.response_time,
                satisfaction_score=request.satisfaction_score,
                assessment_date=request.assessment_date,
                assessment_type=request.assessment_type,
                notes=request.notes,
                is_deleted=Constant.DB_FALSE
            )
            assessment.save()

            response.assessment = AssessmentHistoryDTO(
                id=str(assessment.id),
                user_id=str(assessment.user.id),
                accuracy=assessment.accuracy,
                completion_rate=assessment.completion_rate,
                response_time=assessment.response_time,
                satisfaction_score=assessment.satisfaction_score,
                assessment_date=assessment.assessment_date,
                assessment_type=assessment.assessment_type,
                notes=assessment.notes,
                created_at=assessment.created_at
            )
            response.status = RequestStatus.SUCCESS
            response.response_code = ResponseCodes.ASSESSMENT_SAVE_SUCCESS
            response.message = get_message(ResponseCodes.ASSESSMENT_SAVE_SUCCESS)

        except Exception as e:
            logger.error("Error saving assessment: %s", str(e))
            response.status = RequestStatus.FAILURE
            response.response_code = ResponseCodes.ASSESSMENT_SAVE_FAILURE
            response.message = get_message(ResponseCodes.ASSESSMENT_SAVE_FAILURE)

        return response

    def get_assessment_history(self, request: AssessmentHistoryRequest) -> AssessmentHistoryResponse:
        response = AssessmentHistoryResponse()

        try:
            query = AssessmentHistory.objects(
                user=request.user_id,
                is_deleted=Constant.DB_FALSE
            )

            if request.from_date:
                query = query.filter(assessment_date__gte=request.from_date)
            if request.to_date:
                query = query.filter(assessment_date__lte=request.to_date)

            page = request.page or 0
            size = request.size or 10
            assessments = query.skip(page * size).limit(size).all()

            response.assessments = [
                AssessmentHistoryDTO(
                    id=str(a.id),
                    user_id=str(a.user.id),
                    accuracy=a.accuracy,
                    completion_rate=a.completion_rate,
                    response_time=a.response_time,
                    satisfaction_score=a.satisfaction_score,
                    assessment_date=a.assessment_date,
                    assessment_type=a.assessment_type,
                    notes=a.notes,
                    created_at=a.created_at
                )
                for a in assessments
            ]
            response.status = RequestStatus.SUCCESS
            response.response_code = ResponseCodes.ASSESSMENT_FETCH_SUCCESS
            response.message = get_message(ResponseCodes.ASSESSMENT_FETCH_SUCCESS)

        except Exception as e:
            logger.error("Error fetching assessments: %s", str(e))
            response.status = RequestStatus.FAILURE
            response.response_code = ResponseCodes.ASSESSMENT_FETCH_SUCCESS
            response.message = get_message(ResponseCodes.ASSESSMENT_FETCH_SUCCESS)

        return response


assessment_history_service = AssessmentHistoryService()
