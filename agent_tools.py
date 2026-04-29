"""
Agent Tools - Tool definitions for the Healthcare Agent
=========================================================
This module defines the tools that the agent can use to perform actions.
Each tool wraps existing functionality from the healthcare system.
"""

import json
import os
from typing import Dict, Any, List
from functools import wraps
import fitz
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import pickle

# Import existing modules
from ollama_analyzer import analyze_medical_report as ollama_analyze
from doctor_recommendation import doctors_db


# ============== TOOL FUNCTIONS ==============

def analyze_report_tool(report_text: str = None, file_path: str = None) -> Dict[str, Any]:
    """
    Tool to analyze medical reports using AI.
    Accepts either raw text or file path to PDF.
    Returns analysis with summary, findings, and recommendations.
    """
    try:
        if file_path:
            # Extract text from PDF
            text = ""
            pdf = fitz.open(file_path)
            for page in pdf:
                text += page.get_text()
            pdf.close()
            report_text = text
        
        if not report_text:
            return {"error": "No report text or file provided"}
        
        # Use existing Ollama analyzer
        analysis = ollama_analyze(report_text)
        
        return {
            "success": True,
            "analysis": analysis,
            "summary": "Report analyzed successfully",
            "timestamp": str(pd.Timestamp.now())
        }
    except Exception as e:
        return {"error": f"Failed to analyze report: {str(e)}"}


def find_doctors_tool(specialty: str = None, condition: str = None) -> Dict[str, Any]:
    """
    Tool to find doctors based on specialty or condition.
    Maps conditions to appropriate specialties and returns doctor recommendations.
    """
    # Condition to specialty mapping
    condition_map = {
        "heart": "Cardiologist",
        "cardiac": "Cardiologist",
        "chest pain": "Cardiologist",
        "brain": "Neurologist",
        "neurological": "Neurologist",
        "headache": "Neurologist",
        "seizure": "Neurologist",
        "diabetes": "Endocrinologist",
        "hormone": "Endocrinologist",
        "bone": "Orthopedic",
        "joint": "Orthopedic",
        "fracture": "Orthopedic",
        "skin": "Dermatologist",
        "rash": "Dermatologist",
        "lung": "Pulmonologist",
        "breathing": "Pulmonologist",
        "kidney": "Nephrologist",
        "liver": "Gastroenterologist",
        "stomach": "Gastroenterologist",
        "eye": "Ophthalmologist",
        "cancer": "Oncologist",
        "mental health": "Psychiatrist",
        "depression": "Psychiatrist",
        "anxiety": "Psychiatrist"
    }
    
    # Auto-detect specialty from condition
    if condition and not specialty:
        condition_lower = condition.lower()
        for key, spec in condition_map.items():
            if key in condition_lower:
                specialty = spec
                break
    
    if not specialty:
        specialty = "General Physician"
    
    # Get doctors from database
    doctors = doctors_db.get(specialty, doctors_db.get("General Physician", []))
    
    return {
        "success": True,
        "specialty": specialty,
        "doctors": doctors,
        "count": len(doctors)
    }


def check_symptoms_tool(symptoms: List[str]) -> Dict[str, Any]:
    """
    Tool to analyze symptoms and suggest possible conditions.
    Uses a trained ML model to predict potential diseases.
    """
    try:
        # Load the trained model
        if os.path.exists("disease_model.pkl"):
            model = pickle.load(open("disease_model.pkl", "rb"))
            
            # Load dataset for reference
            data = pd.read_csv("symptoms_dataset.csv")
            symptom_columns = [col for col in data.columns if col != "disease"]
            
            # Create symptom vector
            symptom_vector = []
            user_symptoms = [s.lower() for s in symptoms]
            
            for col in symptom_columns:
                # Check if any user symptom matches this column
                matched = any(col.replace("_", " ") in s or s in col for s in user_symptoms)
                symptom_vector.append(1 if matched else 0)
            
            # Make prediction
            if sum(symptom_vector) > 0:
                prediction = model.predict([symptom_vector])[0]
                confidence = 0.85  # Simplified confidence
                
                return {
                    "success": True,
                    "possible_condition": prediction,
                    "confidence": confidence,
                    "matching_symptoms": symptoms,
                    "recommendation": f"Consult a {get_recommended_specialty(prediction)} for further evaluation"
                }
        
        # Fallback if model not available
        return {
            "success": True,
            "possible_condition": "General checkup recommended",
            "confidence": 0.5,
            "matching_symptoms": symptoms,
            "recommendation": "Please consult a General Physician"
        }
    except Exception as e:
        return {"error": f"Failed to analyze symptoms: {str(e)}"}


def get_recommended_specialty(disease: str) -> str:
    """Map disease to recommended specialty"""
    disease_lower = disease.lower()
    
    specialty_map = {
        "heart": "Cardiologist",
        "diabetes": "Endocrinologist",
        "cancer": "Oncologist",
        "brain": "Neurologist",
        "lung": "Pulmonologist",
        "kidney": "Nephrologist",
        "liver": "Gastroenterologist",
        "bone": "Orthopedic",
        "skin": "Dermatologist",
        "eye": "Ophthalmologist"
    }
    
    for key, spec in specialty_map.items():
        if key in disease_lower:
            return spec
    return "General Physician"


