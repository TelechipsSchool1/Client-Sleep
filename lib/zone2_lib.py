import serial
import struct
import numpy as np
import cv2
import dlib
from imutils import face_utils
from lib.param import *

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

    return (co2_high * 256) + co2_low

# CO2 농도 읽기
def read_co2_from_sensor():
    request_packet = generate_request_packet()
    try:
        with serial.Serial(UART_PORT, baudrate=BAUDRATE, timeout=TIMEOUT) as ser:
            ser.write(request_packet)
            response = b''
            while len(response) < 12:
                response += ser.read(12 - len(response))
            if len(response) == 12:
                return process_response(response)
            else:
                print("Incomplete response.")
                return None
    except Exception as e:
        print(f"Error reading CO2 sensor: {e}")
        return None

# 눈 사이 거리 계산
def compute(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

# 얼굴 감지 및 졸음 측정
def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)
    return 2 if ratio > 0.25 else (1 if 0.21 < ratio <= 0.25 else 0)
