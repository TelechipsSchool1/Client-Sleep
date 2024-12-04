import sys
sys.path.append('/root/clent_sleep_ver2')  # 모듈 경로 추가

import socket
import struct
import time
from lib.param import *

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

status = 0

# 메인 루프
while True:

    # 졸음 status , CO₂ 데이터 읽기
    try:
        with open("zone2.txt","r") as zone2_file:
            lines = zone2_file.readlines()
            if len(lines) >= 2:
                co2 = float(lines[0].strip())
                status = float(lines[1].strip())
            else:
                co2 = 0
                status = 0
    except Exception as e:
        print(f"Error reading zone2 value: {e}")
        co2 = 0
        status = 0


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

client_socket.close()
