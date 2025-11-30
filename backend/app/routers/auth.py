from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import UserRegister, UserLogin, Token, UserProfile
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=Token, status_code=201)
async def register(user_data: UserRegister):
    """
    Register a new user
    - Creates Firebase Auth account
    - Stores profile in Firestore
    - Returns JWT token
    """
    return await auth_service.register_user(user_data)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Login existing user
    - Verifies credentials
    - Returns JWT token
    """
    return await auth_service.login_user(credentials)

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user profile
    Requires: Bearer token
    """
    return await auth_service.get_user_profile(current_user['sub'])
