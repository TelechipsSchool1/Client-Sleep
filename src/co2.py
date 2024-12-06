import sys
sys.path.append('/root/Client-Sleep')  # 모듈 경로 추가

import fcntl
import time
from lib.co2_lib import read_co2_from_sensor

# 초기 변수 설정
co2 = 0.0

# 메인 루프
while True:
    # CO₂ 데이터 읽기
    co2_concentration = read_co2_from_sensor()
    co2 = co2_concentration if co2_concentration is not None else 0.0

    # CO₂ 데이터 저장
    try:
        with open("co2.txt","w") as co2_file:
            fcntl.flock(co2_file, fcntl.LOCK_EX)
            co2_file.write(f"{co2:.2f}\n")
            fcntl.flock(co2_file, fcntl.LOCK_UN)
    except Exception as e:
        print(f"Error writing to co2.txt: {e}")

    #print(co2)
    time.sleep(0.1)
