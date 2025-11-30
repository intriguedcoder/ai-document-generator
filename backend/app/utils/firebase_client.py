import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings
import logging
import os
import json

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
            creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

            if creds_json:
                # Production: Load from env variable (Render deployment)
                cred = credentials.Certificate(json.loads(creds_json))
            else:
                # Local: Read from file path (from .env)
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
