import cv2
import numpy as np
import dlib
import time
from imutils import face_utils

# VideoCapture 객체 생성
cap = cv2.VideoCapture(0)

# 얼굴 검출기 및 랜드마크 예측기 초기화
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    if ratio > 0.25:
        return 2  # Eyes open
    elif ratio > 0.21 and ratio <= 0.25:
        return 1  # Eyes drowsy
    else:
        return 0  # Eyes closed

def calculate_head_pose(landmarks):
    # 2D 랜드마크 좌표
    image_points = np.array([
        (landmarks[30][0], landmarks[30][1]),  # 코끝
        (landmarks[8][0], landmarks[8][1]),    # 턱
        (landmarks[36][0], landmarks[36][1]),  # 왼쪽 눈 바깥쪽
        (landmarks[45][0], landmarks[45][1]),  # 오른쪽 눈 바깥쪽
        (landmarks[48][0], landmarks[48][1]),  # 왼쪽 입
        (landmarks[54][0], landmarks[54][1])   # 오른쪽 입
    ], dtype="double")

    # 카메라 내부 파라미터
    size = (640, 480)
    focal_length = size[1]
    center = (size[1] / 2, size[0] / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")
    dist_coeffs = np.zeros((4, 1))  # 왜곡 없음

    # 3D 모델 포인트
    model_points = np.array([
        (0.0, 0.0, 0.0),             # 코끝
        (0.0, -330.0, -65.0),        # 턱
        (-225.0, 170.0, -135.0),     # 왼쪽 눈 바깥쪽
        (225.0, 170.0, -135.0),      # 오른쪽 눈 바깥쪽
        (-150.0, -150.0, -125.0),    # 왼쪽 입
        (150.0, -150.0, -125.0)      # 오른쪽 입
    ])

    # 자세 계산
    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    return rotation_vector, translation_vector

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)

    for face in faces:
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
        face_frame = frame.copy()
        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        # 깜빡임 감지
        left_blink = blinked(landmarks[36], landmarks[37], 
                             landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43], 
                              landmarks[44], landmarks[47], landmarks[46], landmarks[45])

        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 6:
                status = "SLEEPING!!!"
                color = (255, 0, 0)
        elif left_blink == 1 or right_blink == 1:
            drowsy += 1
            sleep = 0
            active = 0
            if drowsy > 6:
                status = "Drowsy!"
                color = (0, 0, 255)
        else:
            active += 1
            drowsy = 0
            sleep = 0
            if active > 6:
                status = "Active :)"
                color = (0, 255, 0)

        # 고개 기울기 계산
        rotation_vector, _ = calculate_head_pose(landmarks)
        pitch = np.degrees(rotation_vector[0][0])
        yaw = np.degrees(rotation_vector[1][0])
        roll = np.degrees(rotation_vector[2][0])

        cv2.putText(frame, f"Pitch: {pitch:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Yaw: {yaw:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Roll: {roll:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if pitch > 20:  # 고개가 떨어짐
            cv2.putText(frame, "Head Down Detected!", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, status, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        for n in range(0, 68):
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

    cv2.imshow("Result", frame)
    time.sleep(0.1)
    key = cv2.waitKey(1)
    if key == 27:  # ESC 키로 종료
        break

cap.release()
cv2.destroyAllWindows()