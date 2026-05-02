
# SmartHealth AI Medical Report Analyzer

## 📋 Overview

SmartHealth is an advanced AI-powered medical report analysis platform that helps patients and doctors review medical reports with intelligent analysis, risk assessment, and actionable recommendations.

### Key Features

✅ **AI-Powered Analysis** - Uses Ollama (Llama3.2) for comprehensive medical insights  
✅ **Risk Level Indicators** - Color-coded findings (Green=Normal, Yellow=Review, Red=Critical)  
✅ **Doctor Recommendations** - AI-suggested treatments and medications  
✅ **Patient History Tracking** - Maintains complete medical history per patient  
✅ **Doctor-Patient Sharing** - Secure report sharing with medical professionals  
✅ **Smart Fallback** - Template-based analysis when Ollama unavailable  
✅ **Multi-Dashboard** - Separate views for patients, doctors, and admins  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama (optional, for full AI features)
- 2GB+ RAM
- 500MB disk space

### Installation

1. **Clone/Navigate to project directory**
```bash
cd C:\Users\aksh3\Documents\AI_Sheild_Health
```

2. **Install prerequisites**


3. **Run the application**
```bash
python app.py
```

4. **Open browser**
```
http://localhost:5000
```

---

## 🧠 Ollama AI Setup (Recommended)

For full AI-powered medical analysis with doctor recommendations:

### 1. Download Ollama
- Visit: https://ollama.com/download
- Download and run installer
- Install to default location

### 2. Pull the Model
```powershell
ollama pull llama3.2
```

### 3. Verify Installation
```powershell
ollama list
```
You should see `llama3.2` in the list.

### 4. Restart SmartHealth
The AI features will activate automatically.

---

## 📊 Application Features

### 1. **Patient Dashboard** (`/patient-dashboard`)
- View personal medical reports
- Track analysis history
- See health metrics
- Share reports with doctors
- Download reports

### 2. **AI Report Analyzer** (`/report-analyzer`)
- Upload PDF medical reports
- Get instant analysis with:
  - ✅ Risk level indicators
  - 📋 Summary of findings
  - 🔴 Critical alerts
  - 🟡 Items needing review
  - 🟢 Normal findings
- Doctor recommendations
- Suggested treatments
- Follow-up test recommendations

### 3. **Doctor Dashboard** (`/doctor-dashboard`)
- View shared patient reports
- Access complete medical history
- See risk assessments
- Add clinical notes
- Download reports
- Track multiple patients

### 4. **Home** (`/`)
- Overview of all features
- Quick access to main functions
- AI symptom checker
- Medicine authenticity scanner

---

## 📈 Analysis Output Explained

### Risk Levels (Color Coded)

🟢 **[NORMAL]** - Within normal range, no action needed
🟡 **[REVIEW]** - Requires physician interpretation
🔴 **[CRITICAL]** - Abnormal finding, requires immediate attention

### Doctor Recommendations Include

1. **Recommended Actions**
   - Review findings with patient
   - Correlate with symptoms
   - Determine intervention urgency
   - Order additional tests

2. **Treatment Suggestions**
   - Medication recommendations
   - Lifestyle modifications
   - Specialist referrals
   - Prevention strategies

3. **Follow-up Plan**
   - Recommended tests
   - Timeline for retesting
   - Follow-up appointment schedule
   - Monitoring parameters

---

## 🔐 Data Management

### Storage
- Patient data: `patient_data.json`
- Doctor shared reports: `doctor_reports.json`
- Uploaded files: `/uploads/` directory

### Privacy
- No data sent to cloud (local processing)
- Ollama runs locally on your machine
- Full control over patient information
- HIPAA-compliant when deployed properly

---

## ⚙️ Configuration

### Ollama Settings
- Model: `llama3.2`
- Host: `http://localhost:11434`
- Timeout: 30 seconds per request

### Flask Settings
- Debug: ON (development mode)
- Host: `127.0.0.1`
- Port: `5000`
- Auto-reload: Enabled

---

## 🐛 Troubleshooting

### Problem: "Failed to connect to Ollama"
**Solution:**
1. Ensure Ollama is installed: https://ollama.com/download
2. Run: `ollama pull llama3.2`
3. Restart SmartHealth
4. Try uploading a report

