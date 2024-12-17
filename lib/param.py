# Zone ID
ZONE_ID = 2

# Client Socket Configuration
LOCAL_IP = '0.0.0.0'  # local IP
LOCAL_PORT = 8080    # local port
SERVER_IP = '192.168.137.1'  # server IP address
SERVER_PORT = 12345          # server port number

# CO2 Sensor Configuration
UART_PORT = "/dev/ttyAMA2"
BAUDRATE = 9600
TIMEOUT = 1
CO2_THRESHOLD = 1500
CO2_THRESHOLD_OVER_SCORE = 85
CO2_THRESHOLD_UNDER_SCORE = 0

# Sleep Score
SLEEP_UP_SCORE = 17
SLEEP_DOWN_SCORE = -3

# Eye Blink Detection
SHAPE_PREDICTOR = "shape_predictor_68_face_landmarks.dat"

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

