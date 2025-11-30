import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FirebaseClient:
    """Singleton Firebase client"""
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
            cls._initialize_firebase()
        return cls._instance
    
    @classmethod
    def _initialize_firebase(cls):
        """Initialize Firebase Admin SDK"""
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            cls._db = firestore.client()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
            raise
    
    @property
    def db(self):
        return self._db

# Global Firebase client instance
firebase_client = FirebaseClient()
db = firebase_client.db
