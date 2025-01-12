from flask import Flask, Response, render_template, request, redirect, url_for, send_from_directory
import os

from services import Benchpress
from services import BicepCurl
from services import Squat

app = Flask(__name__)

exercise_type = ""
is_resting = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    return redirect(url_for('index'))

@app.route('/BicepCurl')
def show_bicep_curl():
    global exercise_type
    exercise_type = 'bicep_curl'
    return render_template('bicep_curl.html')

@app.route('/Benchpress')
def show_benchpress():
    global exercise_type
    exercise_type = 'benchpress'
    return render_template('benchpress.html')

@app.route('/Pushups')
def show_pushup():
    global exercise_type
    exercise_type = 'pushups'
    return render_template('pushups.html')

@app.route('/Squat')
def show_squat():
    global exercise_type
    exercise_type = 'squat'
    return render_template('squat.html')

@app.route('/update_rest_state', methods=['POST'])
def update_rest_state():
    global is_resting
    data = request.get_json()
    if data and 'is_resting' in data:
        is_resting = data['is_resting']
        print(f"Updated is_resting to: {is_resting}")
        return "Success", 200
    return "Invalid Request", 400


@app.route('/video_feed')
def video_feed():
    global is_resting
    if exercise_type == "bicep_curl":
        return Response(BicepCurl.generate_frames(is_resting), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise_type == 'benchpress':
        return Response(Benchpress.generate_frames(is_resting), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise_type == 'squat':
        return Response(Squat.generate_frames(is_resting), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif exercise_type == 'pushups':
        return Response(Benchpress.generate_frames(is_resting), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Invalid URL", 404
    

    
@app.route('/end_set', methods=['POST'])
def end_set():
    """
    This endpoint updates the counter in the specific exercise module when a set ends.
    """
    from services import Benchpress, BicepCurl, Squat  # Ensure we import the modules for each exercise

    data = request.get_json()
    if data:
        exercise_type = data.get('exercise_type')  # Get the exercise type from the request data
        if exercise_type == 'benchpress':
            Benchpress.counter = 0  # Reset the counter for Bench Press
            print("Counter reset for Bench Press.")
            return "Success", 200
        elif exercise_type == 'bicep_curl':
            BicepCurl.counter = 0  # Reset the counter for Bicep Curl
            print("Counter reset for Bicep Curl.")
            return "Success", 200
        elif exercise_type == 'squat':
            Squat.counter = 0  # Reset the counter for Squat
            print("Counter reset for Squat.")
            return "Success", 200
        elif exercise_type == 'pushups':
            print("Counter reset for Pushups.")
            return "Success", 200
    return "Invalid Request", 400





if __name__ == "__main__":
    app.run(debug=True)