def schedule_appointment_tool(doctor_name: str, specialty: str, 
                               patient_name: str, date: str = None, 
                               time: str = None, notes: str = "") -> Dict[str, Any]:
    """
    Tool to schedule an appointment with a doctor.
    Creates an appointment record in the system.
    """
    try:
        appointment = {
            "appointment_id": f"APT-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
            "doctor_name": doctor_name,
            "specialty": specialty,
            "patient_name": patient_name,
            "date": date or pd.Timestamp.now().strftime('%Y-%m-%d'),
            "time": time or "10:00 AM",
            "notes": notes,
            "status": "scheduled",
            "created_at": str(pd.Timestamp.now())
        }
        
        # Save to appointments file
        appointments_file = "appointments.json"
        appointments = []
        if os.path.exists(appointments_file):
            with open(appointments_file, 'r') as f:
                appointments = json.load(f)
        
        appointments.append(appointment)
        
        with open(appointments_file, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        return {
            "success": True,
            "appointment": appointment,
            "message": f"Appointment scheduled with {doctor_name} for {patient_name}"
        }
    except Exception as e:
        return {"error": f"Failed to schedule appointment: {str(e)}"}


def provide_advice_tool(condition: str = None, report_analysis: str = None) -> Dict[str, Any]:
    """
    Tool to provide health advice based on condition or report analysis.
    Uses AI to generate personalized recommendations.
    """
    try:
        prompt = f"""
        As a healthcare AI assistant, provide practical health advice for:
        
        Condition/Concern: {condition or 'General health'}
        
        Report Analysis: {report_analysis or 'No specific analysis available'}
        
        Provide:
        1. Lifestyle recommendations
        2. Dietary suggestions
        3. Warning signs to watch for
        4. When to seek immediate medical attention
        5. Follow-up recommendations
        
        Keep advice practical and actionable.
        """
        
        try:
            import ollama
            response = ollama.chat(
                model='llama3.2',
                messages=[{'role': 'user', 'content': prompt}]
            )
            advice = response['message']['content']
        except:
            # Fallback advice
            advice = get_fallback_advice(condition)
        
        return {
            "success": True,
            "advice": advice,
            "condition": condition
        }
    except Exception as e:
        return {"error": f"Failed to provide advice: {str(e)}"}


def get_fallback_advice(condition: str) -> str:
    """Provide fallback advice when AI is unavailable"""
    general_advice = """
    Health Advice:
    
    1. Maintain a balanced diet with plenty of fruits and vegetables
    2. Exercise regularly - at least 30 minutes daily
    3. Stay hydrated - drink 8 glasses of water daily
    4. Get adequate sleep - 7-8 hours per night
    5. Manage stress through meditation or relaxation techniques
    
    Please consult with your doctor for personalized advice.
    """
    return general_advice


def get_patient_history_tool(patient_id: str) -> Dict[str, Any]:
    """
    Tool to retrieve patient medical history.
    Returns previous reports, appointments, and health records.
    """
    try:
        patient_file = "patient_data.json"
        
        if os.path.exists(patient_file):
            with open(patient_file, 'r') as f:
                patients = json.load(f)
            
            if patient_id in patients:
                return {
                    "success": True,
                    "patient": patients[patient_id]
                }
        
        return {
            "success": False,
            "error": "Patient not found"
        }
    except Exception as e:
        return {"error": f"Failed to retrieve history: {str(e)}"}


def save_patient_data_tool(patient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool to save patient data and medical records.
    """
    try:
        patient_file = "patient_data.json"
        patients = {}
        
        if os.path.exists(patient_file):
            with open(patient_file, 'r') as f:
                patients = json.load(f)
        
        patients[patient_id] = {
            **data,
            "updated_at": str(pd.Timestamp.now())
        }
        
        with open(patient_file, 'w') as f:
            json.dump(patients, f, indent=2)
        
        return {
            "success": True,
            "message": "Patient data saved successfully"
        }
    except Exception as e:
        return {"error": f"Failed to save data: {str(e)}"}


# ============== TOOL REGISTRY ==============

# All available tools for the agent
AGENT_TOOLS = {
    "analyze_report": analyze_report_tool,
    "find_doctors": find_doctors_tool,
    "check_symptoms": check_symptoms_tool,
    "schedule_appointment": schedule_appointment_tool,
    "provide_advice": provide_advice_tool,
    "get_patient_history": get_patient_history_tool,
    "save_patient_data": save_patient_data_tool
}


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get tool definitions for agent prompt"""
    return [
        {
            "name": "analyze_report",
            "description": "Analyze medical reports (PDF or text) to extract findings, summaries, and recommendations",
            "parameters": {
                "report_text": "Optional raw text of the report",
                "file_path": "Optional path to PDF file"
            }
        },
        {
            "name": "find_doctors",
            "description": "Find and recommend doctors based on specialty or medical condition",
            "parameters": {
                "specialty": "Optional specific specialty (e.g., Cardiologist)",
                "condition": "Optional condition description (e.g., chest pain)"
            }
        },
        {
            "name": "check_symptoms",
            "description": "Analyze symptoms and predict possible conditions using ML",
            "parameters": {
                "symptoms": "List of symptoms the patient is experiencing"
            }
        },
        {
            "name": "schedule_appointment",
            "description": "Schedule an appointment with a doctor",
            "parameters": {
                "doctor_name": "Name of the doctor",
                "specialty": "Doctor's specialty",
                "patient_name": "Patient's name",
                "date": "Optional appointment date",
                "time": "Optional appointment time",
                "notes": "Optional notes for the appointment"
            }
        },
        {
            "name": "provide_advice",
            "description": "Generate personalized health advice based on condition or report",
            "parameters": {
                "condition": "Optional condition or concern",
                "report_analysis": "Optional previous report analysis"
            }
        },
        {
            "name": "get_patient_history",
            "description": "Retrieve patient's medical history and records",
            "parameters": {
                "patient_id": "Patient's unique identifier"
            }
        },
        {
            "name": "save_patient_data",
            "description": "Save or update patient medical records",
            "parameters": {
                "patient_id": "Patient's unique identifier",
                "data": "Dictionary of patient data to save"
            }
        }
    ]