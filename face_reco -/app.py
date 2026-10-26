from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime
from sqlalchemy import func
from models import db, Student, Attendance, Result

# OpenCV + NumPy
import cv2
import numpy as np


# =====================================================
# FLASK INITIALIZATION
# =====================================================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facereco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Student photo upload folder
UPLOAD_FOLDER = "static/uploads/students"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# HOME → DASHBOARD
# =====================================================
@app.route('/')
def home():
    return redirect(url_for('dashboard'))


# =====================================================
# DASHBOARD ROUTE
# =====================================================
@app.route('/dashboard')
def dashboard():

    total_students = Student.query.count()
    active_students = total_students

    today = datetime.now().date()
    present_today = (
        Attendance.query
        .filter(func.date(Attendance.timestamp) == today)
        .count()
    )

    attendance_rate = 0
    if total_students > 0:
        attendance_rate = round((present_today / total_students) * 100, 2)

    recent_logs_raw = (
        db.session.query(Attendance, Student)
        .join(Student, Attendance.student_id == Student.student_id)
        .order_by(Attendance.timestamp.desc())
        .limit(10)
        .all()
    )

    recent_logs = []
    for att, stu in recent_logs_raw:
        recent_logs.append({
            "student_id": stu.student_id,
            "student_name": stu.name,
            "timestamp": att.timestamp.strftime("%Y-%m-%d %H:%M")
        })

    return render_template(
        "dashboard.html",
        active="dashboard",
        total=total_students,
        active_students=active_students,
        present=present_today,
        attendance_rate=attendance_rate,
        recent_logs=recent_logs
    )


# =====================================================
# STUDENTS — LIST
# =====================================================
@app.route('/students')
def students():
    all_students = Student.query.all()
    return render_template('students.html', students=all_students, active='students')


# =====================================================
# ADD STUDENT
# =====================================================
@app.route('/students/add', methods=['POST'])
def add_student():
    student_id = request.form['student_id']
    name = request.form['full_name']
    email = request.form.get('email')
    phone = request.form.get('phone')
    class_name = request.form.get('class_name')

    file = request.files.get('photo')
    filename = None

    if file and file.filename != "":
        filename = f"{student_id}_{file.filename}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    new_student = Student(
        student_id=student_id,
        name=name,
        email=email,
        phone=phone,
        class_name=class_name,
        student_photo=filename
    )

    db.session.add(new_student)
    db.session.commit()

    return redirect(url_for('students'))


# =====================================================
# EDIT STUDENT
# =====================================================
@app.route('/students/edit/<student_id>', methods=['POST'])
def edit_student(student_id):
    student = Student.query.get(student_id)

    student.name = request.form['full_name']
    student.email = request.form.get('email')
    student.phone = request.form.get('phone')
    student.class_name = request.form.get('class_name')

    file = request.files.get('photo')
    if file and file.filename != "":

        if student.student_photo:
            old = os.path.join(UPLOAD_FOLDER, student.student_photo)
            if os.path.exists(old):
                os.remove(old)

        filename = f"{student_id}_{file.filename}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        student.student_photo = filename

    db.session.commit()
    return redirect(url_for('students'))


# =====================================================
# DELETE STUDENT
# =====================================================
@app.route('/students/delete/<student_id>')
def delete_student(student_id):
    student = Student.query.get(student_id)

    if student.student_photo:
        path = os.path.join(UPLOAD_FOLDER, student.student_photo)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))


# =====================================================
# ATTENDANCE PAGE
# =====================================================
@app.route('/attendance')
def attendance():
    students = Student.query.all()
    today = datetime.now().date()

    present_today = {
        a.student_id for a in Attendance.query.filter(
            func.date(Attendance.timestamp) == today
        ).all()
    }

    return render_template(
        'attendance.html',
        students=students,
        present_today=present_today,
        active='attendance'
    )


# =====================================================
# MANUAL ATTENDANCE MARK
# =====================================================
@app.route('/attendance/mark/<student_id>', methods=['POST'])
def mark_attendance(student_id):
    today = datetime.now().date()

    exists = Attendance.query.filter(
        Attendance.student_id == student_id,
        func.date(Attendance.timestamp) == today
    ).first()

    if not exists:
        new_entry = Attendance(student_id=student_id)
        db.session.add(new_entry)
        db.session.commit()

    return "OK", 200


