import cv2
import os
import numpy as np

data_path = "data/known/"

faces = []
labels = []
label_map = {}
current_label = 0

print("Scanning folders...")

for student_id in os.listdir(data_path):
    folder = os.path.join(data_path, student_id)

    if not os.path.isdir(folder):
        continue

    print("Processing:", student_id)
    label_map[current_label] = student_id

    for img_file in os.listdir(folder):
        img_path = os.path.join(folder, img_file)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            continue

        faces.append(img)
        labels.append(current_label)

    current_label += 1

if len(faces) == 0:
    print("No images found.")
    exit()

faces = np.array(faces)
labels = np.array(labels)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, labels)

recognizer.write("face_model.yml")
np.save("label_map.npy", label_map)

print("Training complete!")
print("Model saved as face_model.yml")
print("Labels saved as label_map.npy")
