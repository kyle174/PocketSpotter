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

## Usage
1. Ensure your webcam is connected and positioned to capture your full body.
2. Navigate to the app's homepage and select an exercise.
3. Follow the on-screen instructions to start your workout.
4. View real-time feedback, rep count, and pacing alerts on the screen.
