#!/bin/bash

# Set Directory Path
BASE_DIR="/root/Client-Sleep/src"

# Run Python Script
python3 "$BASE_DIR/cam.py" &
python3 "$BASE_DIR/co2.py" &
python3 "$BASE_DIR/heart.py" &
python3 "$BASE_DIR/zone2_socket.py" &
