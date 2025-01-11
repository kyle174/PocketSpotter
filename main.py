from flask import Flask, Response, render_template, request, redirect, url_for
import cv2
import mediapipe as mp
import numpy as np
import time

import Benchpress
import BicepCurl
import Squat

app = Flask(__name__)

exercise_type = "bicep_curl"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_exercise', methods=['POST'])
def set_exercise():
    global exercise_type
    exercise_type = request.form['exercise']
    return redirect(url_for('index'))

@app.route('/BicepCurl')
def show_bicep_curl():
    return Response(BicepCurl.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Benchpress')
def show_benchpress():
    return Response(Benchpress.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Squat')
def show_squat():
    return Response(Squat.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__ == "__main__":
    app.run(debug=True)
