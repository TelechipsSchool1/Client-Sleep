#!/bin/bash

# 공통된 디렉토리 경로를 변수로 설정
BASE_DIR="/root/Client-Sleep/src"

# 각 Python 스크립트를 실행
python3 "$BASE_DIR/cam.py" &
python3 "$BASE_DIR/co2.py" &
python3 "$BASE_DIR/heart.py" &
python3 "$BASE_DIR/zone2_socket.py" &
