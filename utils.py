import face_recognition
import cv2
import numpy as np
from models import Student, Attendance
from app import db
from datetime import datetime, timedelta

def encode_face(image_file, student_name):
    try:
        # Read the image file
        image_array = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect face locations
        face_locations = face_recognition.face_locations(rgb_image, model="hog")
        
        if len(face_locations) == 0:
            print(f"No face detected in the image for student {student_name}")
            return None
        elif len(face_locations) > 1:
            print(f"Multiple faces detected in the image for student {student_name}")
            return None
            
        # Get the face encoding for the first face found
        face_encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]
        return face_encoding.tolist()  # Convert to list for storage
        
    except Exception as e:
        print(f"Error encoding face for student {student_name}: {str(e)}")
        return None

def recognize_faces(frame):
    try:
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize frame for faster face recognition
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        
        # Detect faces in the frame
        face_locations = face_recognition.face_locations(small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        
        recognized_students = []
        
        # Get all students from database
        students = Student.query.all()
        if not students:
            return []
            
        known_face_encodings = [np.array(student.face_encoding) for student in students if student.face_encoding]
        
        # If no known faces, return empty list
        if not known_face_encodings:
            return []
        
        # For each face detected in the frame
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            if not any(matches):
                continue
                
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                student = students[best_match_index]
                student.face_location = face_location  # Store face location for drawing
                recognized_students.append(student)
        
        return recognized_students
        
    except Exception as e:
        print(f"Error in face recognition: {str(e)}")
        return []

def markAttendance(name):
    try:
        student = Student.query.filter_by(name=name).first()
        if not student:
            print(f"No student found with name: {name}")
            return False
            
        # Check if attendance already marked within last hour
        last_hour = datetime.utcnow() - timedelta(hours=1)
        existing_attendance = Attendance.query.filter_by(
            student_id=student.id
        ).filter(
            Attendance.timestamp > last_hour
        ).first()
        
        if existing_attendance:
            return False  # Already marked within last hour
            
        # Mark new attendance
        new_attendance = Attendance(student_id=student.id)
        db.session.add(new_attendance)
        db.session.commit()
        print(f"Attendance marked for {name} at {new_attendance.timestamp}")
        return True
        
    except Exception as e:
        print(f"Error marking attendance for {name}: {str(e)}")
        return False
