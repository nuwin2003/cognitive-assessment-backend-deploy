from fastapi import APIRouter

from schemas import AuthRequest, AuthResponse
from services.auth_service import auth_service

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(auth_request: AuthRequest):
    return auth_service.login(auth_request)


@router.post("/signup", response_model=AuthResponse)
def sign_up(auth_request: AuthRequest):
    return auth_service.sign_up(auth_request)
