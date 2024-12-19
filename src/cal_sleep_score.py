import sys
sys.path.append('/root/Client-Sleep')  # Module Path

import struct
import time
import fcntl
from lib.param import *

# Set init value
co2 = 0.0
heart = 0.0
sleep_score = 0
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
        print(f"Error reading co2 value: {e}")
        co2 = 0

    print(f"co2 : {co2:.2f}")
    
    # Read sleep status data
    try:
        with open("status.txt","r") as status_file:
            lines = status_file.readlines()
            if len(lines) >= 1:
                status = int(lines[0].strip())
            else:
                status = 0
    except Exception as e:
        print(f"Error reading status value: {e}")
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
    sleep_score = min(MAX_SLEEP_SCORE,sleep_score)

    #print(f"heart : {heart:.2f}")
    #print(f"status : {status:d}")
    #print(f"score : {sleep_score:d}")

    try:
        with open("score.txt","w") as score_file:
            fcntl.flock(score_file, fcntl.LOCK_EX)
            score_file.write(f"{sleep_score:d}\n")
            fcntl.flock(score_file, fcntl.LOCK_UN)
    except Exception as e:
        print(f"Error Writing to score.txt : {e}")
    
    time.sleep(0.2)

