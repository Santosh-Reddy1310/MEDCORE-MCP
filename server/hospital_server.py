import sqlite3
import os
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "hospital.db")

app = Server("medcore-hospital-server")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_list(rows):
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
            description="Get all doctors. Optionally filter by specialization or department.",
            inputSchema={
                "type": "object",
                "properties": {
                    "specialization": {"type": "string", "description": "Filter by specialization"},
                    "department": {"type": "string", "description": "Filter by department name"},
                    "available_only": {"type": "boolean", "description": "Show only available doctors"},
                },
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
            result = {"patients": rows_to_list(cursor.fetchall()), "total": cursor.rowcount}

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
            if arguments.get("available_only"):
                query += " AND available = 1"
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