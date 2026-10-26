from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ---------------------------
# Student Model
# ---------------------------
class Student(db.Model):
    __tablename__ = 'students'

    student_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    class_name = db.Column(db.String(50))
    student_photo = db.Column(db.String(200))   # file name only

    # Relationships
    attendance = db.relationship('Attendance', backref='student', lazy=True)
    results = db.relationship('Result', backref='student', lazy=True)

    def __repr__(self):
        return f"<Student {self.student_id} - {self.name}>"


# ---------------------------
# Attendance Model
# ---------------------------
class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Attendance {self.student_id} at {self.timestamp}>"


# ---------------------------
# Result Model
# ---------------------------
class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey('students.student_id'), nullable=False)

    subject = db.Column(db.String(100), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    date = db.Column(db.String(20), nullable=False)   # store as 'YYYY-MM-DD'

    def __repr__(self):
        return f"<Result {self.student_id} - {self.subject}>"
