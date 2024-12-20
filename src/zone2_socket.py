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
status = 0

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

    # Read sleep status data
    try:
        with open("status.txt","r") as status_file:
            lines = status_file.readlines()
            if len(lines) >= 1:
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
    
    # Read score data
    try:
        with open("score.txt", "r") as score_file:
            lines = score_file.readlines()
            if len(lines) >= 1:
                sleep_score = int(lines[0].strip())
            else:
                sleep_score = -1
    except Exception as e:
        print(f"Error reading heart value: {e}")
        sleep_score = -1

    print(f"co2 : {co2:.2f}")
    print(f"heart : {heart:.2f}")
    print(f"status : {status:d}")
    print(f"score : {sleep_score:d}")

    # Send packet
    data_packet = struct.pack(packet_format, zone_id, co2, heart, sleep_score)
    client_socket.sendall(data_packet)
    time.sleep(1)

client_socket.close()
