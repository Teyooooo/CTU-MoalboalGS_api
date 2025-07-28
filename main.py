from flask import Flask, jsonify, request
import os
from send_email import send_upcoming_deadline_emails_grouped
from attendance import initialize_attendance_date
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "Flask API is running"}), 200

@app.route("/send-reminders")
def manual_trigger():
    token = request.args.get("token")
    if token != os.getenv("SECRET_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    send_upcoming_deadline_emails_grouped()
    return jsonify({"status": "Grouped reminders sent"}), 200

@app.route("/init-attendance")
def trigger_attendance():
    token = request.args.get("token")
    if token != os.getenv("SECRET_TOKEN"):
        return jsonify({"error": "Unauthorized"}), 401

    date = initialize_attendance_date()
    return jsonify({"status": f"Attendance in {date} was initialize successfully"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)