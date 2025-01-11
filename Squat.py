import cv2
import mediapipe as mp
import numpy as np
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

counter = 0
stage = None
last_rep_time = 0


def is_valid_form(hip_angle, knee_angle):
    # Example relationship: If hip_angle decreases, knee_angle should decrease proportionally
    angle_difference = 18
    if (hip_angle - knee_angle) < angle_difference and (hip_angle - knee_angle) > -angle_difference:
        return True
    else:    
        return False

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

    cv2.line(image, (x1,y1), (x2,y2), (255,255,255), 3)
    cv2.line(image, (x3,y3), (x2,y2), (255,255,255), 3)
    cv2.circle(image, (x1,y1), 10, (0, 0, 255), cv2.FILLED)
    cv2.circle(image, (x1,y1), 15, (0, 0, 255), 2)
    cv2.circle(image, (x2,y2), 10, (0, 0, 255), cv2.FILLED)
    cv2.circle(image, (x2,y2), 15, (0, 0, 255), 2)
    cv2.circle(image, (x3,y3), 10, (0, 0, 255), cv2.FILLED)
    cv2.circle(image, (x3,y3), 15, (0, 0, 255), 2)

    return angle

def generate_frames():
    global counter, stage, last_rep_time

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

                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                hip_angle = calculate_angle(shoulder, hip, knee, image)
                knee_angle = calculate_angle(hip, knee, ankle, image)

                if not is_valid_form(hip_angle, knee_angle):
                    feedback = ""
                    color = (0, 255, 0)
                    if hip_angle < (18 + knee_angle):
                        feedback = "Don't lean too far forward!"
                        color = (0, 0, 255)
                    if knee_angle < (18 + hip_angle):
                        feedback = "Don't bend your knees as much!"
                        color = (0, 0, 255)

                        
                        cv2.putText(image, feedback, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
                
                else:
                    if hip_angle > 160:
                        stage = "down"
                    if hip_angle < 68 and stage == 'down':
                        current_time = time.time()
                        if current_time - last_rep_time < 5:
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
