import sys
sys.path.append('/root/Client-Sleep')  # Module Path

import socket
import struct
import time
from lib.param import *

# Set init value
zone_id = ZONE_ID
co2 = 0.0
heart = 0.0
sleep_score = 0

packet_format = 'i f f i'
# Initialize Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.bind((LOCAL_IP, LOCAL_PORT))
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print(f"Connected to server at {SERVER_IP} : {SERVER_PORT} from local port {LOCAL_PORT}")
except Exception as e:
    print(f"Error: {e}")
    client_socket.close()

status = 0

# main loop
while True:

    # Read CO₂ data
    try:
        with open("co2.txt","r") as co2_file:
            lines = co2_file.readlines()
            if len(lines) >= 1:
                co2 = float(lines[0].strip())
    except Exception as e:
        print(f"Error reading zone2 value: {e}")
        co2 = 0

    print(f"co2 : {co2:.2f}")
    
    # Read sleep status data
    try:
        with open("status.txt","r") as status_file:
            lines = status_file.readlines()
            if len(lines) >= 2:
                status = int(lines[0].strip())
            else:
                status = 0
    except Exception as e:
        print(f"Error reading zone2 value: {e}")
        status = 0

    # Read heart data
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

    # Updata sleep score
    frame_score = SLEEP_UP_SCORE if status else SLEEP_DOWN_SCORE
    envir_score = CO2_THRESHOLD_OVER_SCORE if co2 > CO2_THRESHOLD else CO2_THRESHOLD_UNDER_SCORE
    sleep_score += frame_score
    sleep_score = max(sleep_score, envir_score)

    print(co2)
    print(heart)

    # Send packet
    data_packet = struct.pack(packet_format, zone_id, co2, heart, sleep_score)
    client_socket.sendall(data_packet)
    time.sleep(1)

client_socket.close()
