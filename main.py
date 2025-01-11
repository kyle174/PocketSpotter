from flask import Flask, Response, render_template, request, redirect, url_for
import cv2
import mediapipe as mp
import numpy as np
import time

import Benchpress
import RightBicep

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

@app.route('/RightBicep')
def show_right_bicep():
    return Response(RightBicep.right_bicep_generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Benchpress')
def show_benchpress():
    return Response(Benchpress.generate_frames_bench(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
