import logging
from passlib.context import CryptContext

from models import User
from schemas import AuthRequest, AuthResponse, UserDTO
from utils import Constant, RequestStatus, ResponseCodes, get_message

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    def login(self, auth_request: AuthRequest) -> AuthResponse:
        logger.info("Log In Starts")

        auth_response = AuthResponse()
        try:
            user = User.objects(email=auth_request.email, is_deleted=Constant.DB_FALSE).first()

            if not user:
                logger.error("User not found with email: %s", auth_request.email)
                auth_response.status = RequestStatus.FAILURE
                auth_response.response_code = ResponseCodes.USER_NOT_FOUND
                auth_response.message = get_message(ResponseCodes.USER_NOT_FOUND)
                return auth_response

            if not pwd_context.verify(auth_request.password, user.password):
                logger.error("Password mismatch for user: %s", auth_request.email)
                auth_response.status = RequestStatus.FAILURE
                auth_response.response_code = ResponseCodes.PASSWORD_MISMATCH
                auth_response.message = get_message(ResponseCodes.PASSWORD_MISMATCH)
                return auth_response

            logger.info("Log In Success")
            auth_response.user = UserDTO(
                id=str(user.id),
                email=user.email,
                user_name=user.user_name,
                user_role=user.user_role
            )
            auth_response.status = RequestStatus.SUCCESS
            auth_response.response_code = ResponseCodes.SUCCESS
            auth_response.message = get_message(ResponseCodes.USER_SIGN_IN_SUCCESS)

        except Exception as e:
            logger.error("Error during login: %s", str(e))
            auth_response.status = RequestStatus.FAILURE
            auth_response.response_code = ResponseCodes.USER_NOT_FOUND
            auth_response.message = get_message(ResponseCodes.USER_NOT_FOUND)

        logger.info("Log In Ends")
        return auth_response

    def sign_up(self, auth_request: AuthRequest) -> AuthResponse:
        logger.info("Sign Up Starts")

        auth_response = AuthResponse()
        try:
            existing_user = User.objects(email=auth_request.email, is_deleted=Constant.DB_FALSE).first()

            if existing_user:
                logger.error("Email already taken: %s", auth_request.email)
                auth_response.status = RequestStatus.FAILURE
                auth_response.response_code = ResponseCodes.EMAIL_ALREADY_TAKEN
                auth_response.message = get_message(ResponseCodes.EMAIL_ALREADY_TAKEN)
                return auth_response

            user = User(
                email=auth_request.email,
                password=pwd_context.hash(auth_request.password),
                user_name=auth_request.user_name,
                user_role=auth_request.user_role,
                is_deleted=Constant.DB_FALSE
            )
            user.save()

            logger.info("Sign Up Success")
            auth_response.user = UserDTO(
                id=str(user.id),
                email=user.email,
                user_name=user.user_name,
                user_role=user.user_role
            )
            auth_response.status = RequestStatus.SUCCESS
            auth_response.response_code = ResponseCodes.SUCCESS
            auth_response.message = get_message(ResponseCodes.USER_SIGNUP_SUCCESS)

        except Exception as e:
            logger.error("Error during signup: %s", str(e))
            auth_response.status = RequestStatus.FAILURE
            auth_response.response_code = ResponseCodes.USER_SIGNUP_FAILURE
            auth_response.message = get_message(ResponseCodes.USER_SIGNUP_FAILURE)

        logger.info("Sign Up Ends")
        return auth_response


auth_service = AuthService()
