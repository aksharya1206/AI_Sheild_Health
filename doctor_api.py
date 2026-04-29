from flask import Blueprint, request, jsonify

doctor_bp = Blueprint('doctor', __name__)

doctors_db = {
    "Cardiologist": [
        {"name": "Dr. John Smith", "experience": "10 years", "rating": 4.8},
        {"name": "Dr. Sarah Johnson", "experience": "8 years", "rating": 4.7}
    ],
    "Neurologist": [
        {"name": "Dr. Michael Brown", "experience": "12 years", "rating": 4.9},
        {"name": "Dr. Emily Davis", "experience": "7 years", "rating": 4.6}
    ],
    "General Physician": [
        {"name": "Dr. Robert Wilson", "experience": "15 years", "rating": 4.8},
        {"name": "Dr. Lisa Anderson", "experience": "9 years", "rating": 4.7}
    ]
}

@doctor_bp.route('/get-doctors', methods=['POST'])
def get_doctors():
    data = request.json
    specialty = data.get('specialty', 'General Physician')

    if specialty in doctors_db:
        return jsonify({
            'specialty': specialty,
            'doctors': doctors_db[specialty]
        })

    return jsonify({
        'error': 'Specialty not found',
        'available_specialties': list(doctors_db.keys())
    }), 404

@doctor_bp.route('/specialties', methods=['GET'])
def get_specialties():
    return jsonify({
        'specialties': list(doctors_db.keys())
    })