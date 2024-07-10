
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    face_encoding: List[float]

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class FaceLogBase(BaseModel):
    user_id: int
    event_type: str

class FaceLogCreate(FaceLogBase):
    pass

class FaceLog(FaceLogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True