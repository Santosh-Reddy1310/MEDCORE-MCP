# 🏥 MedCore MCP - Hospital Management AI System

A comprehensive hospital management system powered by Model Context Protocol (MCP), Groq AI, and Streamlit. Query hospital data using natural language with an intelligent AI assistant.

## ✨ Features

- **🤖 AI Assistant**: Natural language queries powered by Groq Mixtral 8x7B
- **📊 Real-time Dashboard**: Hospital metrics, bed occupancy, patient statistics
- **🛏️ Ward Management**: Live bed status and occupancy tracking
- **👨‍⚕️ Doctor Directory**: Search doctors by specialization and availability
- **👥 Patient Management**: Track patients, diagnoses, and assignments
- **📅 Appointment System**: Schedule and manage appointments
- **📈 Analytics**: Hospital statistics and trends

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API Key (get from [console.groq.com](https://console.groq.com))

### Installation

```bash
# 1. Clone/setup project
cd medcore-mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env.local with your Groq API key
echo "GROQ_API_KEY = gsk_YOUR_API_KEY_HERE" > .env.local

# 4. Setup database
python db/setup_db.py

# 5. Run the app
streamlit run app.py
```

Open browser to `http://localhost:8501`

## 📋 What's Included

### Data
- **75 Patients** across 5 hospitals with diverse medical conditions
- **35 Doctors** across 20+ specializations
- **70 Beds** across 5 wards with occupancy tracking
- **50 Appointments** with scheduling data
- **7 Days** of hospital statistics

### Components
- **Streamlit UI** - Interactive web interface
- **MCP Server** - 12 hospital management tools
- **Groq Integration** - AI-powered natural language processing
- **SQLite Database** - Persistent data storage

## 💬 Example Queries

Try these in the AI Assistant:

```
"How many patients are currently admitted?"
"Show me all critical patients"
"Which wards have free beds?"
"List available doctors"
"What is the bed occupancy rate?"
"Show me patients in ICU"
"Which doctors are in Cardiology?"
"Tell me about patient ID 5"
```

## 📁 Project Structure

```
medcore-mcp/
├── app.py                      # Streamlit web UI
├── requirements.txt            # Python dependencies
├── .env.local                  # Groq API key (create this)
├── verify_setup.py            # Setup verification script
│
├── db/
│   ├── setup_db.py            # Database initialization
│   └── hospital.db            # SQLite database (generated)
│
├── server/
│   └── hospital_server.py      # MCP server with 12 tools
│
├── client/
│   └── ai_client.py           # Groq integration + MCP client
│
└── docs/
    ├── QUICK_START.md         # 3-step setup guide
    ├── SETUP_GUIDE.md         # Detailed installation
    ├── SERVER_TOOLS_GUIDE.md  # Tool documentation
    ├── EXAMPLE_QUERIES.md     # 50+ example queries
    ├── DATA_SUMMARY.md        # Database statistics
    └── INTEGRATION_SUMMARY.md # Architecture overview
```

## 🛠️ MCP Tools (12 Available)

1. **get_all_patients** - List patients with filters
2. **get_patient_by_id** - Get patient details
3. **search_patient** - Search by name/diagnosis
4. **get_all_doctors** - List doctors with filters
5. **get_available_doctors** - Available doctors only
6. **get_doctor_by_id** - Get doctor details
7. **get_bed_availability** - Bed occupancy status
8. **get_appointments** - List appointments
9. **get_hospital_stats** - Hospital statistics
10. **get_patients_by_doctor** - Patients per doctor
11. **get_critical_patients** - Critical patients only
12. **get_ward_summary** - Ward-wise statistics

## 🎯 Dashboard Features

### Overview Metrics
- Active patient count
- Bed occupancy rate
- ICU patient tracking
- Available doctor count
- Free bed tracking
- Pending appointments

### AI Assistant
- Natural language queries
- Multi-turn conversations
- Context-aware responses
- Automatic data fetching

### Ward Status
- Real-time bed occupancy
- Ward-wise breakdown
- Occupancy visualization
- Free bed tracking

## 🔐 Configuration

### Environment Variables

Create `.env.local` in project root:

```
GROQ_API_KEY = gsk_YOUR_API_KEY_HERE
```

Get your API key from [console.groq.com](https://console.groq.com)

### Database

SQLite database automatically created at `db/hospital.db` with:
- 5 hospitals
- 75 patients
- 35 doctors
- 70 beds
- 50 appointments
- 7 days of statistics

## 📊 Database Schema

### Patients
- ID, Name, Age, Gender, Ward, Admission Date, Diagnosis, Doctor ID, Status, Blood Group, Contact

### Doctors
- ID, Name, Specialization, Department, Available, Contact, Experience Years

### Beds
- ID, Ward, Bed Number, Is Occupied, Patient ID

### Appointments
- ID, Patient ID, Doctor ID, Date, Time, Reason, Status

### Hospital Stats
- ID, Date, Total Admissions, Total Discharges, ICU Occupancy, Emergency Cases, Revenue

## 🧪 Verification

Run the setup verification script:

```bash
python verify_setup.py
```

This checks:
- ✅ .env.local configuration
- ✅ Dependencies installed
- ✅ Project files present
- ✅ Database populated
- ✅ Groq API configured
- ✅ MCP server syntax

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| "GROQ_API_KEY not found" | Create `.env.local` with your API key |
| "Database not found" | Run `python db/setup_db.py` |
| "Port 8501 in use" | Use `streamlit run app.py --server.port 8502` |
| "Import error" | Run `pip install -r requirements.txt` |
| "Connection refused" | Ensure MCP server can start (check Python path) |

## 📚 Documentation

- **QUICK_START.md** - 3-step setup guide
- **SETUP_GUIDE.md** - Detailed installation & troubleshooting
- **SERVER_TOOLS_GUIDE.md** - Complete tool documentation
- **EXAMPLE_QUERIES.md** - 50+ example queries
- **DATA_SUMMARY.md** - Database statistics
- **INTEGRATION_SUMMARY.md** - Architecture & integration details

## 🏗️ Architecture

```
Streamlit UI (app.py)
    ↓
Groq AI (mixtral-8x7b-32768)
    ↓
MCP Server (hospital_server.py)
    ↓
SQLite Database (hospital.db)
```

## 🔄 Data Flow

1. User enters query in Streamlit
2. Query sent to Groq AI
3. Groq determines which tools to call
4. MCP server executes tools
5. Database returns data
6. Groq generates natural language response
7. Response displayed in Streamlit

## 🎓 Learning Resources

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 📝 Example Workflow

```
User: "Show me all critical patients"
    ↓
Groq: Calls get_critical_patients tool
    ↓
MCP Server: Queries database
    ↓
Database: Returns 8 critical patients
    ↓
Groq: Formats response with patient details
    ↓
Streamlit: Displays formatted list
```

## 🤝 Contributing

Feel free to extend with:
- Additional hospital tools
- More patient data
- Advanced analytics
- Integration with real hospital systems

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🎉 Ready to Start?

```bash
# Verify setup
python verify_setup.py

# Run the application
streamlit run app.py
```

Then open `http://localhost:8501` in your browser!

---

**Built with ❤️ using MCP, Groq, and Streamlit**

For questions or issues, check the documentation files or review the example queries.
