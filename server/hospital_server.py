import sqlite3
import os
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "hospital.db")

# Ensure absolute path
if not os.path.isabs(DB_PATH):
    DB_PATH = os.path.abspath(DB_PATH)

app = Server("medcore-hospital-server")


def get_conn():
    """Get database connection with error handling."""
    try:
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file not found: {DB_PATH}. Please run 'python db/setup_db.py' to initialize.")
        
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {str(e)}")


def rows_to_list(rows):
    """Convert database rows to list of dictionaries."""
    return [dict(row) for row in rows]


# ─────────────────────────────────────────────
# TOOL DEFINITIONS
# ─────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_all_patients",
            description="Get all patients in the hospital. Optionally filter by ward (Ward A, Ward B, Ward C, Ward D, ICU) or status (admitted, critical, post-op, discharged).",
            inputSchema={
                "type": "object",
                "properties": {
                    "ward":   {"type": "string", "description": "Filter by ward name"},
                    "status": {"type": "string", "description": "Filter by patient status"},
                    "limit": {"type": "integer", "description": "Limit number of results (default: 50)"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get_patient_by_id",
            description="Get full details of a single patient by their ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "integer", "description": "The patient's ID"},
                },
                "required": ["patient_id"],
            },
        ),
        types.Tool(
            name="search_patient",
            description="Search patients by name or diagnosis keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Name or diagnosis keyword to search"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_all_doctors",
            description="Get all doctors. Optionally filter by specialization or department. For only available doctors, use get_available_doctors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "specialization": {"type": "string", "description": "Filter by specialization (e.g., Cardiology, Pediatrics)"},
                    "department": {"type": "string", "description": "Filter by department name"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get_available_doctors",
            description="Get all doctors currently available for consultation.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_bed_availability",
            description="Get bed occupancy status. Optionally filter by ward. Returns occupied and free bed counts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ward": {"type": "string", "description": "Filter by ward name"},
                },
            },
        ),
        types.Tool(
            name="get_appointments",
            description="Get appointments. Optionally filter by date (YYYY-MM-DD) or status (scheduled, completed, cancelled).",
            inputSchema={
                "type": "object",
                "properties": {
                    "date":   {"type": "string", "description": "Filter by date (YYYY-MM-DD)"},
                    "status": {"type": "string", "description": "Filter by appointment status"},
                    "limit": {"type": "integer", "description": "Limit number of results (default: 50)"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get_hospital_stats",
            description="Get hospital statistics summary including total patients, bed occupancy rate, ICU status, admissions trend, and recent daily stats.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_patients_by_doctor",
            description="Get all patients currently assigned to a specific doctor by doctor ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_id": {"type": "integer", "description": "The doctor's ID"},
                },
                "required": ["doctor_id"],
            },
        ),
        types.Tool(
            name="get_critical_patients",
            description="Get all critical patients in the hospital.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_doctor_by_id",
            description="Get full details of a doctor by their ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_id": {"type": "integer", "description": "The doctor's ID"},
                },
                "required": ["doctor_id"],
            },
        ),
        types.Tool(
            name="get_ward_summary",
            description="Get summary of all wards with occupancy and patient count.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_doctor_by_name",
            description="Get doctor details by full or partial doctor name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Doctor name or partial match"},
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="get_doctors_by_experience",
            description="Get doctors with at least a minimum number of years of experience. Optional filters by department/specialization and availability.",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_years": {"type": "integer", "description": "Minimum years of experience"},
                    "department": {"type": "string", "description": "Optional department filter"},
                    "specialization": {"type": "string", "description": "Optional specialization filter"},
                    "available_only": {
                        "anyOf": [
                            {"type": "boolean"},
                            {"type": "string", "enum": ["true", "false", "1", "0", "yes", "no"]}
                        ],
                        "description": "Optional availability filter"
                    },
                },
                "required": ["min_years"],
            },
        ),
        types.Tool(
            name="get_appointments_by_doctor_name",
            description="Get appointments for a doctor by doctor name. Optional date and status filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string", "description": "Doctor full/partial name"},
                    "date": {"type": "string", "description": "Optional date filter (YYYY-MM-DD)"},
                    "status": {"type": "string", "description": "Optional status filter"},
                    "limit": {"type": "integer", "description": "Limit number of rows (default: 50)"},
                },
                "required": ["doctor_name"],
            },
        ),
        types.Tool(
            name="get_appointments_by_patient_id",
            description="Get appointments for a given patient ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {"type": "integer", "description": "Patient ID"},
                    "limit": {"type": "integer", "description": "Limit number of rows (default: 50)"},
                },
                "required": ["patient_id"],
            },
        ),
        types.Tool(
            name="get_recent_admissions",
            description="Get patients admitted in the last N days.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days lookback (default: 3)"},
                    "ward": {"type": "string", "description": "Optional ward filter"},
                    "limit": {"type": "integer", "description": "Limit number of rows (default: 50)"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get_department_overview",
            description="Get operational overview by department including doctor counts, available doctors, and active patient load.",
            inputSchema={
                "type": "object",
                "properties": {
                    "department": {"type": "string", "description": "Optional department filter"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get_appointments_summary",
            description="Get appointment utilization metrics with counts by status and overall completion/cancellation rate.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_patients_by_condition",
            description="Get patients by diagnosis keyword or condition pattern (e.g., cancer, cardiac, respiratory, trauma).",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "Condition keyword to search in diagnosis"},
                    "status": {"type": "string", "description": "Optional status filter"},
                    "limit": {"type": "integer", "description": "Limit number of rows (default: 50)"},
                },
                "required": ["condition"],
            },
        ),
        types.Tool(
            name="get_patients_by_doctor_name",
            description="Get all patients currently being treated by a doctor specified by name. Use this when asking 'which patients is Dr. X treating?' or similar queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string", "description": "Doctor name (full or partial match)"},
                    "status": {"type": "string", "description": "Optional patient status filter (admitted, critical, post-op, discharged)"},
                    "limit": {"type": "integer", "description": "Limit number of rows (default: 50)"},
                },
                "required": ["doctor_name"],
            },
        ),
        types.Tool(
            name="get_patients_by_department",
            description="Get all patients being treated by doctors in a specific department. Use for queries like 'show me Cardiology patients' or 'patients in Oncology'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "department": {"type": "string", "description": "Department name (e.g., Cardiology, Oncology, Neurology, Pediatrics, Surgery, Emergency)"},
                    "status": {"type": "string", "description": "Optional patient status filter"},
                    "limit": {"type": "integer", "description": "Limit number of rows (default: 50)"},
                },
                "required": ["department"],
            },
        ),
        types.Tool(
            name="get_todays_appointments",
            description="Get all appointments scheduled for today. Optionally filter by status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Optional status filter (scheduled, completed, cancelled)"},
                },
                "required": [],
            },
        ),
    ]


