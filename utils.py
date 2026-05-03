class Constant:
    DB_FALSE = "N"
    DB_TRUE = "Y"


class RequestStatus:
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class ResponseCodes:
    SUCCESS = "200"
    USER_NOT_FOUND = "1001"
    PASSWORD_MISMATCH = "1002"
    EMAIL_ALREADY_TAKEN = "1003"
    USER_SIGNUP_SUCCESS = "1004"
    USER_SIGNUP_FAILURE = "1005"
    USER_SIGN_IN_SUCCESS = "1006"
    ASSESSMENT_SAVE_SUCCESS = "2001"
    ASSESSMENT_SAVE_FAILURE = "2002"
    ASSESSMENT_FETCH_SUCCESS = "2003"
    USER_NOT_FOUND_FOR_ASSESSMENT = "2004"


MESSAGES = {
    ResponseCodes.USER_NOT_FOUND: "User not found.",
    ResponseCodes.PASSWORD_MISMATCH: "Incorrect password.",
    ResponseCodes.EMAIL_ALREADY_TAKEN: "Email is already registered.",
    ResponseCodes.USER_SIGNUP_SUCCESS: "User signed up successfully.",
    ResponseCodes.USER_SIGNUP_FAILURE: "Sign up failed. Please try again.",
    ResponseCodes.USER_SIGN_IN_SUCCESS: "User logged in successfully.",
    ResponseCodes.ASSESSMENT_SAVE_SUCCESS: "Assessment saved successfully.",
    ResponseCodes.ASSESSMENT_SAVE_FAILURE: "Failed to save assessment.",
    ResponseCodes.ASSESSMENT_FETCH_SUCCESS: "Assessment history fetched successfully.",
    ResponseCodes.USER_NOT_FOUND_FOR_ASSESSMENT: "User not found for assessment.",
}


def get_message(code: str) -> str:
    return MESSAGES.get(code, "Unknown response code.")
