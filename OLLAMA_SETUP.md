# 🚀 Ollama AI Setup Guide for SmartHealth

## Overview
SmartHealth uses **Ollama with Llama3.2** model for medical report analysis. Ollama must be running on your system for full AI features.

---

## ⚙️ Installation Steps (Windows)

### 1. Download Ollama
- Visit: https://ollama.com/download
- Click "Download for Windows"
- Installer will download (OllamaSetup.exe)

### 2. Install Ollama
- Run `OllamaSetup.exe`
- Follow the installation wizard
- Accept the default installation path (recommended)
- Ollama will be added to your system PATH

### 3. Pull the Llama3.2 Model
After installation, open **Command Prompt** or **PowerShell** and run:

```powershell
ollama pull llama3.2
```

This will download the Llama3.2 model (~5-10 minutes depending on internet speed).

### 4. Verify Installation
Check that the model is installed:

```powershell
ollama list
```

You should see output like:
```
NAME            ID              SIZE      MODIFIED
llama3.2:latest xxxxxxxxxx     4.7 GB    5 minutes ago
```

---

## ✅ Running Ollama

### Automatic Start
- Ollama runs automatically after installation
- Accessible at `http://localhost:11434`
- Look for the Ollama icon in your system tray

### Manual Start (if needed)
```powershell
ollama serve
```

### Check Service Status
```powershell
# Test connection
curl http://localhost:11434/api/tags

# Or in Python
python -c "import ollama; print(ollama.list())"
```

---

## 🧪 Test the Integration

### 1. Start SmartHealth App
```powershell
cd C:\Users\aksh3\Documents\AI_Sheild_Health
python app.py
```

### 2. Open in Browser
- Navigate to `http://localhost:5000`
- Go to "📊 AI Report Analyzer"
- Upload a test PDF
- Click "Analyze Report"

### 3. Expected Response
You should see AI-powered analysis with:
- Summary of findings
- Key findings
- Health concerns
- Recommended specialists
- Urgency level
- Clinical advice

---

## 🔧 Troubleshooting

### Issue: "Failed to connect to Ollama"

**Solution 1: Check if Ollama is running**
```powershell
# Windows - Look in system tray for Ollama icon
# Or test the connection:
curl http://localhost:11434/api/tags
```

**Solution 2: Model not installed**
```powershell
ollama list  # Check if llama3.2 is installed

# If missing, pull it:
ollama pull llama3.2
```

**Solution 3: Restart Ollama**
- Press Ctrl+C if running in terminal
- Wait 5 seconds
- Run `ollama serve` again

**Solution 4: Port conflict**
- Check if port 11434 is in use
- Restart your computer
- Update Ollama to latest version

---

## 📊 Using Fallback Mode

If Ollama is not available, SmartHealth provides **template-based analysis** which:
- ✓ Extracts text from PDFs
- ✓ Provides preliminary assessment
- ✓ Stores reports in history
- ✓ Allows doctor sharing
- ✗ Lacks full AI semantic analysis

To enable full AI features, ensure Ollama is running.

---

## 🖥️ System Requirements

- **OS:** Windows 7 or later (Windows 10/11 recommended)
- **RAM:** 8 GB minimum (16 GB+ recommended)
- **Disk:** 10 GB free (for model + applications)
- **Internet:** Required for initial model download

---

## 📚 Additional Resources

- **Ollama Website:** https://ollama.com
- **Available Models:** https://ollama.ai/library
- **Ollama GitHub:** https://github.com/ollama/ollama

---

## 🎯 Quick Commands Reference

```powershell
# Installation
ollama pull llama3.2

# Check installed models
ollama list

# Start service (manual)
ollama serve

# Test connection
curl http://localhost:11434/api/tags

# Run Ollama with a model directly
ollama run llama3.2 "Your prompt here"
```

---

## 📞 Support

If you experience issues:
1. Check the Ollama website FAQ: https://ollama.com
2. Review logs in your Documents folder
3. Ensure Windows Defender/Antivirus isn't blocking Ollama
4. Try a clean reinstall if all else fails

---

**Last Updated:** April 2026
**SmartHealth Version:** 1.0
**Supported Ollama Versions:** 0.1.x and later
