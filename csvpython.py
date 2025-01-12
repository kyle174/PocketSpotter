import csv
import os

csv_file = "exercise_reps_test.csv"

def initialize_csv(file_path):
    if not os.path.exists(file_path):
        # Create CSV and write headers
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Exercise", "Rep Number", "Timestamp"])

def log_rep_to_csv(file_path, exercise, rep_number, timestamp):
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([exercise, rep_number, timestamp,])


