from flask import render_template, session, redirect, url_for
from app import app

@app.route('/patient-dashboard')
def patient_dashboard():
    # Optional: Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))

    # Sample patient data
    patient_data = {
        'name': 'Akshita',
        'age': 19,
        'blood_group': 'B+',
        'appointments': [
            {
                'doctor': 'Dr. John Smith',
                'specialty': 'Cardiologist',
                'date': '2026-04-30',
                'time': '5:30 PM',
                'status': 'Upcoming'
            },
            {
                'doctor': 'Dr. Sarah Johnson',
                'specialty': 'Dermatologist',
                'date': '2026-04-20',
                'time': '4:00 PM',
                'status': 'Completed'
            }
        ],
        'reports': [
            {
                'name': 'Blood Test Report',
                'date': '2026-04-15',
                'summary': 'Hemoglobin normal, Vitamin D slightly low.'
            },
            {
                'name': 'ECG Report',
                'date': '2026-04-10',
                'summary': 'Normal sinus rhythm.'
            }
        ],
        'health_score': 82
    }

    return render_template('patient_dashboard.html', patient=patient_data)