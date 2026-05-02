import ollama
import json
import re
from datetime import datetime

def analyze_medical_report(report_text):
    """
    Enhanced Medical AI Analyzer.
    Categorizes findings into Red/Yellow/Green cards automatically.
    """
    # SYSTEM PROMPT: AI ko expert bananene ke liye
    prompt = f"""
    You are a Senior Medical Diagnostic Expert. Analyze this report text:
    "{report_text}"

    STRICT RULES:
    1. Every single finding must start with a tag: [CRITICAL], [WARNING], or [NORMAL].
    2. [CRITICAL] for dangerous levels (Red).
    3. [WARNING] for slightly high/low levels (Yellow).
    4. [NORMAL] for healthy levels (Green).
    5. For each finding, explain WHY it is categorized that way in 1 simple sentence.
    6. Mention the specific Specialist (e.g., Cardiologist, Nephrologist) the patient should see.
    7. NO long paragraphs. Use only bullet points.
    """

    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1} # Accuracy ke liye temperature low rakha hai
        )
        analysis = response['message']['content']
        
        # Boring text ko Colorful HTML Cards mein convert karna
        return format_analysis_html(analysis)
    
    except Exception as e:
        return get_fallback_analysis(report_text)

def format_analysis_html(analysis_text):
    """
    Begineer Friendly: Ye function AI ke text ko dhoond kar cards mein badal deta hai.
    """
    lines = analysis_text.split('\n')
    html_output = '<div class="analysis-container">'

    for line in lines:
        if not line.strip(): continue
        
        # Default settings
        card_class = "normal-card"
        icon = "✅"
        
        # Tag detection logic
        if "[CRITICAL]" in line:
            card_class = "critical-card"
            icon = "🚨"
            line = line.replace("[CRITICAL]", "<strong>URGENT:</strong>")
        elif "[WARNING]" in line:
            card_class = "warning-card"
            icon = "⚠️"
            line = line.replace("[WARNING]", "<strong>ATTENTION:</strong>")
        elif "[NORMAL]" in line:
            card_class = "normal-card"
            icon = "🩺"
            line = line.replace("[NORMAL]", "<strong>STABLE:</strong>")

        html_output += f"""
        <div class="analysis-card {card_class}" style="
            padding: 15px; 
            margin-bottom: 10px; 
            border-radius: 10px; 
            border-left: 8px solid; 
            display: flex; 
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            background: white;">
            <span style="font-size: 1.5rem; margin-right: 15px;">{icon}</span>
            <span style="font-family: sans-serif; color: #333;">{line}</span>
        </div>"""

    html_output += '</div>'
    return html_output

def get_fallback_analysis(report_text):
    # Purana fallback code yahan rehne dein...
    return "Ollama is offline. Please start Ollama and pull llama3.2."
 