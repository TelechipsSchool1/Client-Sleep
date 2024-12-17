import numpy as np
import cv2
from lib.param import *

# Calculate the distance between eyes
def compute(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

# Face detection and sleepiness measurement
def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)
    return 2 if ratio > 0.25 else (1 if 0.21 < ratio <= 0.25 else 0)

def calculate_head_pose(landmarks):
    # 2D landmark coordinate
    image_points = np.array([
        (landmarks[30][0], landmarks[30][1]),  # nose
        (landmarks[8][0], landmarks[8][1]),    # tin
        (landmarks[36][0], landmarks[36][1]),  # outside left eye
        (landmarks[45][0], landmarks[45][1]),  # outside right eye
        (landmarks[48][0], landmarks[48][1]),  # left mouse
        (landmarks[54][0], landmarks[54][1])   # right mouse
    ], dtype="double")

    # Camera internal parameters
    size = (640, 480)
    focal_length = size[1]
    center = (size[1] / 2, size[0] / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype="double")
    dist_coeffs = np.zeros((4, 1))  # No distortion

    # 3D model point
    model_points = np.array([
        (0.0, 0.0, 0.0),             # nose
        (0.0, -330.0, -65.0),        # int
        (-225.0, 170.0, -135.0),     # outside left eye
        (225.0, 170.0, -135.0),      # outside right eye
        (-150.0, -150.0, -125.0),    # left mouse
        (150.0, -150.0, -125.0)      # right mouse
    ])

    # Calculate posture
    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    return rotation_vector, translation_vector

