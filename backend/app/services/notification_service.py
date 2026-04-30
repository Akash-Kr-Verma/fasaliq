import firebase_admin
from firebase_admin import credentials, messaging
import os
import logging

logger = logging.getLogger(__name__)

def initialize_firebase():
    try:
        if not firebase_admin._apps:
            # Check if the service account key file exists
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_service_account.json")
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully.")
            else:
                logger.warning(f"Firebase credentials not found at {cred_path}. Push notifications will be disabled.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

def send_push_notification(fcm_token: str, title: str, body: str, data: dict = None):
    """
    Sends a push notification to a specific FCM token.
    """
    if not firebase_admin._apps:
        logger.warning("Firebase not initialized. Cannot send notification.")
        return False
        
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data if data else {},
            token=fcm_token,
        )
        response = messaging.send(message)
        logger.info(f"Successfully sent message: {response}")
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False
