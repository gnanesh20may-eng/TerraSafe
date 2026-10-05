import firebase_admin
from firebase_admin import credentials, messaging
from backend.app.config import DEMO_MODE, FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY, FIREBASE_PROJECT_ID


def _ensure_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": FIREBASE_PROJECT_ID,
            "client_email": FIREBASE_CLIENT_EMAIL,
            "private_key": FIREBASE_PRIVATE_KEY,
        })
        firebase_admin.initialize_app(cred)


def send_alert_notification(location: str, risk_score: int, risk_level: str, message: str):
    if DEMO_MODE:
        return {
            "status": "demo-only",
            "message": f"Demo notification queued for {location}",
            "source": "DEMO_DATA",
        }

    try:
        _ensure_firebase()
        payload = messaging.Notification(title="🚨 Landslide Risk Alert", body=f"{location}: {risk_score}/100 ({risk_level}) - {message}")
        messaging.send(messaging.Message(notification=payload, topic="landslide_alerts"))
        return {"status": "sent", "message": "Firebase notification sent"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
