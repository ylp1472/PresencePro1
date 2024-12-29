from flask import render_template, url_for, flash, redirect, request, jsonify, make_response
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db, bcrypt
from models import Admin, Student, Attendance
from utils import encode_face, recognize_faces
import cv2
import numpy as np
from datetime import datetime
import csv
from io import StringIO

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and bcrypt.check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now().date()
    attendances = Attendance.query.filter(db.func.date(Attendance.timestamp) == today).all()
    return render_template('dashboard.html', attendances=attendances)

@app.route('/mark_attendance')
@login_required
def mark_attendance():
    return render_template('mark_attendance.html')

@app.route('/process_attendance', methods=['POST'])
@login_required
def process_attendance():
    if 'image' not in request.files:
        return 'No image file', 400
    
    file = request.files['image']
    npimg = np.fromfile(file, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    recognized_students = recognize_faces(img)
    
    for student in recognized_students:
        attendance = Attendance(student_id=student.id)
        db.session.add(attendance)
    
    db.session.commit()
    
    return jsonify([student.name for student in recognized_students])

@app.route('/student_management')
@login_required
def student_management():
    students = Student.query.all()
    return render_template('student_management.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        registration_number = request.form['registration_number']
        image = request.files['image']
        
        if image:
            face_encoding = encode_face(image)
            if face_encoding is not None:
                student = Student(name=name, registration_number=registration_number, face_encoding=face_encoding)
                db.session.add(student)
                db.session.commit()
                flash('Student added successfully!', 'success')
                return redirect(url_for('student_management'))
            else:
                flash('No face detected in the image. Please try again.', 'danger')
        else:
            flash('Please upload an image.', 'danger')
    
    return render_template('add_student.html')

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.registration_number = request.form['registration_number']
        image = request.files['image']
        
        if image:
            face_encoding = encode_face(image)
            if face_encoding is not None:
                student.face_encoding = face_encoding
            else:
                flash('No face detected in the image. Previous image retained.', 'warning')
        
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('student_management'))
    
    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('student_management'))

@app.route('/export_attendance', methods=['POST'])
@login_required
def export_attendance():
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
    
    attendances = Attendance.query.filter(Attendance.timestamp.between(start_date, end_date)).all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student Name', 'Registration Number', 'Timestamp'])
    
    for attendance in attendances:
        cw.writerow([attendance.student.name, attendance.student.registration_number, attendance.timestamp])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=attendance_{start_date.date()}_to_{end_date.date()}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

from flask import Response
import cv2
from app import app

# Initialize the video capture object (use 0 for the default webcam)
video_capture = cv2.VideoCapture(1)

def gen():
    """Generate frame by frame for video feed."""
    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # Convert frame to JPEG and encode it to send as a response
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        
        # Yield the frame as a byte string in the format for MJPEG
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Route to stream video feed."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

import base64
from io import BytesIO
from flask import request, jsonify
import face_recognition
import numpy as np
import cv2

@app.route('/process_attendance', methods=['POST'])
@login_required
def process_attendance():
    # Get base64 image data from request
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'status': 'error', 'message': 'No image data provided.'}), 400

    # Decode the base64 image data
    image_data = image_data.split(',')[1]  # Remove the base64 header
    img_bytes = base64.b64decode(image_data)

    # Convert byte data to numpy array
    npimg = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Detect faces and recognize them
    recognized_students = recognize_faces(img)

    # Mark attendance for each recognized student
    for student in recognized_students:
        attendance = Attendance(student_id=student.id)
        db.session.add(attendance)

    db.session.commit()

    # Return list of recognized student names
    recognized_names = [student.name for student in recognized_students]
    return jsonify({'status': 'success', 'names': recognized_names})

import face_recognition
from models import Student

def recognize_faces(img):
    # Convert the image to RGB (OpenCV uses BGR by default)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect faces and face encodings in the image
    face_locations = face_recognition.face_locations(rgb_img)
    face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

    recognized_students = []

    # Loop through each face found in the image
    for face_encoding in face_encodings:
        # Compare the face encoding with the stored face encodings in the database
        students = Student.query.all()  # You can optimize this by only querying the necessary records
        for student in students:
            # Compare the captured face encoding with the stored encoding
            match = face_recognition.compare_faces([student.face_encoding], face_encoding)
            if match[0]:
                recognized_students.append(student)
                break  # Stop once a match is found for this face

    return recognized_students
import face_recognition
from models import Student

def recognize_faces(img):
    # Convert the image to RGB (OpenCV uses BGR by default)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect faces and face encodings in the image
    face_locations = face_recognition.face_locations(rgb_img)
    face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

    recognized_students = []

    # Loop through each face found in the image
    for face_encoding in face_encodings:
        # Compare the face encoding with the stored face encodings in the database
        students = Student.query.all()  # You can optimize this by only querying the necessary records
        for student in students:
            # Compare the captured face encoding with the stored encoding
            match = face_recognition.compare_faces([student.face_encoding], face_encoding)
            if match[0]:
                recognized_students.append(student)
                break  # Stop once a match is found for this face

    return recognized_students


