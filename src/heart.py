import sys
sys.path.append('/root/clent_sleep_ver2')  # 모듈 경로 추가

import time
from collections import deque
import numpy as np
import fcntl
from lib.heart_lib import init_max30102, read_fifo, preprocess_data, calculate_bpm
from lib.param import I2C_BUS
import smbus

def main():
    bus = smbus.SMBus(I2C_BUS)
    init_max30102(bus)

    red_data = []
    start_time = time.time()
    recent_bpm_values = deque(maxlen=10)  # 최근 10개 데이터를 저장하는 큐

    try:
        while True:
            red, ir = read_fifo(bus)
            if red < 50000 or red > 200000:
                continue

            red_data.append(red)

            # Calculate BPM every 5 seconds
            if time.time() - start_time >= 5:
                filtered_data = preprocess_data(red_data)
                bpm = calculate_bpm(filtered_data, sampling_rate=50)
                if bpm > 0:
                    recent_bpm_values.append(bpm)
                    recent_avg_bpm = np.mean(recent_bpm_values)
                    print(f"Heart Rate: {bpm:.2f} bpm, Avg: {recent_avg_bpm:.2f} bpm")
                    try:
                        with open("heart.txt", "w") as heart_file:
                            fcntl.flock(heart_file, fcntl.LOCK_EX)
                            heart_file.write(f"{bpm:.2f}\n")
                            heart_file.write(f"{recent_avg_bpm:.2f}\n")
                            fcntl.flock(heart_file, fcntl.LOCK_UN)
                    except Exception as e:
                        print(f"Error writing to heart.txt: {e}")

                red_data = []
                start_time = time.time()

            time.sleep(0.02)
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    finally:
        bus.close()

if __name__ == "__main__":
    main()
