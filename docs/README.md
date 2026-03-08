# MedCore MCP Documentation

Welcome to the MedCore Hospital Management System documentation. This folder contains comprehensive guides and references for the entire system.

## 📚 Documentation Files

### Getting Started
- **[QUICK_START.md](QUICK_START.md)** - 3-step setup guide to get running in minutes
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed installation and configuration instructions

### System Overview
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - Architecture overview and component integration
- **[DATA_SUMMARY.md](DATA_SUMMARY.md)** - Database statistics and data distribution

### Reference
- **[SERVER_TOOLS_GUIDE.md](SERVER_TOOLS_GUIDE.md)** - Complete documentation of all 12 MCP tools
- **[EXAMPLE_QUERIES.md](EXAMPLE_QUERIES.md)** - 50+ example queries for the AI Assistant

### Development
- **[CHANGES_MADE.md](CHANGES_MADE.md)** - Summary of all changes and updates
- **[CORRECTIONS_APPLIED.md](CORRECTIONS_APPLIED.md)** - Critical fixes and corrections
- **[FINAL_CHECKLIST.md](FINAL_CHECKLIST.md)** - Production readiness checklist

---

## 🚀 Quick Navigation

### I want to...

**Get started quickly**
→ Read [QUICK_START.md](QUICK_START.md)

**Understand the system architecture**
→ Read [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)

**Learn about available tools**
→ Read [SERVER_TOOLS_GUIDE.md](SERVER_TOOLS_GUIDE.md)

**See example queries**
→ Read [EXAMPLE_QUERIES.md](EXAMPLE_QUERIES.md)

**Understand the database**
→ Read [DATA_SUMMARY.md](DATA_SUMMARY.md)

**Verify everything is working**
→ Read [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md)

**See what changed**
→ Read [CHANGES_MADE.md](CHANGES_MADE.md)

---

## 📋 System Overview

**MedCore MCP** is a hospital management system powered by:
- **Model Context Protocol (MCP)** - For tool-based data access
- **Groq AI** - For natural language processing
- **Streamlit** - For the web interface
- **SQLite** - For data persistence

### Key Features
- 🏥 **75 Patients** across 5 hospitals
- 👨‍⚕️ **35 Doctors** across 20+ specializations
- 🛏️ **70 Beds** with occupancy tracking
- 📅 **50 Appointments** with scheduling
- 🤖 **AI Assistant** for natural language queries
- 📊 **Real-time Dashboard** with hospital metrics

### 12 MCP Tools
1. get_all_patients
2. get_patient_by_id
3. search_patient
4. get_all_doctors
5. get_available_doctors
6. get_doctor_by_id
7. get_bed_availability
8. get_appointments
9. get_hospital_stats
10. get_patients_by_doctor
11. get_critical_patients
12. get_ward_summary

---

## 🔧 Configuration

### Environment Variables
```
GROQ_API_KEY = gsk_YOUR_API_KEY_HERE
```

### Database
- **Type**: SQLite3
- **Location**: `db/hospital.db`
- **Tables**: patients, doctors, beds, appointments, hospital_stats

### Model
- **Provider**: Groq
- **Model**: llama-3.3-70b-versatile
- **Tool Calling**: Enabled

---

## 📖 Reading Order

For first-time users, we recommend reading in this order:

1. **[QUICK_START.md](QUICK_START.md)** - Get the system running
2. **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - Understand the architecture
3. **[SERVER_TOOLS_GUIDE.md](SERVER_TOOLS_GUIDE.md)** - Learn about available tools
4. **[EXAMPLE_QUERIES.md](EXAMPLE_QUERIES.md)** - See what you can do
5. **[DATA_SUMMARY.md](DATA_SUMMARY.md)** - Understand the data

---

## 🎯 Common Tasks

### Setup the System
```bash
pip install -r requirements.txt
python db/setup_db.py
streamlit run app.py
```

### Verify Configuration
```bash
python verify_setup.py
python test_config.py
```

### Query the AI Assistant
```
"How many patients are currently admitted?"
"Show me all critical patients"
"Which wards have free beds?"
```

### Check Database
```bash
python -c "import sqlite3; c = sqlite3.connect('db/hospital.db'); print(c.execute('SELECT COUNT(*) FROM patients').fetchone())"
```

---

## 🔐 Security

- API keys stored in `.env.local` (not in git)
- Database is local SQLite (no remote exposure)
- MCP communication is stdio-based (no network exposure)
- Input validation on all tool parameters

---

## 📞 Support

For issues or questions:
1. Check the relevant documentation file
2. Review the troubleshooting section in [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. Check [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md) for verification steps
4. Review [EXAMPLE_QUERIES.md](EXAMPLE_QUERIES.md) for usage patterns

---

## 📊 Project Statistics

- **Documentation Files**: 9
- **Code Files**: 4 (app.py, ai_client.py, hospital_server.py, setup_db.py)
- **Utility Scripts**: 2 (verify_setup.py, test_config.py)
- **Database Records**: 75 patients + 35 doctors + 70 beds + 50 appointments
- **MCP Tools**: 12
- **Specializations**: 20+

---

## ✅ Status

**Production Ready** ✅

All components are integrated, tested, and documented. The system is ready for deployment.

---

**Last Updated**: March 8, 2026
**Version**: 1.0.0
**Status**: Production Ready
