import serial
from lib.param import *

# Generate request packets
def generate_request_packet():
    start_bytes = [0x42, 0x4D]
    command = [0xE3]
    parameters = [0x00, 0x00]
    chksum_high = [0x01]
    chksum_low = [0x72]
    return bytes(start_bytes + command + parameters + chksum_high + chksum_low)

# Processing response datai
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

# Read CO2 concentration
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
