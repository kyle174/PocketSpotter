import cv2
import mediapipe as mp
import numpy as np
import time

def calculate_angle(a, b, c, image):
    h, w, _ = image.shape  # Height and width of the image

    # Scale normalized coordinates to pixel values
    x1, y1 = int(a[0] * w), int(a[1] * h)
    x2, y2 = int(b[0] * w), int(b[1] * h)
    x3, y3 = int(c[0] * w), int(c[1] * h)

    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    cv2.line(image, (x1, y1), (x2, y2), (255, 255, 255), 3)
    cv2.line(image, (x3, y3), (x2, y2), (255, 255, 255), 3)
    cv2.circle(image, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
    cv2.circle(image, (x1, y1), 15, (0, 0, 255), 2)
    cv2.circle(image, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
    cv2.circle(image, (x2, y2), 15, (0, 0, 255), 2)
    cv2.circle(image, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
    cv2.circle(image, (x3, y3), 15, (0, 0, 255), 2)

    return angle