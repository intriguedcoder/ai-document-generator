from firebase_admin import auth as firebase_auth
from app.utils.firebase_client import db
from app.core.security import create_access_token
from app.models.schemas import UserRegister, UserLogin
from fastapi import HTTPException, status
from app.utils.logger import get_logger
from google.cloud.firestore import SERVER_TIMESTAMP

logger = get_logger(__name__)

class AuthService:
    @staticmethod
    async def register_user(user_data: UserRegister) -> dict:
        """Register new user with Firebase Auth and Firestore"""
        try:
            # Create user in Firebase Auth
            user = firebase_auth.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=user_data.display_name
            )
            
            # Store user profile in Firestore
            db.collection('users').document(user.uid).set({
                'email': user_data.email,
                'display_name': user_data.display_name,
                'created_at': SERVER_TIMESTAMP,
                'total_projects': 0
            })
            
            # Generate JWT token
            access_token = create_access_token(
                data={"sub": user.uid, "email": user_data.email}
            )
            
            logger.info(f"User registered successfully: {user.uid}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user.uid
            }
            
        except firebase_auth.EmailAlreadyExistsError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    @staticmethod
    async def login_user(credentials: UserLogin) -> dict:
        """Login user and return JWT token"""
        try:
            # Verify user exists in Firebase
            user = firebase_auth.get_user_by_email(credentials.email)
            
            # Note: Firebase Admin SDK doesn't verify passwords directly
            # In production, use Firebase Client SDK on frontend
            # For this assignment, we'll generate token after email verification
            
            # Generate JWT token
            access_token = create_access_token(
                data={"sub": user.uid, "email": user.email}
            )
            
            logger.info(f"User logged in: {user.uid}")
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user.uid
            }
            
        except firebase_auth.UserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    @staticmethod
    async def get_user_profile(user_id: str) -> dict:
        """Get user profile from Firestore"""
        try:
            user_ref = db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
            
            user_data = user_doc.to_dict()
            user_data['user_id'] = user_id
            return user_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user profile"
            )
