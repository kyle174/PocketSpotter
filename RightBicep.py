from flask import Flask, Response, render_template
import cv2
import mediapipe as mp
import numpy as np
import time
import angle

app = Flask(__name__)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

counter = 0
stage = None
last_rep_time = 0

def generate_frames():
    global counter, stage, last_rep_time

    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark

                rshoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                relbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                rwrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                right_angle = angle.calculate_angle(rshoulder, relbow, rwrist, image)

                feedback = ""
                color = (0, 255, 0)
                if right_angle < 30:
                    feedback = "Don't curl too far up!"
                    color = (0, 0, 255)
                elif right_angle > 150:
                    feedback = "Complete the curl!"
                    color = (0, 0, 255)
                else:
                    feedback = "Good form!"
                    color = (0, 255, 0)

                cv2.putText(image, feedback, (150, 50), cv2.FONT_HERSHEY_DUPLEX, 1, color, 2, cv2.LINE_AA)

                if right_angle > 150:
                    stage = "down"
                    start_time = time.time() 
                if right_angle < 50 and stage == "down":
                    current_time = time.time()
                    if current_time - last_rep_time < 3:
                        pp1 = (565, 170) 
                        pp2 = (625, 170) 
                        pp3 = (595, 120) 
                        triangle = np.array([pp1, pp2, pp3], np.int32)
                        cv2.fillPoly(image, [triangle], (3, 186, 252))
                        cv2.polylines(image, [triangle], isClosed=True, color=(0, 0, 0), thickness=2)

                        cv2.putText(image, '!', (588,163), 
                                    cv2.FONT_HERSHEY_DUPLEX, 1.25, (0,0,0), 1, cv2.LINE_AA)
                        cv2.putText(image, 'SLOW!', (572,190), 
                                    cv2.FONT_HERSHEY_DUPLEX, 0.5, (3, 186, 252), 1, cv2.LINE_AA)
                    else:
                        stage = "up"
                        counter += 1
                        last_rep_time = current_time
                        print(f"Rep Counted! Total Reps: {counter}")

            except Exception as e:
                print(e)

            cv2.rectangle(image, (545,0), (665, 105), (126,115,101), -1)
            cv2.rectangle(image, (550,0), (650, 100), (186,173,167), -1)
            
            cv2.putText(image, 'REPS', (580,20), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), 
                        (580,80), 
                        cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)  

            ret, buffer = cv2.imencode('.jpg', image)
            if not ret:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()
