import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces

def encode_face(image, face):
    x, y, w, h = face
    face_img = image[y:y+h, x:x+w]
    face_img = cv2.resize(face_img, (100, 100))
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    return face_img.flatten()

def recognize_face(face_encoding, known_faces, threshold=5000):
    if not known_faces:
        return None
    
    distances = [np.linalg.norm(face_encoding - np.array(known_face[1])) for known_face in known_faces]
    min_distance_index = np.argmin(distances)
    
    if distances[min_distance_index] < threshold:
        return known_faces[min_distance_index][0]  # Return the user_id
    return None