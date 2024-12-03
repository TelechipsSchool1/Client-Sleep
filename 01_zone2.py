import cv2
import numpy as np
import dlib
import struct
import socket
import serial
import time
from imutils import face_utils

# --- Client Socket Configuration ---
LOCAL_IP = '0.0.0.0'  # 로컬 IP (0.0.0.0은 모든 인터페이스를 의미)
LOCAL_PORT = 8080    # 원하는 로컬 포트를 지정

SERVER_IP = '192.168.137.1'  # 서버 IP 주소 #실제 서버 주소는 '192.168.137.6'
SERVER_PORT = 12345          # 서버 포트 번호

# --- CO2 Sensor Configuration ---
UART_PORT = "/dev/ttyAMA2"
BAUDRATE = 9600
TIMEOUT = 1

# 요청 패킷 생성
def generate_request_packet():
    start_bytes = [0x42, 0x4D]
    command = [0xE3]
    parameters = [0x00, 0x00]
    chksum_high = [0x01]
    chksum_low = [0x72]
    return bytes(start_bytes + command + parameters + chksum_high + chksum_low)

# 응답 데이터 처리
def process_response(response):
    if len(response) != 12:
        print("Invalid response length.")
        return None
    
    co2_high = response[4]
    co2_low = response[5]
    checksum_total = sum(response[:10])
    calculated_high = checksum_total // 256
    calculated_low = checksum_total % 256

    if (calculated_high != response[10]) or (calculated_low != response[11]):
        print("Checksum invalid!")
        return None

    # CO₂ 농도 계산
    return (co2_high * 256) + co2_low

# CO2 농도 읽기 함수
# def read_co2_from_sensor():
#     request_packet = generate_request_packet()
#     try:
#         with serial.Serial(UART_PORT, baudrate=BAUDRATE, timeout=TIMEOUT) as ser:
#             ser.write(request_packet)
#             response = ser.read(12)
#             if len(response) == 12:
#                 return process_response(response)
#             else:
#                 print("Incomplete response.")
#                 return None
#     except Exception as e:
#         print(f"Error reading CO2 sensor: {e}")
#         return None

def read_co2_from_sensor():
    request_packet = generate_request_packet()
    try:
        with serial.Serial(UART_PORT, baudrate=BAUDRATE, timeout=TIMEOUT) as ser:
            ser.write(request_packet)
            response = b''
            while len(response) < 12:
                response += ser.read(12 - len(response))  # 부족한 바이트만 추가로 읽음
            if len(response) == 12:
                return process_response(response)
            else:
                print("Incomplete response.")
                return None
    except Exception as e:
        print(f"Error reading CO2 sensor: {e}")
        return None


# --- Eye Blink Detection Configuration ---
cap = cv2.VideoCapture(1)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

zone_id = 2
co2 = 0.0
heart = 0.0
sleep_score = 100

packet_format = 'i f f i'
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.bind((LOCAL_IP, LOCAL_PORT))
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print(f"Connected to server at {SERVER_IP} : {SERVER_PORT} from local port {LOCAL_PORT}")
except Exception as e:
    print(f"Error: {e}")
    client_socket.close()

#client_socket.connect(('192.168.137.1', 12345))


sleep = 0
drowsy = 0
active = 0
status = 0
color = (0, 0, 0)

def compute(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)
    return 2 if ratio > 0.25 else (1 if 0.21 < ratio <= 0.25 else 0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        left_blink = blinked(landmarks[36], landmarks[37], 
                             landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43], 
                              landmarks[44], landmarks[47], landmarks[46], landmarks[45])
        
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

    # heart 값 읽기
    try:
        with open("heart.txt", "r") as heart_file:
            lines = heart_file.readlines()  # 모든 줄 읽기
            if len(lines) >= 2:  # 최소 두 줄인지 확인
                heart = float(lines[0].strip())  # 첫 줄: 현재 심박수
                heart_avg = float(lines[1].strip())  # 두 번째 줄: 평균 심박수
            else:
                print("heart.txt does not contain enough data.")
                heart = 0.0
                heart_avg = 0.0
    except Exception as e:
        print(f"Error reading heart value: {e}")
        heart = 0.0
        heart_avg = 0.0

    # Sleep score 업데이트
    frame_score = 17 if status else -3
    envir_score = 85 if co2 > 1500 else 0
    sleep_score += frame_score
    if sleep_score < envir_score:
        sleep_score = envir_score

    # 총 점수 255 이상 : 졸음 경보
    # 총 점수 510 이상 : 졸음 위험
    # 패킷 전송
    data_packet = struct.pack(packet_format, zone_id, co2, heart, sleep_score)
    client_socket.sendall(data_packet)
    time.sleep(1)

    #cv2.imshow("Result", frame)
    key = cv2.waitKey(1)
    if key == 27:  # Esc 키로 종료
        break

cap.release()
cv2.destroyAllWindows()
client_socket.close()

