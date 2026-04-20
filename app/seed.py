from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.user_groups import UserGroup, UserGroupEnum


def seed_user_groups():
    db: Session = SessionLocal()
    try:
        for group_name in UserGroupEnum:
            exists = db.query(UserGroup).filter_by(name=group_name).first()
            if not exists:
                db.add(UserGroup(name=group_name))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_user_groups()
