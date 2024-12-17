import sys
sys.path.append('/root/Client-Sleep')  # Module Path

import cv2
import dlib
import time
import fcntl
import numpy as np
from lib.cam_lib import blinked, calculate_head_pose
from lib.param import *
from imutils import face_utils

cap = cv2.VideoCapture(1)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(SHAPE_PREDICTOR)

# Set init value
sleep = 0
drowsy = 0
active = 0
status = 0
color = (0, 0, 0)

# main loop
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()
 
        face_frame = frame.copy()
        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
 
        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        # Detect blink
        left_blink = blinked(landmarks[36], landmarks[37], landmarks[38], 
                             landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43], landmarks[44], 
                              landmarks[47], landmarks[46], landmarks[45])
        
        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 6:
                status = 1
                color = (255, 0, 0)
        elif left_blink == 1 or right_blink == 1:
            sleep = 0
            active = 0
            drowsy += 1
            if drowsy > 6:
                status = 0
                color = (0, 0, 255)
        else:
            drowsy = 0
            sleep = 0
            active += 1
            if active > 6:
                status = 0
                color = (0, 255, 0)

        # Calculate head tilt
        rotation_vector, _ = calculate_head_pose(landmarks)
        pitch = np.degrees(rotation_vector[0][0])
        yaw = np.degrees(rotation_vector[1][0])
        roll = np.degrees(rotation_vector[2][0])

        # cv2.putText(frame, f"Pitch: {pitch:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # cv2.putText(frame, f"Yaw: {yaw:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # cv2.putText(frame, f"Roll: {roll:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if pitch > 20:  # Down head tilt
            cv2.putText(frame, "Head Down Detected!", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        #cv2.putText(frame, status, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        for n in range(0, 68):
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

    # Save sleep status
    try:
        with open("status.txt","w") as status_file:
            fcntl.flock(status_file, fcntl.LOCK_EX)
            status_file.write(f"{status:d}\n")
            fcntl.flock(status_file, fcntl.LOCK_UN)
    except Exception as e:
        print(f"Error writing to status.txt: {e}")
    
    #cv2.imshow("Result", frame)
    time.sleep(0.1)

    # End Condition
    key = cv2.waitKey(1)
    if key == 27: # Exit with the ESC key
        break

cap.release()
cv2.destroyAllWindows()
