import sys
sys.path.append('/root/Client-Sleep')  # Module path

import fcntl
import time
from lib.co2_lib import read_co2_from_sensor

# Set CO₂ init value
co2 = 0.0

# main loop
while True:
    # Read CO₂ data
    co2_concentration = read_co2_from_sensor()
    co2 = co2_concentration if co2_concentration is not None else 0.0

    # Save CO₂ data
    try:
        with open("co2.txt","w") as co2_file:
            fcntl.flock(co2_file, fcntl.LOCK_EX)
            co2_file.write(f"{co2:.2f}\n")
            fcntl.flock(co2_file, fcntl.LOCK_UN)
    except Exception as e:
        print(f"Error writing to co2.txt: {e}")

    time.sleep(0.1)
