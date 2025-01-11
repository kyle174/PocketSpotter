from flask import Flask, Response, render_template_string
import cv2
import mediapipe as mp
import numpy as np
import time
import statistics
import angle


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Define inbalanced_state globally to persist its value across calls
inbalanced_state = 0
too_fast_state = 0
def determine_bench_form(left_angles, right_angles, timestamps):
    global inbalanced_state  # Use the global variable
    global too_fast_state
    global too_slow_state
    T_MAX = 5  # Maximum time between reps in seconds
    T_MIN = 1

    # Check time between reps
    if len(timestamps) > 1:
        time_diff = timestamps[-1] - timestamps[-2]
        if time_diff > T_MAX and too_slow_state == 0:
            print("Incorrect form detected: Time between reps too high")
            too_slow_state = 1  # Update state to prevent repeated warnings
        elif time_diff <= T_MAX and too_slow_state == 1:
            too_slow_state = 0  # Reset the state when the speed is corrected
        elif time_diff < T_MIN and too_fast_state == 0:
            print("Incorrect form detected: Reps too fast")
            too_fast_state = 1  # Update state to prevent repeated warnings
        elif time_diff >= T_MIN and too_fast_state == 1:
            too_fast_state = 0  # Reset the state when the speed is corrected

    # Check for symmetry
    if len(left_angles) > 10 and len(right_angles) > 10:
        left_mean = statistics.mean(left_angles[-10:])
        right_mean = statistics.mean(right_angles[-10:])
        
        if abs(left_mean - right_mean) > 25 and inbalanced_state == 0:
            print("Incorrect form detected: Left and right angles differ by more than 25 degrees")
            inbalanced_state = 1  # Update state to prevent repeated warnings
        elif abs(left_mean - right_mean) <= 25 and inbalanced_state == 1:
            inbalanced_state = 0  # Reset the state when the imbalance is corrected

    # Check for symmetry
    if len(left_angles) > 10 and len(right_angles) > 10:
        left_mean = statistics.mean(left_angles[-10:])
        right_mean = statistics.mean(right_angles[-10:])
        
        if abs(left_mean - right_mean) > 25 and inbalanced_state == 0:
            print("Incorrect form detected: Left and right angles differ by more than 25 degrees")
            inbalanced_state = 1  # Update state to prevent repeated warnings
        elif abs(left_mean - right_mean) <= 25 and inbalanced_state == 1:
            inbalanced_state = 0  # Reset the state when the imbalance is corrected

def generate_frames_bench():
    cap = cv2.VideoCapture(0)

    # Curl counter variables
    counter = 0
    stage = None
    left_angles = []
    right_angles = []
    timestamps = []

    ## Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates
                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                              landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                # Calculate angle
                left_angle = angle.calculate_angle(left_shoulder, left_elbow, left_wrist, image)
                right_angle = angle.calculate_angle(right_shoulder, right_elbow, right_wrist, image)

                # Append angles to lists
                left_angles.append(left_angle)
                right_angles.append(right_angle)

                # Determine bench press form
                determine_bench_form(left_angles, right_angles, timestamps)

                # Visualize angle
                cv2.putText(image, str(left_angle),
                            tuple(np.multiply(left_elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )
                cv2.putText(image, str(right_angle),
                            tuple(np.multiply(right_elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )

            except:
                pass

            # Render curl counter
            # Setup status box
            cv2.rectangle(image, (0, 0), (75, 73), (245, 117, 16), -1)

            # Rep data
            cv2.putText(image, 'REPS', (15, 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter),
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

            if left_angle > 150 and right_angle > 150 and stage != "up":
                stage = "down"
            if left_angle < 50 and stage == 'down':
                stage = "up"
            if stage == 'up' and left_angle > 150 and right_angle > 150:
                counter += 1
                timestamps.append(time.time())
                print(counter)
                stage = "down"

            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

