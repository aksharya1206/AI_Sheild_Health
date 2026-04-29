import ollama
import json
import re
from datetime import datetime

def analyze_medical_report(report_text):
    """
    Analyze medical report using Ollama AI with fallback option.
    Requires Ollama to be running with llama3.2 model.
    """
    prompt = f"""
    You are a medical AI assistant.

    Analyze the following medical report and provide:
    1. Simple Summary
    2. Key Findings (mark CRITICAL findings clearly)
    3. Possible Concerns
    4. Recommended Specialist
    5. Urgency Level (LOW/MEDIUM/HIGH/CRITICAL)
    6. Suggested Doctor Actions
    7. Recommended Treatments/Medications
    8. Follow-up Tests Needed
    9. Patient Advice

    Medical Report:
    {report_text}
    
    Format critical findings with [CRITICAL] prefix and normal findings with [NORMAL] prefix.
    """

    try:
        # Attempt to connect to Ollama
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        analysis = response['message']['content']
        # Enhance the analysis with HTML formatting
        return format_analysis_html(analysis)
    
    except (ConnectionError, ollama.ResponseError) as e:
        # Ollama not running - provide fallback analysis
        return get_fallback_analysis(report_text)
    except Exception as e:
        # Other errors
        raise Exception(f"Ollama Analysis Error: {str(e)}")


def format_analysis_html(analysis_text):
    """Format analysis text with HTML for better visualization"""
    # This will be rendered in the frontend
    return analysis_text


def get_fallback_analysis(report_text):
    """
    Provide an intelligent template-based analysis with risk indicators.
    This allows the system to continue functioning with basic analysis.
    """
    # Extract key health indicators from text
    critical_keywords = ['critical', 'severe', 'emergency', 'abnormal', 'high', 'positive', 'positive result']
    normal_keywords = ['normal', 'negative', 'healthy', 'within range', 'optimal']
    
    report_lower = report_text.lower()
    has_critical = any(kw in report_lower for kw in critical_keywords)
    
    summary = report_text[:300] if len(report_text) > 300 else report_text
    
    urgency_level = "HIGH" if has_critical else "MEDIUM"
    urgency_color = "#dc3545" if has_critical else "#ffc107"
    
    fallback = f"""
<div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #0056b3;">
        <strong style="color: #0056b3;">⚠️ TEMPLATE-BASED ANALYSIS</strong>
        <p style="margin: 5px 0; font-size: 12px; color: #666;">
            Full Ollama AI unavailable. Install Ollama for comprehensive AI analysis.
            <br/>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>

    <h3 style="color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px;">1. SUMMARY</h3>
    <p style="background: #f0f7ff; padding: 12px; border-left: 4px solid #0056b3; border-radius: 4px;">
        {summary}...
    </p>

    <h3 style="color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; margin-top: 20px;">2. KEY FINDINGS & RISK LEVEL</h3>
    <div style="background: #fff3cd; padding: 12px; border-left: 4px solid {urgency_color}; border-radius: 4px; margin-bottom: 10px;">
        <strong style="color: {urgency_color};">URGENCY LEVEL: {urgency_level}</strong>
        <p style="margin: 5px 0;">Report contains {'abnormal/critical' if has_critical else 'mostly normal'} findings requiring professional review.</p>
    </div>

    <div style="background: #f0f0f0; padding: 15px; border-radius: 4px; margin-bottom: 15px;">
        <p style="margin: 8px 0;"><span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">[NORMAL]</span> Report structure and basic parameters received</p>
        <p style="margin: 8px 0;"><span style="background: #ffc107; color: #333; padding: 2px 8px; border-radius: 3px; font-weight: bold;">[REVIEW]</span> Text extraction completed - requires physician interpretation</p>
        {f'<p style="margin: 8px 0;"><span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">[CRITICAL]</span> Abnormal findings detected - immediate review recommended</p>' if has_critical else ''}
    </div>

    <h3 style="color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; margin-top: 20px;">3. RECOMMENDED SPECIALIST</h3>
    <div style="background: #e7f3ff; padding: 12px; border-left: 4px solid #0056b3; border-radius: 4px;">
        <ul style="margin: 0; padding-left: 20px;">
            <li>Primary Care Physician / General Practitioner (Initial Assessment)</li>
            <li>Pathologist (Lab Results Review)</li>
            <li>Specialist review based on abnormal findings</li>
        </ul>
    </div>

    <h3 style="color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; margin-top: 20px;">4. DOCTOR RECOMMENDATIONS & ACTION PLAN</h3>
    <div style="background: #e8f5e9; padding: 12px; border-left: 4px solid #28a745; border-radius: 4px;">
        <strong style="color: #2e7d32;">✓ Recommended Doctor Actions:</strong>
        <ul style="margin: 10px 0; padding-left: 20px;">
            <li>Review all abnormal findings with patient</li>
            <li>Correlate lab results with clinical symptoms</li>
            <li>Assess need for immediate intervention vs. follow-up care</li>
            <li>Order additional tests if indicated</li>
            <li>Document findings in patient medical record</li>
        </ul>
    </div>

    <h3 style="color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; margin-top: 20px;">5. SUGGESTED TREATMENTS & MEDICATIONS</h3>
    <div style="background: #fff3e0; padding: 12px; border-left: 4px solid #ff9800; border-radius: 4px;">
        <strong style="color: #e65100;">💊 General Guidelines:</strong>
        <ul style="margin: 10px 0; padding-left: 20px;">
            <li><strong>Do NOT prescribe</strong> based on this template analysis alone</li>
            <li>Await full AI analysis with Ollama for specific medication recommendations</li>
            <li>Treatment must be individualized based on:</li>
            <ul style="padding-left: 20px;">
                <li>Complete patient history</li>
                <li>Current medications and allergies</li>
                <li>Comorbidities</li>
                <li>Patient preferences and contraindications</li>
            </ul>
            <li>Consider specialist consultation for complex cases</li>
        </ul>
    </div>

    <h3 style="color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; margin-top: 20px;">6. FOLLOW-UP TESTS NEEDED</h3>
    <div style="background: #f3e5f5; padding: 12px; border-left: 4px solid #9c27b0; border-radius: 4px;">
        <ul style="margin: 0; padding-left: 20px;">
            <li>Repeat relevant lab tests as indicated</li>
            <li>Imaging studies if abnormalities detected</li>
            <li>Specialist referral tests as needed</li>
            <li>Schedule follow-up appointment: 1-4 weeks depending on severity</li>
        </ul>
    </div>

    <h3 style="color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; margin-top: 20px;">7. PATIENT ADVICE</h3>
    <div style="background: #e0f2f1; padding: 12px; border-left: 4px solid #009688; border-radius: 4px;">
        <ul style="margin: 0; padding-left: 20px;">
            <li>Discuss all findings with your doctor</li>
            <li>Follow recommended lifestyle modifications</li>
            <li>Take medications exactly as prescribed</li>
            <li>Keep follow-up appointments</li>
            <li>Report any new symptoms immediately</li>
        </ul>
    </div>
</div>
    """
    return fallback