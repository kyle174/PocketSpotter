from flask import Flask, Response, request, render_template, redirect, url_for, send_from_directory
import cv2
import numpy as np
import base64
import os

from services import Benchpress, BicepCurl, Squat

app = Flask(__name__)

exercise_type = ""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/BicepCurl')
def show_bicep_curl():
    global exercise_type
    exercise_type = 'bicep_curl'
    return render_template('bicep_curl.html')


@app.route('/video_feed', methods=['POST'])
def video_feed():
    global exercise_type
    if request.method == 'POST':
        try:
            frame_data = request.json['frame']
            # Decode the Base64 image
            img_data = base64.b64decode(frame_data.split(',')[1])
            np_img = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            # Process the frame based on the exercise type
            if exercise_type == 'bicep_curl':
                processed_frame = BicepCurl.process(frame)
            elif exercise_type == 'benchpress':
                processed_frame = Benchpress.process(frame)
            elif exercise_type == 'squat':
                processed_frame = Squat.process(frame)
            else:
                processed_frame = frame

            # Optional: Display the processed frame for debugging
            cv2.imshow('Processed Frame', processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()

            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    else:
        return "Invalid request method", 405


if __name__ == "__main__":
    app.run(debug=True)
