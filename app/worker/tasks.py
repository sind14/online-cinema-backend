from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.activation_tokens import ActivationToken
from app.worker.celery_app import celery_app

@celery_app.task
def delete_expired_tokens():
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        expired_tokens = db.query(ActivationToken).filter(ActivationToken.expires_at < now).all()
        for token in expired_tokens:
            db.delete(token)
        db.commit()
        print(f"Deleted {len(expired_tokens)} expired activation tokens")
    finally:
        db.close()
