from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta
from sqlalchemy import func
import json

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, face_encoding=json.dumps(user.face_encoding))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_face_encodings(db: Session):
    users = db.query(models.User).all()
    return [(user.id, json.loads(user.face_encoding)) for user in users]

def create_face_log(db: Session, face_log: schemas.FaceLogCreate):
    db_face_log = models.FaceLog(**face_log.dict())
    db.add(db_face_log)
    db.commit()
    db.refresh(db_face_log)
    return db_face_log

def get_face_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.FaceLog).order_by(models.FaceLog.timestamp.desc()).offset(skip).limit(limit).all()

def get_daily_detection_counts(db: Session, days: int = 7):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    counts = db.query(
        func.date(models.FaceLog.timestamp).label('date'),
        func.count(models.FaceLog.id).label('count')
    ).filter(
        models.FaceLog.timestamp.between(start_date, end_date)
    ).group_by(
        func.date(models.FaceLog.timestamp)
    ).all()
    
    return {str(date): count for date, count in counts}