# ─────────────────────────────────────────────
# TOOL HANDLERS
# ─────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    conn = get_conn()
    cursor = conn.cursor()
    result = {}

    try:
        if name == "get_all_patients":
            query = "SELECT * FROM patients WHERE 1=1"
            params = []
            if arguments.get("ward"):
                query += " AND ward = ?"
                params.append(arguments["ward"])
            if arguments.get("status"):
                query += " AND status = ?"
                params.append(arguments["status"])
            limit = arguments.get("limit", 50)
            query += f" LIMIT {limit}"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = {"patients": rows_to_list(rows), "total": len(rows)}

        elif name == "get_patient_by_id":
            cursor.execute(
                "SELECT p.*, d.name as doctor_name, d.specialization FROM patients p LEFT JOIN doctors d ON p.doctor_id = d.id WHERE p.id = ?",
                (arguments["patient_id"],)
            )
            row = cursor.fetchone()
            result = dict(row) if row else {"error": "Patient not found"}

        elif name == "search_patient":
            q = f"%{arguments['query']}%"
            cursor.execute(
                "SELECT p.*, d.name as doctor_name FROM patients p LEFT JOIN doctors d ON p.doctor_id = d.id WHERE p.name LIKE ? OR p.diagnosis LIKE ?",
                (q, q)
            )
            rows = cursor.fetchall()
            result = {"matches": rows_to_list(rows), "count": len(rows)}

        elif name == "get_all_doctors":
            query = "SELECT * FROM doctors WHERE 1=1"
            params = []
            if arguments.get("specialization"):
                query += " AND specialization = ?"
                params.append(arguments["specialization"])
            if arguments.get("department"):
                query += " AND department = ?"
                params.append(arguments["department"])
            cursor.execute(query, params)
            result = {"doctors": rows_to_list(cursor.fetchall())}

        elif name == "get_available_doctors":
            cursor.execute("SELECT * FROM doctors WHERE available = 1 ORDER BY specialization")
            result = {"available_doctors": rows_to_list(cursor.fetchall())}

        elif name == "get_doctor_by_id":
            cursor.execute("SELECT * FROM doctors WHERE id = ?", (arguments["doctor_id"],))
            row = cursor.fetchone()
            result = dict(row) if row else {"error": "Doctor not found"}

        elif name == "get_bed_availability":
            if arguments.get("ward"):
                cursor.execute(
                    "SELECT ward, bed_number, is_occupied, patient_id FROM beds WHERE ward = ? ORDER BY bed_number",
                    (arguments["ward"],)
                )
                beds = rows_to_list(cursor.fetchall())
                occupied = sum(1 for b in beds if b["is_occupied"])
                result = {
                    "ward": arguments["ward"],
                    "total": len(beds),
                    "occupied": occupied,
                    "free": len(beds) - occupied,
                    "occupancy_rate": round((occupied / len(beds)) * 100, 1) if beds else 0,
                    "beds": beds,
                }
            else:
                cursor.execute(
                    "SELECT ward, COUNT(*) as total, SUM(is_occupied) as occupied FROM beds GROUP BY ward ORDER BY ward"
                )
                wards = rows_to_list(cursor.fetchall())
                for w in wards:
                    w["free"] = w["total"] - (w["occupied"] or 0)
                    w["occupancy_rate"] = round((w["occupied"] / w["total"]) * 100, 1) if w["total"] else 0
                result = {"ward_summary": wards}

        elif name == "get_appointments":
            query = """
                SELECT a.*, p.name as patient_name, d.name as doctor_name
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.id
                LEFT JOIN doctors d ON a.doctor_id = d.id
                WHERE 1=1
            """
            params = []
            if arguments.get("date"):
                query += " AND a.date = ?"
                params.append(arguments["date"])
            if arguments.get("status"):
                query += " AND a.status = ?"
                params.append(arguments["status"])
            limit = arguments.get("limit", 50)
            query += f" ORDER BY a.date, a.time LIMIT {limit}"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = {"appointments": rows_to_list(rows), "total": len(rows)}

        elif name == "get_hospital_stats":
            cursor.execute("SELECT COUNT(*) as total FROM patients WHERE status != 'discharged'")
            active = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as total, SUM(is_occupied) as occupied FROM beds")
            beds = cursor.fetchone()
            total_beds = beds["total"]
            occupied_beds = beds["occupied"] or 0

            cursor.execute("SELECT COUNT(*) as icu FROM patients WHERE ward = 'ICU' AND status = 'critical'")
            icu = cursor.fetchone()["icu"]

            cursor.execute("SELECT COUNT(*) as total FROM doctors WHERE available = 1")
            avail_docs = cursor.fetchone()["total"]

            cursor.execute("SELECT * FROM hospital_stats ORDER BY date DESC LIMIT 7")
            daily = rows_to_list(cursor.fetchall())

            cursor.execute("SELECT COUNT(*) as critical FROM patients WHERE status = 'critical'")
            critical = cursor.fetchone()["critical"]

            result = {
                "summary": {
                    "active_patients": active,
                    "critical_patients": critical,
                    "total_beds": total_beds,
                    "occupied_beds": occupied_beds,
                    "free_beds": total_beds - occupied_beds,
                    "occupancy_rate_percent": round((occupied_beds / total_beds) * 100, 1) if total_beds else 0,
                    "icu_critical_patients": icu,
                    "available_doctors": avail_docs,
                },
                "daily_stats_last_7_days": daily,
            }

        elif name == "get_patients_by_doctor":
            cursor.execute(
                "SELECT p.* FROM patients p WHERE p.doctor_id = ? AND p.status != 'discharged' ORDER BY p.status DESC",
                (arguments["doctor_id"],)
            )
            rows = cursor.fetchall()
            result = {"patients": rows_to_list(rows), "count": len(rows)}

        elif name == "get_critical_patients":
            cursor.execute(
                "SELECT p.*, d.name as doctor_name, d.specialization FROM patients p LEFT JOIN doctors d ON p.doctor_id = d.id WHERE p.status = 'critical' ORDER BY p.admission_date"
            )
            rows = cursor.fetchall()
            result = {"critical_patients": rows_to_list(rows), "count": len(rows)}

        elif name == "get_ward_summary":
            cursor.execute("""
                SELECT 
                    b.ward,
                    COUNT(b.id) as total_beds,
                    SUM(b.is_occupied) as occupied_beds,
                    COUNT(DISTINCT p.id) as patient_count,
                    GROUP_CONCAT(DISTINCT p.status) as patient_statuses
                FROM beds b
                LEFT JOIN patients p ON b.patient_id = p.id
                GROUP BY b.ward
                ORDER BY b.ward
            """)
            rows = cursor.fetchall()
            wards = []
            for row in rows:
                ward_data = dict(row)
                ward_data["free_beds"] = ward_data["total_beds"] - (ward_data["occupied_beds"] or 0)
                ward_data["occupancy_rate"] = round((ward_data["occupied_beds"] / ward_data["total_beds"]) * 100, 1) if ward_data["total_beds"] else 0
                wards.append(ward_data)
            result = {"wards": wards}

        elif name == "get_doctor_by_name":
            q = f"%{arguments['name']}%"
            cursor.execute(
                """
                SELECT * FROM doctors
                WHERE name LIKE ?
                ORDER BY experience_years DESC, name ASC
                """,
                (q,)
            )
            rows = cursor.fetchall()
            result = {"doctors": rows_to_list(rows), "count": len(rows)}

        elif name == "get_doctors_by_experience":
            query = "SELECT * FROM doctors WHERE experience_years >= ?"
            params = [arguments["min_years"]]
            if arguments.get("department"):
                query += " AND department = ?"
                params.append(arguments["department"])
            if arguments.get("specialization"):
                query += " AND specialization = ?"
                params.append(arguments["specialization"])

            available_only = arguments.get("available_only")
            if isinstance(available_only, str):
                available_only = available_only.strip().lower() in ("true", "1", "yes")
            if available_only is True:
                query += " AND available = 1"

            query += " ORDER BY experience_years DESC, name ASC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = {"doctors": rows_to_list(rows), "count": len(rows)}

        elif name == "get_appointments_by_doctor_name":
            query = """
                SELECT a.*, p.name as patient_name, d.name as doctor_name
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.id
                LEFT JOIN doctors d ON a.doctor_id = d.id
                WHERE d.name LIKE ?
            """
            params = [f"%{arguments['doctor_name']}%"]
            if arguments.get("date"):
                query += " AND a.date = ?"
                params.append(arguments["date"])
            if arguments.get("status"):
                query += " AND a.status = ?"
                params.append(arguments["status"])
            limit = arguments.get("limit", 50)
            query += f" ORDER BY a.date, a.time LIMIT {limit}"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = {"appointments": rows_to_list(rows), "count": len(rows)}

        elif name == "get_appointments_by_patient_id":
            query = """
                SELECT a.*, p.name as patient_name, d.name as doctor_name
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.id
                LEFT JOIN doctors d ON a.doctor_id = d.id
                WHERE a.patient_id = ?
                ORDER BY a.date, a.time
            """
            limit = arguments.get("limit", 50)
            cursor.execute(query + f" LIMIT {limit}", (arguments["patient_id"],))
            rows = cursor.fetchall()
            result = {"appointments": rows_to_list(rows), "count": len(rows)}

        elif name == "get_recent_admissions":
            days = arguments.get("days", 3)
            query = """
                SELECT p.*, d.name as doctor_name, d.department
                FROM patients p
                LEFT JOIN doctors d ON p.doctor_id = d.id
                WHERE date(p.admission_date) >= date('now', '-' || ? || ' day')
            """
            params = [days]
            if arguments.get("ward"):
                query += " AND p.ward = ?"
                params.append(arguments["ward"])
            query += " ORDER BY p.admission_date DESC"
            limit = arguments.get("limit", 50)
            cursor.execute(query + f" LIMIT {limit}", params)
            rows = cursor.fetchall()
            result = {"patients": rows_to_list(rows), "count": len(rows), "days": days}

        elif name == "get_department_overview":
            query = """
                SELECT
                    d.department,
                    COUNT(DISTINCT d.id) as total_doctors,
                    SUM(CASE WHEN d.available = 1 THEN 1 ELSE 0 END) as available_doctors,
                    COUNT(DISTINCT p.id) as active_patients
                FROM doctors d
                LEFT JOIN patients p ON p.doctor_id = d.id AND p.status != 'discharged'
                WHERE 1=1
            """
            params = []
            if arguments.get("department"):
                query += " AND d.department = ?"
                params.append(arguments["department"])
            query += " GROUP BY d.department ORDER BY active_patients DESC, d.department ASC"
            cursor.execute(query, params)
            rows = rows_to_list(cursor.fetchall())
            for row in rows:
                total = row["total_doctors"] or 0
                available = row["available_doctors"] or 0
                row["availability_percent"] = round((available / total) * 100, 1) if total else 0
            result = {"departments": rows, "count": len(rows)}

        elif name == "get_appointments_summary":
            cursor.execute(
                """
                SELECT status, COUNT(*) as total
                FROM appointments
                GROUP BY status
                ORDER BY status
                """
            )
            status_rows = rows_to_list(cursor.fetchall())
            counts = {r["status"]: r["total"] for r in status_rows}
            total = sum(counts.values())
            completed = counts.get("completed", 0)
            cancelled = counts.get("cancelled", 0)
            result = {
                "summary": {
                    "total_appointments": total,
                    "scheduled": counts.get("scheduled", 0),
                    "completed": completed,
                    "cancelled": cancelled,
                    "completion_rate_percent": round((completed / total) * 100, 1) if total else 0,
                    "cancellation_rate_percent": round((cancelled / total) * 100, 1) if total else 0,
                },
                "by_status": status_rows,
            }

        elif name == "get_patients_by_condition":
            condition = arguments["condition"].strip().lower()
            condition_map = {
                "cardiac": ["cardiac", "heart", "coronary", "myocardial"],
                "respiratory": ["respiratory", "pneumonia", "copd", "asthma", "pulmonary", "ards"],
                "neurological": ["neuro", "stroke", "parkinson", "alzheimer", "glioblastoma"],
                "infectious": ["infection", "sepsis", "dengue", "tuberculosis", "viral"],
                "trauma": ["trauma", "fracture", "injury", "burn"],
                "cancer": ["cancer", "carcinoma", "leukemia", "lymphoma", "tumor", "oncology"],
            }

            keywords = condition_map.get(condition, [condition])
            query = """
                SELECT p.*, d.name as doctor_name, d.department
                FROM patients p
                LEFT JOIN doctors d ON p.doctor_id = d.id
                WHERE (
            """
            query += " OR ".join(["LOWER(p.diagnosis) LIKE ?" for _ in keywords])
            query += ")"
            params = [f"%{k}%" for k in keywords]
            if arguments.get("status"):
                query += " AND p.status = ?"
                params.append(arguments["status"])
            query += " ORDER BY p.admission_date DESC"
            limit = arguments.get("limit", 50)
            cursor.execute(query + f" LIMIT {limit}", params)
            rows = cursor.fetchall()
            result = {"patients": rows_to_list(rows), "count": len(rows), "condition": condition, "keywords": keywords}

        elif name == "get_patients_by_doctor_name":
            query = """
                SELECT p.*, d.name as doctor_name, d.specialization, d.department, d.contact as doctor_contact
                FROM patients p
                JOIN doctors d ON p.doctor_id = d.id
                WHERE d.name LIKE ?
            """
            params = [f"%{arguments['doctor_name']}%"]
            if arguments.get("status"):
                query += " AND p.status = ?"
                params.append(arguments["status"])
            else:
                query += " AND p.status != 'discharged'"
            query += " ORDER BY p.status DESC, p.admission_date DESC"
            limit = arguments.get("limit", 50)
            cursor.execute(query + f" LIMIT {limit}", params)
            rows = cursor.fetchall()
            result = {"patients": rows_to_list(rows), "count": len(rows), "doctor_name_query": arguments['doctor_name']}

        elif name == "get_patients_by_department":
            query = """
                SELECT p.*, d.name as doctor_name, d.specialization, d.department
                FROM patients p
                JOIN doctors d ON p.doctor_id = d.id
                WHERE d.department LIKE ?
            """
            params = [f"%{arguments['department']}%"]
            if arguments.get("status"):
                query += " AND p.status = ?"
                params.append(arguments["status"])
            else:
                query += " AND p.status != 'discharged'"
            query += " ORDER BY p.status DESC, p.admission_date DESC"
            limit = arguments.get("limit", 50)
            cursor.execute(query + f" LIMIT {limit}", params)
            rows = cursor.fetchall()
            result = {"patients": rows_to_list(rows), "count": len(rows), "department": arguments['department']}

        elif name == "get_todays_appointments":
            from datetime import date
            today = date.today().isoformat()
            query = """
                SELECT a.*, p.name as patient_name, d.name as doctor_name, d.specialization
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.id
                LEFT JOIN doctors d ON a.doctor_id = d.id
                WHERE a.date = ?
            """
            params = [today]
            if arguments.get("status"):
                query += " AND a.status = ?"
                params.append(arguments["status"])
            query += " ORDER BY a.time ASC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            result = {"appointments": rows_to_list(rows), "count": len(rows), "date": today}

        else:
            result = {"error": f"Unknown tool: {name}"}

    except Exception as e:
        result = {"error": str(e)}
    finally:
        conn.close()

    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())