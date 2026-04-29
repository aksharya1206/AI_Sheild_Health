from flask import render_template, request, jsonify
from ollama_analyzer import analyze_medical_report
import os
from werkzeug.utils import secure_filename
import fitz
import json
from datetime import datetime

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PATIENT_DATA_FILE = 'patient_data.json'
DOCTOR_REPORTS_FILE = 'doctor_reports.json'


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ''
    pdf = fitz.open(file_path)
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text


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


def register_routes(app):
    @app.route('/report-analyzer-view')
    def report_analyzer_view():
        return render_template('report_analyser.html')

    @app.route('/analyze-medical-report', methods=['POST'])
    def analyze_medical_report_endpoint():
        """Analyze medical report using Ollama AI with patient history"""
        
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

        # Get patient history for context
        patient_data = load_json_file(PATIENT_DATA_FILE)
        patient_history = patient_data.get('reports', [])
        
        # Build context with patient history
        history_context = ""
        if patient_history:
            history_context = "\n\nPATIENT MEDICAL HISTORY:\n"
            for i, report in enumerate(patient_history[-3:]):  # Last 3 reports
                history_context += f"\n- Previous Report {i+1}: {report.get('summary', 'N/A')}"

        # Create comprehensive prompt
        full_prompt = f"""
You are a medical AI assistant analyzing a medical report with patient context.

PATIENT MEDICAL HISTORY:
{history_context}

CURRENT MEDICAL REPORT TO ANALYZE:
{extracted_text}

Please provide a comprehensive analysis including:
1. Summary of current findings
2. Abnormal findings
3. Possible health concerns based on history and current report
4. Recommended specialists
5. Suggested follow-up tests
6. Urgency level (Low/Medium/High/Critical)
7. Clinical recommendations
        """

        # Analyze using Ollama
        try:
            analysis = analyze_medical_report(full_prompt)
        except Exception as e:
            error_msg = str(e)
            if "Failed to connect" in error_msg or "ConnectionError" in error_msg:
                return jsonify({
                    'error': 'Ollama AI service is not running',
                    'details': 'Please ensure Ollama is installed and running',
                    'fallback': 'Template-based analysis will be used if you retry'
                }), 503
            return jsonify({'error': f'Analysis failed: {error_msg}'}), 500

        # Save report to patient history
        if 'reports' not in patient_data:
            patient_data['reports'] = []
        
        report_entry = {
            'id': len(patient_data['reports']),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename': filename,
            'summary': analysis[:200] + '...' if len(analysis) > 200 else analysis,
            'full_analysis': analysis,
            'extracted_text': extracted_text,
            'patient_id': patient_id
        }
        patient_data['reports'].append(report_entry)
        save_json_file(PATIENT_DATA_FILE, patient_data)

        return jsonify({
            'analysis': analysis,
            'extracted_text': extracted_text,
            'filename': filename,
            'report_id': report_entry['id'],
            'success': True
        })

    @app.route('/share-report-to-doctor', methods=['POST'])
    def share_report_to_doctor():
        """Share report with doctor including patient history"""
        
        data = request.json
        report_id = data.get('report_id')
        doctor_name = data.get('doctor_name', 'Not Specified')
        patient_info = data.get('patient_info', {})

        doctor_data = load_json_file(DOCTOR_REPORTS_FILE)
        if 'reports' not in doctor_data:
            doctor_data['reports'] = []

        # Get the report from patient data
        patient_data = load_json_file(PATIENT_DATA_FILE)
        reports = patient_data.get('reports', [])
        
        if isinstance(report_id, int) and report_id < len(reports):
            shared_report = reports[report_id].copy()
            
            # Include relevant patient history
            shared_report['patient_history'] = reports[max(0, report_id-3):report_id]
            shared_report['shared_with_doctor'] = doctor_name
            shared_report['patient_info'] = patient_info
            shared_report['shared_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            shared_report['prescription'] = shared_report.get('prescription', None)
            shared_report['treatment_plan'] = shared_report.get('treatment_plan', None)
            shared_report['doctor_notes'] = shared_report.get('doctor_notes', None)
            
            doctor_data['reports'].append(shared_report)
            save_json_file(DOCTOR_REPORTS_FILE, doctor_data)
            
            return jsonify({
                'success': True,
                'message': f'Report shared with {doctor_name}',
                'patient_history_included': len(shared_report.get('patient_history', []))
            })
        
        return jsonify({'error': 'Report not found'}), 404

    @app.route('/api/doctor/prescriptions', methods=['GET'])
    def get_doctor_prescriptions():
        """Return all shared doctor prescriptions and treatment plans."""
        doctor_data = load_json_file(DOCTOR_REPORTS_FILE)
        reports = doctor_data.get('reports', [])
        return jsonify({'prescriptions': reports})

    @app.route('/api/doctor/save-prescription', methods=['POST'])
    def save_doctor_prescription():
        data = request.json
        index = data.get('index')
        prescription = data.get('prescription')
        treatment_plan = data.get('treatment_plan')
        doctor_notes = data.get('doctor_notes')

        doctor_data = load_json_file(DOCTOR_REPORTS_FILE)
        reports = doctor_data.get('reports', [])

        if isinstance(index, int) and 0 <= index < len(reports):
            reports[index]['prescription'] = prescription
            reports[index]['treatment_plan'] = treatment_plan
            reports[index]['doctor_notes'] = doctor_notes
            save_json_file(DOCTOR_REPORTS_FILE, doctor_data)
            return jsonify({'success': True, 'message': 'Prescription saved successfully'})

        return jsonify({'error': 'Report index not found'}), 404
