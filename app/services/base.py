from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session


class BaseCRUDService:
    model = None
    unique_field = None

    @classmethod
    def get_all(cls, db: Session):
        return db.execute(select(cls.model)).scalars().all()

    @classmethod
    def get_by_id(cls, db: Session, obj_id: int):
        return db.get(cls.model, obj_id)

    @classmethod
    def get_or_404(cls, db, obj_id: int):
        obj = cls.get_by_id(db, obj_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{cls.model.__name__} with id {obj_id} not found",
            )
        return obj

    @classmethod
    def create(cls, db: Session, **data):
        if cls.unique_field:
            field_value = data.get(cls.unique_field)
            existing = db.execute(
                select(cls.model).where(
                    getattr(cls.model, cls.unique_field) == field_value
                )
            ).scalar_one_or_none()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{cls.model.__name__} with this {cls.unique_field} already exists",
                )

        obj = cls.model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def update(cls, db: Session, obj, **data):
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)

        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def delete(cls, db: Session, obj):
        db.delete(obj)
        db.commit()
