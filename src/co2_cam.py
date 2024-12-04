import sys
sys.path.append('/root/clent_sleep_ver2')  # 모듈 경로 추가

import cv2
import dlib
import socket
import struct
import time
import fcntl
from lib.zone2_lib import read_co2_from_sensor, blinked
from lib.param import *
from imutils import face_utils

cap = cv2.VideoCapture(1)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(SHAPE_PREDICTOR)

# 초기 변수 설정
co2 = 0.0


sleep = 0
drowsy = 0
active = 0
status = 0
color = (0, 0, 0)

# 메인 루프
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

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
        # cv2.putText(frame, str(status), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    # CO₂ 데이터 읽기
    co2_concentration = read_co2_from_sensor()
    co2 = co2_concentration if co2_concentration is not None else 0.0

    # CO₂, sleep status 데이터 저장
    try:
        with open("zone2.txt","w") as zone2_file:
            fcntl.flock(zone2_file, fcntl.LOCK_EX)
            zone2_file.write(f"{co2:.2f}\n")
            zone2_file.write(f"{status:d}\n")
            fcntl.flock(zone2_file, fcntl.LOCK_UN)
    except Exception as e:
        print(f"Error writing to zone2.txt: {e}")

    


    # 종료 조건
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()
