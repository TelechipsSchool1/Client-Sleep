import smbus
import time
from scipy.signal import find_peaks
import numpy as np
from collections import deque
import fcntl

# I2C bus and device address
I2C_BUS = 1
DEVICE_ADDRESS = 0x57

# Register addresses (based on datasheet)
REG_INTR_ENABLE_1 = 0x02
REG_INTR_ENABLE_2 = 0x03
REG_FIFO_WR_PTR = 0x04
REG_OVF_COUNTER = 0x05
REG_FIFO_RD_PTR = 0x06
REG_FIFO_DATA = 0x07
REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED1_PA = 0x0C
REG_LED2_PA = 0x0D

# Initialize the MAX30102 sensor
def init_max30102(bus):
    try:
        bus.write_byte_data(DEVICE_ADDRESS, REG_INTR_ENABLE_1, 0x00)
        bus.write_byte_data(DEVICE_ADDRESS, REG_INTR_ENABLE_2, 0x00)
        bus.write_byte_data(DEVICE_ADDRESS, REG_FIFO_WR_PTR, 0x00)
        bus.write_byte_data(DEVICE_ADDRESS, REG_OVF_COUNTER, 0x00)
        bus.write_byte_data(DEVICE_ADDRESS, REG_FIFO_RD_PTR, 0x00)
        bus.write_byte_data(DEVICE_ADDRESS, REG_MODE_CONFIG, 0x03)  # SPO2 mode
        bus.write_byte_data(DEVICE_ADDRESS, REG_SPO2_CONFIG, 0x23)  # 50Hz, 411us pulse width
        bus.write_byte_data(DEVICE_ADDRESS, REG_LED1_PA, 0x1F)  # RED LED intensity
        bus.write_byte_data(DEVICE_ADDRESS, REG_LED2_PA, 0x1F)  # IR LED intensity
        print("MAX30102 initailized successfully!!")
    except Exception as e:
        print(f"Failed to read FIFO data : {e}")
        return 0, 0

# Read FIFO data
def read_fifo(bus):
    try:
        data = bus.read_i2c_block_data(DEVICE_ADDRESS, REG_FIFO_DATA, 6)
        red = (data[0] << 16) | (data[1] << 8) | data[2]
        ir = (data[3] << 16) | (data[4] << 8) | data[5]
        return red & 0x03FFFF, ir & 0x03FFFF
    except Exception as e:
        return 0, 0

# Moving average filter
def moving_average(data, window_size=5):
    if len(data) < window_size:
        return data
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

# Preprocess the data
def preprocess_data(data):
    # Apply moving average and ignore outliers
    smoothed_data = moving_average(data)
    valid_data = [x for x in smoothed_data if 50000 <= x <= 200000]
    return valid_data

# Calculate BPM based on peak intervals
def calculate_bpm(filtered_data, sampling_rate=50):
    if len(filtered_data) < 2:
        return 0

    peaks, _ = find_peaks(filtered_data, height=np.mean(filtered_data) * 0.6, distance=30)
    if len(peaks) < 2:
        return 0

    intervals = np.diff(peaks) / sampling_rate  # Convert intervals to seconds
    avg_interval = np.mean(intervals)
    bpm = 60 / avg_interval  # Convert to BPM
    return bpm

def main():
    bus = smbus.SMBus(I2C_BUS)
    init_max30102(bus)

    red_data = []
    start_time = time.time()
    recent_bpm_values = deque(maxlen=10)  # 최근 10개 데이터를 저장하는 큐

    try:
        while True:
            red, ir = read_fifo(bus)
            if red < 50000 or red > 200000:  # Ignore outliers
                continue

            red_data.append(red)

            # Calculate BPM every 5 seconds
            if time.time() - start_time >= 5:
                filtered_data = preprocess_data(red_data)
                bpm = calculate_bpm(filtered_data, sampling_rate=50)
                if bpm > 0:  # 유효한 BPM만 기록
                    recent_bpm_values.append(bpm)  # 최근 10개 데이터에 추가
                    recent_avg_bpm = np.mean(recent_bpm_values)  # 최근 데이터 평균
                    # heart.txt 파일에 현재 값과 평균 값 저장 (쓰기 잠금 적용)
                    print(f"Heart Rate : {bpm:.2f} bpm, ang : {recent_avg_bpm:.2f}bpm")
                    try:
                        with open("heart.txt", "w") as heart_file:
                            fcntl.flock(heart_file, fcntl.LOCK_EX)  # 쓰기 잠금
                            heart_file.write(f"{bpm:.2f}\n")  # 현재 BPM 값
                            heart_file.write(f"{recent_avg_bpm:.2f}\n")  # 평균 BPM 값
                            fcntl.flock(heart_file, fcntl.LOCK_UN)  # 잠금 해제
                    except Exception as e:
                        print(f"Error writing to heart.txt: {e}")

                red_data = []
                start_time = time.time()

            time.sleep(0.02)  # Adjust for 50Hz sampling rate
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    finally:
        bus.close()

if __name__ == "__main__":
    main()
