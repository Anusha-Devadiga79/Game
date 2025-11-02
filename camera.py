import sys
import cv2
import os

if len(sys.argv) < 2:
    print("Student name required as argument.")
    print("Usage: python camera.py <student_name>")
    sys.exit()

name = sys.argv[1]
data_folder = "data"
os.makedirs(data_folder, exist_ok=True)

cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Failed to open camera.")
    sys.exit()

ret, frame = cam.read()
if ret:
    output_path = os.path.join(data_folder, f"{name}.png")
    cv2.imwrite(output_path, frame)
    print(f"Image saved as {output_path}")
    cv2.imshow("Student Capture", frame)
    cv2.waitKey(1000)
else:
    print("Failed to capture image.")

cam.release()
cv2.destroyAllWindows()
