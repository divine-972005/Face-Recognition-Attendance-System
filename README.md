
# Face Recognition Attendance System

## 1. Project Overview
The Face Recognition Attendance System is a Python-based web application designed to simplify student attendance management using face recognition technology. It combines computer vision with a web interface to support student management, attendance tracking, and report viewing.

## 2. Objectives
- Automate attendance recording using face recognition.
- Maintain student information systematically.
- Reduce manual attendance errors and effort.
- Provide an interface to view attendance records and reports.

## 3. Technologies Used
- **Programming Language:** Python
- **Face Recognition / Computer Vision:** OpenCV
- **Backend:** Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Face Detection:** Haar Cascade

## 4. Main Features
- Dashboard for accessing application functions.
- Student information management.
- Camera interface for face recognition.
- Attendance record management.
- Results and report viewing.
- Face recognition model training support.

## 5. Project Structure

```text
Face-Recognition-Attendance-System/
├── app.py
├── recognize.py
├── train_recognizer.py
├── models.py
├── models/
├── instance/
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── students.html
│   ├── attendance.html
│   ├── results.html
│   ├── reports.html
│   └── partials/
├── face_model.yml
└── label_map.npy
```

*Note: The structure above lists the main files visible during upload. Add any other required files and folders present in your repository.*

## 6. Installation and Execution

1. Install Python 3.11 or another compatible version.
2. Clone or download this repository.
3. Open a terminal in the project directory.
4. Install the required dependencies listed in `requirements.txt`.
5. Configure the database and required model files.
6. Run the application using:

```bash
python app.py
```

7. Open the local URL displayed in the terminal in your web browser.

**Note:** The exact dependencies and setup steps should match the current source code. Create and upload `requirements.txt` if it is not already present.

## 7. Expected Outcome
The application provides a web interface for student management, face recognition-based attendance operations, and attendance report viewing.

## 8. Future Enhancements
- Improve recognition accuracy under different lighting conditions.
- Add secure authentication and role-based access.
- Support attendance analytics and report exports.
- Improve data privacy and database security.

## 9. Conclusion
This project demonstrates the application of computer vision and web development to student attendance management. It combines Python-based processing with a web interface to explore a more efficient approach to recording and managing attendance.

## 10. Author
**GitHub:** [divine-972005](https://github.com/divine-972005)