# =====================================================
# FACE RECOGNITION API
# =====================================================
@app.route('/api/recognize', methods=['POST'])
def api_recognize():
    if 'image' not in request.files:
        return {"status": "error", "message": "no image"}, 400

    file = request.files['image']
    img_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

    if frame is None:
        return {"status": "error", "message": "invalid image"}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    if len(faces) == 0:
        return {"status": "no_face"}

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("face_model.yml")

    label_map = np.load("label_map.npy", allow_pickle=True).item()

    for (x, y, w, h) in faces:
        roi = gray[y:y+h, x:x+w]
        label, confidence = recognizer.predict(roi)

        student_id = None
        for sid, lbl in label_map.items():
            if lbl == label:
                student_id = sid
                break

        if student_id is None:
            return {"status": "unknown"}

        # Mark attendance
        today = datetime.now().date()
        exists = Attendance.query.filter(
            Attendance.student_id == student_id,
            func.date(Attendance.timestamp) == today
        ).first()

        if not exists:
            new_entry = Attendance(student_id=student_id)
            db.session.add(new_entry)
            db.session.commit()

        return {
            "status": "success",
            "student_id": student_id,
            "confidence": float(confidence)
        }

    return {"status": "error"}


# =====================================================
# RESULTS PAGE
# =====================================================
@app.route('/results')
def results():
    all_results = Result.query.join(Student).add_columns(
        Result.id,
        Result.subject,
        Result.marks,
        Result.grade,
        Result.date,
        Student.student_id,
        Student.name,
        Student.class_name
    ).all()

    students = Student.query.all()

    return render_template(
        'results.html',
        results=all_results,
        students=students,
        active='results'
    )


# =====================================================
# ADD RESULT
# =====================================================
@app.route('/results/add', methods=['POST'])
def add_result():
    result = Result(
        student_id=request.form["student_id"],
        subject=request.form["subject"],
        marks=int(request.form["marks"]),
        grade=request.form["grade"],
        date=request.form["date"]
    )
    db.session.add(result)
    db.session.commit()
    return redirect(url_for('results'))


# =====================================================
# DELETE RESULT
# =====================================================
@app.route('/results/delete/<int:id>')
def delete_result(id):
    result = Result.query.get(id)
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('results'))


# =====================================================
# REPORTS PAGE
# =====================================================
@app.route('/reports')
def reports():

    # Monthly chart
    monthly_raw = (
        db.session.query(
            func.strftime("%m", Attendance.timestamp),
            func.count(Attendance.id)
        )
        .group_by(func.strftime("%m", Attendance.timestamp))
        .all()
    )

    month_map = {
        "01": "Jan","02":"Feb","03":"Mar","04":"Apr",
        "05":"May","06":"Jun","07":"Jul","08":"Aug",
        "09":"Sep","10":"Oct","11":"Nov","12":"Dec"
    }

    months = [month_map[m] for m, v in monthly_raw]
    month_values = [v for m, v in monthly_raw]

    # Class-wise chart
    class_raw = (
        db.session.query(Student.class_name, func.count(Attendance.id))
        .join(Attendance, Attendance.student_id == Student.student_id)
        .group_by(Student.class_name)
        .all()
    )

    class_labels = [c for c, v in class_raw]
    class_values = [v for c, v in class_raw]

    # Student table
    report_list = []
    all_students = Student.query.all()

    for s in all_students:
        total = Attendance.query.filter_by(student_id=s.student_id).count()
        percent = round((total / 30) * 100, 2)
        report_list.append({
            "student_id": s.student_id,
            "name": s.name,
            "class_name": s.class_name,
            "total_attendance": total,
            "percentage": percent
        })

    avg = round(sum(s["percentage"] for s in report_list) / len(report_list), 2) if report_list else 0

    top_class = "N/A"
    if class_values:
        top_class = class_labels[class_values.index(max(class_values))]

    total_records = Attendance.query.count()

    return render_template(
        "reports.html",
        months=months,
        monthly_values=month_values,
        class_labels=class_labels,
        class_values=class_values,
        report_list=report_list,
        total_records=total_records,
        avg_attendance=avg,
        top_class=top_class,
        active="reports"
    )


# =====================================================
# RUN FLASK
# =====================================================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
