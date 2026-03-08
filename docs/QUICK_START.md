# MedCore MCP - Quick Start

## 🚀 Get Running in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup Database
```bash
python db/setup_db.py
```

### Step 3: Run the App
```bash
streamlit run app.py
```

Open browser to `http://localhost:8501`

---

## 📋 What You Get

✅ **75 Patients** across 5 hospitals with diverse conditions
✅ **35 Doctors** across 20+ specializations  
✅ **70 Beds** across 5 wards with occupancy tracking
✅ **50 Appointments** with scheduling data
✅ **12 MCP Tools** for hospital data queries
✅ **AI Assistant** powered by Groq llama-3.3-70b-versatile

---

## 🎯 Key Features

### Dashboard
- Real-time hospital metrics
- Bed occupancy visualization
- Critical patient alerts
- Doctor availability status

### AI Assistant
- Natural language queries
- Automatic data fetching
- Multi-turn conversations
- Context-aware responses

### Ward Status
- Live bed occupancy
- Ward-wise breakdown
- Occupancy rate visualization
- Free bed tracking

---

## 💬 Try These Queries

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

---

## 📁 Project Structure

```
medcore-mcp/
├── app.py                    # Streamlit UI
├── db/setup_db.py           # Database setup
├── server/hospital_server.py # MCP server
├── client/ai_client.py      # Groq integration
├── .env.local               # API key
├── requirements.txt         # Dependencies
└── docs/                    # Documentation
```

---

## 🔑 Environment Setup

Create `.env.local` with your Groq API key:

```
GROQ_API_KEY = gsk_YOUR_API_KEY_HERE
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "GROQ_API_KEY not found" | Check `.env.local` exists with correct key |
| "Database not found" | Run `python db/setup_db.py` |
| "Port 8501 in use" | Use `streamlit run app.py --server.port 8502` |
| "Import error" | Run `pip install -r requirements.txt` |

---

## 📊 Database Stats

- **Patients:** 75 (60 admitted, 10 critical, 4 post-op, 1 discharged)
- **Doctors:** 35 (28 available, 7 unavailable)
- **Beds:** 70 total (55 occupied, 15 free)
- **Wards:** 5 (Ward A, B, C, D, ICU)
- **Appointments:** 50 (various statuses)

---

## 🎓 Learn More

- `docs/SETUP_GUIDE.md` - Detailed setup instructions
- `docs/SERVER_TOOLS_GUIDE.md` - All 12 MCP tools documented
- `docs/EXAMPLE_QUERIES.md` - 50+ example queries
- `docs/DATA_SUMMARY.md` - Database statistics

---

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Setup database
3. ✅ Configure `.env.local`
4. ✅ Run `streamlit run app.py`
5. ✅ Try the quick queries
6. ✅ Explore the AI Assistant

---

## 📞 Support

- Check documentation files in `docs/`
- Review example queries
- Test with quick query buttons
- Check server logs for errors

---

**Happy exploring! 🏥**
