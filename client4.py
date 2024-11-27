import cv2
import socket
import struct

# TCP/IP 소켓 설정
HOST = "192.168.0.245"  # 서버 IP 주소
PORT = 9999  # 포트 번호
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# OpenCV로 비디오 캡처
cap = cv2.VideoCapture(0)

while True:
    try:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        # 프레임을 PNG로 인코딩 (메모리에서 처리)
        ret, buffer = cv2.imencode('.png', frame)
        if not ret:
            print("Failed to encode frame. Skipping...")
            continue

        # 데이터 크기를 네트워크 바이트 오더로 전송
        size = len(buffer)
        sock.sendall(struct.pack('!I', size) + buffer.tobytes())  # 데이터 크기 + 실제 데이터
        print("Image sent successfully.")

    except Exception as e:
        print(f"Error: {e}")
        break

# 리소스 해제
cap.release()
sock.close()
