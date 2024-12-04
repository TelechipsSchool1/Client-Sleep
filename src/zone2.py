import cv2
import dlib
import socket
import struct
import time
from lib.zone2_lib import read_co2_from_sensor, blinked
from lib.param import *

cap = cv2.VideoCapture(1)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(SHAPE_PREDICTOR)

# 초기 변수 설정
zone_id = ZONE_ID
co2 = 0.0
heart = 0.0
sleep_score = 100

packet_format = 'i f f i'
# 소켓 초기화
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.bind((LOCAL_IP, LOCAL_PORT))
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print(f"Connected to server at {SERVER_IP} : {SERVER_PORT} from local port {LOCAL_PORT}")
except Exception as e:
    print(f"Error: {e}")
    client_socket.close()

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

    # heart.txt 읽기
    try:
        with open("heart.txt", "r") as heart_file:
            lines = heart_file.readlines()
            if len(lines) >= 2:
                heart = float(lines[0].strip())
                heart_avg = float(lines[1].strip())
            else:
                heart = 0.0
    except Exception as e:
        print(f"Error reading heart value: {e}")
        heart = 0.0

    # Sleep score 업데이트
    frame_score = SLEEP_UP_SCORE if status else SLEEP_DOWN_SCORE
    envir_score = CO2_THRESHOLD_OVER_SCORE if co2 > CO2_THRESHOLD else CO2_THRESHOLD_UNDER_SCORE
    sleep_score += frame_score
    sleep_score = max(sleep_score, envir_score)

    # 총 점수 255 이상 : 졸음 경보
    # 총 점수 510 이상 : 졸음 위험
    # 패킷 전송
    data_packet = struct.pack(packet_format, zone_id, co2, heart, sleep_score)
    client_socket.sendall(data_packet)
    time.sleep(1)

    #cv2.imshow("Result", frame)

    # 종료 조건
    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()
