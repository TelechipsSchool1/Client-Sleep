import smbus
import time
import numpy as np
from scipy.signal import find_peaks
from collections import deque
import fcntl
from lib.param import *

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
        print("MAX30102 initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize MAX30102: {e}")

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
    smoothed_data = moving_average(data)
    valid_data = [x for x in smoothed_data if 50000 <= x <= 200000]
    return valid_data

# Calculate BPM
def calculate_bpm(filtered_data, sampling_rate=50):
    if len(filtered_data) < 2:
        return 0

    peaks, _ = find_peaks(filtered_data, height=np.mean(filtered_data) * 0.6, distance=30)
    if len(peaks) < 2:
        return 0

    intervals = np.diff(peaks) / sampling_rate
    avg_interval = np.mean(intervals)
    bpm = 60 / avg_interval
    return bpm
