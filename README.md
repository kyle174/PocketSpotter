# PocketSpotter

PocketSpotter is a cutting-edge fitness assistant that uses computer vision to provide real-time feedback during workouts. It can count reps, evaluate your form, and keep you on track with proper pacing, ensuring a safe and effective exercise routine. PocketSpotter supports multiple exercises including bicep curls, bench press, squats, and pushups.

## Features
* Rep Counting: Automatically detects and counts reps for supported exercises.
* Form Feedback: Analyzes joint angles to provide instant feedback on proper form.
* Pacing Alerts: Warns users if reps are performed too quickly, helping to maintain proper speed.
* Rest Timer: Tracks rest periods between sets to ensure effective recovery.
* Visual Overlay: Displays real-time stats and feedback directly on the screen during the workout.

## Supported Exercises
* Bicep Curls
* Bench Press
* Squats
* Pushups

## Technology Stack
* Python: Core logic and server-side processing.
* OpenCV: Real-time video processing.
* MediaPipe: Pose estimation for joint tracking.
* Flask: Web framework for serving the application.
* HTML/CSS: User interface for interacting with the system.

## How It Works
* Pose Detection: PocketSpotter leverages MediaPipe to detect key body landmarks (shoulders, elbows, wrists, etc.).
* Angle Calculation: It calculates joint angles to determine the current stage of the exercise (e.g., "up" or "down").
* Rep Detection: Reps are counted when the user completes a full range of motion with proper form.
* Feedback Mechanism: Based on the joint angles and timing, feedback is displayed to guide the user on form and pace.
* CSV Logging: Logs workout data (e.g., reps and timestamps) for future analysis.

## How to Run  

Follow these steps to set up and run the project locally:  

### 1. Clone the Repository  
First, clone the repository to your local machine:  
```bash
git clone git@github.com:kyle174/PocketSpotter.git
```
### 2. Create a Virtual Environment

It’s recommended to use a virtual environment to manage dependencies

```bash

python -m venv venv

```
Activate the virtual environment:

* On Windows:
```bash

venv\Scripts\activate

```

* On Mac:
```bash

source venv/bin/activate

```

### 3. Install Dependencies

Install all required Python packages using pip:

```bash

pip install flask mediapipe opencv-python numpy

```
### 4. Run the Flask Application

Start the Flask server to launch the application:

```bash

python main.py

```

### 5. Access the Application

Open your browser and navigate to:

```bash

http://127.0.0.1:5000/

```