### Problem: Analysis is slow
**Solution:**
1. Ollama needs time to process (1-3 minutes for large reports)
2. Ensure sufficient RAM (8GB+ recommended)
3. Close other applications
4. Check system resources

### Problem: PDF text not extracting
**Solution:**
1. Ensure PDF is not image-only (OCR needed)
2. Try a different PDF
3. Verify PDF is readable/not corrupted

### Problem: Port 5000 already in use
**Solution:**
```python
# Edit app.py line: app.run(debug=True, port=5001)
```

---

## 🔄 API Endpoints

### Patient Routes
```
GET  /api/patient/history          - Get patient's report history
POST /api/patient/profile          - Save patient profile
```

### Analysis Routes
```
POST /analyze-medical-report        - Analyze report with Ollama
POST /share-report-to-doctor        - Share report with doctor
GET  /api/doctor/shared-reports     - Get doctor's shared reports
```

### UI Routes
```
GET  /                              - Home page
GET  /patient-dashboard             - Patient dashboard
GET  /doctor-dashboard              - Doctor dashboard
GET  /report-analyzer               - Report analyzer page
GET  /find-doctor                   - Find specialist
GET  /treatments                    - Treatment information
POST /predict                       - Symptom checker
POST /scan_medicine                 - Medicine scanner
```

---

## 📱 Supported Browsers

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)



## 🛠️ Development

### Adding New Features
1. Update Flask route in `app.py`
2. Create corresponding template in `Templates/`
3. Add styling to `static/style.css`
4. Add JavaScript functionality to `static/script.js`

### Modifying Analysis
Edit the prompt in `report_analyser.py` at line ~65

### Customizing AI Model
Change model name in `ollama_analyzer.py`:
```python
response = ollama.chat(
    model='your-model-name',  # e.g., 'mistral', 'neural-chat'
    messages=[...]
)
```

---

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│          User Browser (Frontend)        │
│  (HTML/CSS/JavaScript)                  │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST
┌──────────────────┴──────────────────────┐
│      Flask Web Server (app.py)          │
│  - Route Handlers                       │
│  - PDF Processing                       │
│  - JSON Data Management                 │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐    ┌──────▼────────┐
│  Ollama AI     │    │  Local Files  │
│ (llama3.2)     │    │   Storage     │
└────────────────┘    └───────────────┘
```

---

## 📝 Example Workflow

1. **Patient Upload**
   - Visit `/report-analyzer`
   - Upload medical PDF
   - System extracts text

2. **AI Analysis**
   - Ollama analyzes report
   - Generates findings with risk levels
   - Suggests doctor actions
   - Recommends treatments

3. **Review Results**
   - Patient sees color-coded analysis
   - Identifies critical findings
   - Views doctor recommendations

4. **Share with Doctor**
   - Select specialist from list
   - Enter doctor's name
   - Share report with history

5. **Doctor Review**
   - Doctor views in dashboard
   - Sees patient history
   - Adds clinical notes
   - Downloads report

---

## 🔑 Key Technologies

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript
- **AI:** Ollama with Llama3.2 model
- **PDF Processing:** PyMuPDF (fitz)
- **ML:** scikit-learn (for symptom checker)
- **Database:** JSON (local storage)

---



--## 🤝 Support

For issues or questions:
1. Check OLLAMA_SETUP.md for Ollama help
2. Review browser console for errors
3. Verify all dependencies installed
4. Restart the application

---

## 🎯 Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication & multi-user support
- [ ] PDF OCR for image-based documents
- [ ] Medical imaging analysis (X-ray, CT, MRI)
- [ ] Appointment booking system
- [ ] Prescription management
- [ ] Mobile app (iOS/Android)
- [ ] Integration with EHR systems
- [ ] Video consultation support
- [ ] Multi-language support

---

**Last Updated:** April 2026  
**Version:** 1.0  
**Status:** Production Ready
# AI_Sheild_Health
AI Health Shield is an AI-powered healthcare platform that analyzes medical reports, provides easy-to-understand health insights, recommends doctors, and offers patient and doctor dashboards for smarter, faster, and more accessible healthcare decisions.
e6bcc7261e5a5c40defcb79a0db3fef8128cac63
