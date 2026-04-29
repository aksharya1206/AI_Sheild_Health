from flask import request, jsonify

# Sample doctor database
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

def register_routes(app):
    @app.route('/get-doctors', methods=['POST'])
    def get_doctors():
        """Get doctor recommendations based on specialty"""
        data = request.json
        specialty = data.get('specialty', 'General Physician')
        
        if specialty in doctors_db:
            return jsonify({
                'specialty': specialty,
                'doctors': doctors_db[specialty]
            })
        else:
            return jsonify({
                'error': 'Specialty not found',
                'available_specialties': list(doctors_db.keys())
            }), 404

    @app.route('/specialties', methods=['GET'])
    def get_specialties():
        """Get list of available doctor specialties"""
        return jsonify({
            'specialties': list(doctors_db.keys())
        })
