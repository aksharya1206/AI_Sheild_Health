from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import cv2
from PIL import Image
import os
from werkzeug.utils import secure_filename
import fitz
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Import route registration functions
from report_analyser import register_routes as register_report_routes
from doctor_recommendation import register_routes as register_doctor_routes

# Register routes
register_report_routes(app)
register_doctor_routes(app)

# Patient data storage (JSON-based for simplicity)
PATIENT_DATA_FILE = 'patient_data.json'
REPORTS_DATA_FILE = 'reports_data.json'
DOCTOR_REPORTS_FILE = 'doctor_reports.json'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper functions for file operations
def load_json_file(filename):
    """Load JSON file, return empty dict if not exists"""
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json_file(filename, data):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    text = ""
    pdf = fitz.open(filepath)
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text

# Training data for disease prediction
data = {
    "fever": [1,1,0,0],
    "cough": [1,0,1,0],
    "fatigue": [1,1,1,0],
    "headache": [0,1,0,0],
    "bodypain": [1,1,0,0],
    "disease": ["Flu","Viral Fever","Cold","Healthy"]
}

df = pd.DataFrame(data)
X = df[["fever","cough","fatigue","headache","bodypain"]]
y = df["disease"]

model = DecisionTreeClassifier()
model.fit(X,y)


# ========== ROUTES ==========

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/find-doctor")
def find_doctor():
    return render_template("find_doctor.html")


@app.route("/treatments")
def treatments():
    return render_template("treatments.html")


@app.route("/patient-dashboard")
def patient_dashboard():
    patient_data = load_json_file(PATIENT_DATA_FILE)
    reports = patient_data.get('reports', [])
    return render_template("patient_dashboard.html", 
                         patient=patient_data.get('profile', {}),
                         reports=reports[-5:] if reports else [],
                         appointments=patient_data.get('appointments', []))


@app.route("/doctor-dashboard")
def doctor_dashboard():
    doctor_data = load_json_file(DOCTOR_REPORTS_FILE)
    reports = doctor_data.get('reports', [])
    return render_template("doctor_dashboard.html",
                         doctor={"name": "AI Analysis System", "specialty": "General"},
                         reports=reports[-5:] if reports else [])


@app.route("/predict", methods=["POST"])
def predict():
    fever = int(request.form.get("fever", 0))
    cough = int(request.form.get("cough", 0))
    fatigue = int(request.form.get("fatigue", 0))
    headache = int(request.form.get("headache", 0))
    bodypain = int(request.form.get("bodypain", 0))

    prediction = model.predict([[fever,cough,fatigue,headache,bodypain]])
    return jsonify({"disease": prediction[0]})


@app.route("/scan_medicine", methods=["POST"])
def scan_medicine():
    file = request.files["image"]
    img = Image.open(file)
    img = np.array(img)
    height, width = img.shape[:2]

    if height > 500:
        result = "Medicine looks authentic"
    else:
        result = "Possible fake medicine"

    return jsonify({
        "result": result,
        "expiry_warning": "Check expiry date on package",
        "side_effects": "May cause nausea or dizziness"
    })


# ========== PATIENT ROUTES ==========

@app.route('/api/patient/profile', methods=['POST'])
def save_patient_profile():
    """Save patient profile"""
    data = request.json
    patient_data = load_json_file(PATIENT_DATA_FILE)
    patient_data['profile'] = data
    save_json_file(PATIENT_DATA_FILE, patient_data)
    return jsonify({'success': True, 'message': 'Profile saved'})


@app.route('/api/patient/history', methods=['GET'])
def get_patient_history():
    """Get patient medical history"""
    patient_data = load_json_file(PATIENT_DATA_FILE)
    reports = patient_data.get('reports', [])
    return jsonify({'history': reports})


# ========== REPORT ANALYSIS ROUTES ==========

@app.route('/report-analyzer')
def report_analyzer():
    return render_template('report_analyser.html')


@app.route('/analyze-report', methods=['POST'])
def analyze_report():
    """Analyze medical report using Ollama AI"""
    from ollama_analyzer import analyze_medical_report
    
    if 'report' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['report']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    patient_id = request.form.get('patient_id', 'default')
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(filepath)

    # Analyze using Ollama
    analysis = analyze_medical_report(extracted_text)

    # Save report to patient history
    patient_data = load_json_file(PATIENT_DATA_FILE)
    if 'reports' not in patient_data:
        patient_data['reports'] = []
    
    report_entry = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'filename': filename,
        'summary': analysis[:200] + '...' if len(analysis) > 200 else analysis,
        'full_analysis': analysis,
        'extracted_text': extracted_text
    }
    patient_data['reports'].append(report_entry)
    save_json_file(PATIENT_DATA_FILE, patient_data)

    return jsonify({
        'analysis': analysis,
        'extracted_text': extracted_text,
        'filename': filename,
        'success': True
    })


# ========== DOCTOR-PATIENT SHARING ROUTES ==========
# Note: Doctor sharing routes are registered via report_analyser.register_routes()
# This includes /share-report-to-doctor and /api/doctor/shared-reports endpoints


@app.route('/api/doctor/shared-reports', methods=['GET'])
def get_doctor_reports():
    """Get all reports shared with doctor"""
    doctor_data = load_json_file(DOCTOR_REPORTS_FILE)
    reports = doctor_data.get('reports', [])
    return jsonify({'reports': reports})


if __name__ == "__main__":
    app.run(debug=True)