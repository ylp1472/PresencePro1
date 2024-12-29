import face_recognition
import cv2
import numpy as np
from models import Student

def encode_face(image_file):
    image = face_recognition.load_image_file(image_file)
    face_locations = face_recognition.face_locations(image)
    if len(face_locations) > 0:
        face_encoding = face_recognition.face_encodings(image, face_locations)[0]
        return face_encoding
    return None

def recognize_faces(image):
    # Convert the image to RGB (required by face_recognition)
    rgb_small_frame = image[:, :, ::-1]  # Convert BGR to RGB
    
    # Detect faces in the image
    face_locations = face_recognition.face_locations(rgb_small_frame)
    
    # Ensure face_locations is not empty
    if len(face_locations) > 0:
        # Get face encodings for each detected face
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        return face_encodings
    else:
        print("erorr recognize_faces")
        return []
