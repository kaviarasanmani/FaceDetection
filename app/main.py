from fastapi import FastAPI, Request, Depends, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
from app.face_detection import detect_faces, encode_face, recognize_face
import cv2
import numpy as np
from typing import List

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(request: Request, name: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    faces = detect_faces(img)
    if len(faces) != 1:
        raise HTTPException(status_code=400, detail="Image must contain exactly one face")
    
    face_encoding = encode_face(img, faces[0])
    user = crud.create_user(db, schemas.UserCreate(name=name, face_encoding=face_encoding.tolist()))
    
    return templates.TemplateResponse("register_success.html", {"request": request, "user": user})

@app.get("/detect")
async def detect_page(request: Request):
    return templates.TemplateResponse("detect.html", {"request": request})

@app.post("/detect")
async def detect_faces_endpoint(image: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    faces = detect_faces(img)
    known_faces = crud.get_all_face_encodings(db)
    
    results = []
    for face in faces:
        face_encoding = encode_face(img, face)
        user_id = recognize_face(face_encoding, known_faces)
        if user_id:
            user = crud.get_user(db, user_id)
            crud.create_face_log(db, schemas.FaceLogCreate(user_id=user_id, event_type="detected"))
            results.append({"name": user.name, "confidence": "High"})
        else:
            results.append({"name": "Unknown", "confidence": "Low"})
    
    return {"results": results}

@app.get("/logs")
async def logs(request: Request, db: Session = Depends(get_db)):
    logs = crud.get_face_logs(db)
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs})

@app.get("/analytics")
async def analytics(request: Request, db: Session = Depends(get_db)):
    daily_counts = crud.get_daily_detection_counts(db)
    return templates.TemplateResponse("analytics.html", {"request": request, "daily_counts": daily_counts})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)