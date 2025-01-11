from flask import Flask, Response, render_template
import cv2
import mediapipe as mp
import numpy as np
import time
import statistics

app = Flask(__name__)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

counter = 0
stage = None
last_rep_time = 0
inbalanced_state = 0

def calculate_angle(a, b, c, image):
    h, w, _ = image.shape  

    x1, y1 = int(a[0] * w), int(a[1] * h)
    x2, y2 = int(b[0] * w), int(b[1] * h)
    x3, y3 = int(c[0] * w), int(c[1] * h)

    a = np.array(a)
    b = np.array(b)  
    c = np.array(c)  

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

def generate_frames():
    global counter, stage, last_rep_time, inbalanced_state
    left_angles = []
    right_angles = []

    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
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

                required_landmarks = [
                    mp_pose.PoseLandmark.LEFT_SHOULDER,
                    mp_pose.PoseLandmark.LEFT_ELBOW,
                    mp_pose.PoseLandmark.LEFT_WRIST,
                    mp_pose.PoseLandmark.RIGHT_SHOULDER, 
                    mp_pose.PoseLandmark.RIGHT_ELBOW,
                    mp_pose.PoseLandmark.RIGHT_WRIST
                ]
                if not all(landmarks[lm.value].visibility > 0.5 for lm in required_landmarks):
                    cv2.putText(image, "Ensure full body is visible!", (50, 50),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    # Skip this frame
                    ret, buffer = cv2.imencode('.jpg', image)
                    if not ret:
                        break
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                    continue

                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist, image)
                right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist, image)
                left_angles.append(left_angle)
                right_angles.append(right_angle)

                feedback = ""
                color = (0, 0, 255)
                if len(left_angles) > 10 and len(right_angles) > 10:
                    left_mean = statistics.mean(left_angles[-10:])
                    right_mean = statistics.mean(right_angles[-10:])
                    
                    if abs(left_mean - right_mean) > 25 and inbalanced_state == 0:
                        feedback = "Incorrect form detected: Left and right angles differ by more than 25 degrees"
                        inbalanced_state = 1 
                    elif abs(left_mean - right_mean) <= 25 and inbalanced_state == 1:
                        inbalanced_state = 0  

                cv2.putText(image, feedback, (150, 50), cv2.FONT_HERSHEY_DUPLEX, 1, color, 2, cv2.LINE_AA)
                
                if left_angle > 150 and right_angle > 150 and stage != "up":
                    stage = "down"
                if left_angle < 50 and stage == "down":
                    stage = "up"
                    start_time = time.time() 
                if left_angle > 150 and right_angle > 150 and stage == "up":
                    current_time = time.time()
                    if current_time - last_rep_time < 2.5:
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
                        stage = "down"
                        counter += 1
                        last_rep_time = current_time
                        print(f"Rep Counted! Total Reps: {counter}")

            except Exception as e:
                print(e)

            cv2.rectangle(image, (545,0), (665, 105), (126,115,101), -1)
            cv2.rectangle(image, (550,0), (650, 100), (186,173,167), -1)
            
            cv2.putText(image, 'REPS', (580,20), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            if counter < 10:
                cv2.putText(image, str(counter), (580,80), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            else:
                cv2.putText(image, str(counter), (550,80), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', image)
            if not ret:
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)