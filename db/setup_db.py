import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "hospital.db")


def create_tables(conn):
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            department TEXT NOT NULL,
            available INTEGER DEFAULT 1,
            contact TEXT,
            experience_years INTEGER
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            ward TEXT,
            admission_date TEXT,
            diagnosis TEXT,
            doctor_id INTEGER,
            status TEXT DEFAULT 'admitted',
            blood_group TEXT,
            contact TEXT,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        );

        CREATE TABLE IF NOT EXISTS beds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ward TEXT NOT NULL,
            bed_number TEXT NOT NULL,
            is_occupied INTEGER DEFAULT 0,
            patient_id INTEGER,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            date TEXT,
            time TEXT,
            reason TEXT,
            status TEXT DEFAULT 'scheduled',
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        );

        CREATE TABLE IF NOT EXISTS hospital_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total_admissions INTEGER,
            total_discharges INTEGER,
            icu_occupancy INTEGER,
            emergency_cases INTEGER,
            revenue INTEGER
        );
    """)
    conn.commit()
    print("✅ Tables created.")


def seed_doctors(conn):
    cursor = conn.cursor()
    doctors = [
        # Hospital 1 - City General Hospital
        ("Dr. Arjun Mehta",       "Cardiology",      "Cardiology",        1, "+91-9876543201", 15),
        ("Dr. Priya Sharma",      "Neurology",       "Neurology",         1, "+91-9876543202", 12),
        ("Dr. Suresh Reddy",      "Orthopedics",     "Orthopedics",       1, "+91-9876543203", 10),
        ("Dr. Ananya Iyer",       "Pediatrics",      "Pediatrics",        1, "+91-9876543204", 8),
        ("Dr. Vikram Nair",       "General Surgery", "Surgery",           0, "+91-9876543205", 18),
        ("Dr. Meena Pillai",      "Dermatology",     "Dermatology",       1, "+91-9876543206", 6),
        ("Dr. Rohit Gupta",       "Oncology",        "Oncology",          1, "+91-9876543207", 14),
        ("Dr. Kavya Desai",       "Gynecology",      "Gynecology",        1, "+91-9876543208", 9),
        ("Dr. Sameer Joshi",      "Psychiatry",      "Psychiatry",        0, "+91-9876543209", 11),
        ("Dr. Lakshmi Venkat",    "Emergency",       "Emergency",         1, "+91-9876543210", 7),
        
        # Hospital 2 - Apollo Medical Center
        ("Dr. Rajesh Kumar",      "Cardiology",      "Cardiology",        1, "+91-9876543211", 16),
        ("Dr. Neha Gupta",        "Nephrology",      "Nephrology",        1, "+91-9876543212", 13),
        ("Dr. Anil Verma",        "Gastroenterology","GI",                1, "+91-9876543213", 11),
        ("Dr. Sunita Rao",        "Pulmonology",     "Respiratory",       1, "+91-9876543214", 9),
        ("Dr. Harish Patel",      "Urology",         "Urology",           0, "+91-9876543215", 14),
        ("Dr. Anjali Singh",      "Rheumatology",    "Rheumatology",      1, "+91-9876543216", 8),
        ("Dr. Vikram Desai",      "Endocrinology",   "Endocrinology",     1, "+91-9876543217", 12),
        ("Dr. Pooja Nair",        "Hematology",      "Hematology",        1, "+91-9876543218", 10),
        
        # Hospital 3 - St. Mary's Hospital
        ("Dr. Sanjay Chopra",     "Neurosurgery",    "Neurosurgery",      1, "+91-9876543219", 17),
        ("Dr. Divya Menon",       "Ophthalmology",   "Ophthalmology",     1, "+91-9876543220", 9),
        ("Dr. Ravi Shankar",      "ENT",             "ENT",               0, "+91-9876543221", 13),
        ("Dr. Geeta Bhat",        "Infectious Disease","ID",              1, "+91-9876543222", 11),
        ("Dr. Ashok Reddy",       "Trauma Surgery",  "Trauma",            1, "+91-9876543223", 15),
        ("Dr. Sneha Kapoor",      "Anesthesiology",  "Anesthesia",        1, "+91-9876543224", 10),
        
        # Hospital 4 - Fortis Healthcare
        ("Dr. Mohan Rao",         "Cardiothoracic",  "Cardiothoracic",    1, "+91-9876543225", 18),
        ("Dr. Priya Nambiar",     "Obstetrics",      "OB/GYN",            1, "+91-9876543226", 12),
        ("Dr. Karan Singh",       "Pediatric Surgery","Pediatric Surgery",1, "+91-9876543227", 9),
        ("Dr. Isha Malhotra",     "Pathology",       "Pathology",         0, "+91-9876543228", 8),
        ("Dr. Rajiv Gupta",       "Radiology",       "Radiology",         1, "+91-9876543229", 14),
        
        # Hospital 5 - Max Healthcare
        ("Dr. Deepak Sharma",     "Oncology",        "Oncology",          1, "+91-9876543230", 16),
        ("Dr. Nisha Patel",       "Palliative Care", "Palliative",        1, "+91-9876543231", 7),
        ("Dr. Arjun Nair",        "Geriatrics",      "Geriatrics",        1, "+91-9876543232", 11),
        ("Dr. Meera Joshi",       "Immunology",      "Immunology",        1, "+91-9876543233", 10),
        ("Dr. Sanjiv Kumar",      "Hepatology",      "Hepatology",        0, "+91-9876543234", 13),
    ]
    cursor.executemany(
        "INSERT INTO doctors (name, specialization, department, available, contact, experience_years) VALUES (?,?,?,?,?,?)",
        doctors
    )
    conn.commit()
    print("✅ Doctors seeded (35).")


def seed_patients(conn):
    cursor = conn.cursor()
    today = datetime.today()

    patients = [
        # Hospital 1 - City General Hospital (Patients 1-15)
        ("Ravi Kumar",        45, "Male",   "Ward A", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Type 2 Diabetes",          1, "admitted",    "B+",  "+91-9000000001"),
        ("Sneha Patel",       30, "Female", "ICU",    (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Severe Head Injury",       2, "critical",    "O+",  "+91-9000000002"),
        ("Mohammed Irfan",    60, "Male",   "Ward B", (today - timedelta(days=7)).strftime("%Y-%m-%d"),  "Coronary Artery Disease",  1, "admitted",    "A+",  "+91-9000000003"),
        ("Geeta Nambiar",     25, "Female", "Ward C", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Fractured Femur",          3, "admitted",    "AB-", "+91-9000000004"),
        ("Aditya Singh",      8,  "Male",   "Ward D", (today - timedelta(days=5)).strftime("%Y-%m-%d"),  "Viral Fever",              4, "admitted",    "O-",  "+91-9000000005"),
        ("Fatima Shaikh",     35, "Female", "Ward A", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Hypertension",             1, "admitted",    "B-",  "+91-9000000006"),
        ("Sunil Verma",       55, "Male",   "Ward B", (today - timedelta(days=6)).strftime("%Y-%m-%d"),  "Lung Cancer - Stage 2",    7, "admitted",    "A-",  "+91-9000000007"),
        ("Pooja Menon",       28, "Female", "Ward C", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Appendicitis",             5, "post-op",     "O+",  "+91-9000000008"),
        ("Kiran Rao",         72, "Male",   "ICU",    (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Cardiac Arrest",           1, "critical",    "A+",  "+91-9000000009"),
        ("Nisha Agarwal",     40, "Female", "Ward D", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Migraine - Chronic",       2, "admitted",    "B+",  "+91-9000000010"),
        ("Deepak Tiwari",     50, "Male",   "Ward A", (today - timedelta(days=8)).strftime("%Y-%m-%d"),  "Kidney Stones",            5, "admitted",    "AB+", "+91-9000000011"),
        ("Asha Krishnan",     65, "Female", "Ward B", (today - timedelta(days=5)).strftime("%Y-%m-%d"),  "Hip Replacement",          3, "post-op",     "O-",  "+91-9000000012"),
        ("Vijay Patil",       33, "Male",   "Ward C", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Dengue Fever",             10,"admitted",    "B+",  "+91-9000000013"),
        ("Rekha Bose",        48, "Female", "Ward D", (today - timedelta(days=9)).strftime("%Y-%m-%d"),  "Thyroid Disorder",         6, "admitted",    "A+",  "+91-9000000014"),
        ("Aryan Shah",        18, "Male",   "Ward A", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Asthma Attack",            1, "admitted",    "O+",  "+91-9000000015"),
        
        # Hospital 2 - Apollo Medical Center (Patients 16-30)
        ("Sunita Chauhan",    55, "Female", "ICU",    (today).strftime("%Y-%m-%d"),                      "Stroke",                   11, "critical",    "AB+", "+91-9000000016"),
        ("Manoj Kumar",       42, "Male",   "Ward B", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Gallbladder Stones",       12, "admitted",    "B-",  "+91-9000000017"),
        ("Divya Nair",        29, "Female", "Ward C", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "PCOS",                     13, "admitted",    "O+",  "+91-9000000018"),
        ("Ramesh Pillai",     70, "Male",   "Ward D", (today - timedelta(days=6)).strftime("%Y-%m-%d"),  "Parkinson's Disease",      11, "admitted",    "A-",  "+91-9000000019"),
        ("Kavitha Rajan",     38, "Female", "Ward A", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Breast Cancer - Stage 1",  14, "admitted",    "B+",  "+91-9000000020"),
        ("Harish Shetty",     45, "Male",   "Ward B", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Diabetes + Hypertension",  11, "admitted",    "O+",  "+91-9000000021"),
        ("Meera Jain",        22, "Female", "Ward C", (today).strftime("%Y-%m-%d"),                      "Road Accident - Fracture", 12, "admitted",    "AB-", "+91-9000000022"),
        ("Sanjay Dubey",      58, "Male",   "Ward D", (today - timedelta(days=7)).strftime("%Y-%m-%d"),  "COPD",                     13, "admitted",    "A+",  "+91-9000000023"),
        ("Anita Kulkarni",    31, "Female", "Ward A", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Anemia",                   14, "admitted",    "O-",  "+91-9000000024"),
        ("Prakash Sharma",    63, "Male",   "Ward B", (today - timedelta(days=5)).strftime("%Y-%m-%d"),  "Prostate Issues",          15, "admitted",    "B+",  "+91-9000000025"),
        ("Lalitha Devi",      50, "Female", "ICU",    (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Multi-organ Failure",      11, "critical",    "A+",  "+91-9000000026"),
        ("Nikhil Joshi",      27, "Male",   "Ward C", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Sports Injury - Knee",     12, "admitted",    "O+",  "+91-9000000027"),
        ("Shalini Mishra",    44, "Female", "Ward D", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Rheumatoid Arthritis",     13, "admitted",    "B-",  "+91-9000000028"),
        ("Gopal Yadav",       66, "Male",   "Ward A", (today - timedelta(days=8)).strftime("%Y-%m-%d"),  "Heart Failure",            11, "admitted",    "AB+", "+91-9000000029"),
        ("Preethi Suresh",    36, "Female", "Ward B", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Kidney Failure",           15, "discharged",  "O+",  "+91-9000000030"),
        
        # Hospital 3 - St. Mary's Hospital (Patients 31-45)
        ("Vikram Desai",      52, "Male",   "Ward A", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Neurosurgery - Brain Tumor", 19, "post-op",   "B+",  "+91-9000000031"),
        ("Anjali Verma",      41, "Female", "Ward C", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Retinal Detachment",       20, "admitted",    "O+",  "+91-9000000032"),
        ("Rajesh Nair",       58, "Male",   "ICU",    (today).strftime("%Y-%m-%d"),                      "Severe Pneumonia",         21, "critical",    "A+",  "+91-9000000033"),
        ("Priya Kapoor",      34, "Female", "Ward B", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Tuberculosis",             22, "admitted",    "AB-", "+91-9000000034"),
        ("Sanjiv Kumar",      67, "Male",   "Ward D", (today - timedelta(days=6)).strftime("%Y-%m-%d"),  "Severe Burns - 35% BSA",   23, "admitted",    "O-",  "+91-9000000035"),
        ("Neha Sharma",       29, "Female", "Ward A", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Pregnancy Complications",  24, "admitted",    "B-",  "+91-9000000036"),
        ("Arun Patel",        55, "Male",   "Ward C", (today - timedelta(days=5)).strftime("%Y-%m-%d"),  "Acute Pancreatitis",       25, "admitted",    "A-",  "+91-9000000037"),
        ("Divya Singh",       38, "Female", "Ward B", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Sepsis",                   21, "critical",    "O+",  "+91-9000000038"),
        ("Karthik Rao",       44, "Male",   "Ward D", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Acute Myocardial Infarction", 19, "admitted", "A+", "+91-9000000039"),
        ("Meera Nambiar",     51, "Female", "ICU",    (today).strftime("%Y-%m-%d"),                      "Respiratory Failure",      23, "critical",    "B+",  "+91-9000000040"),
        ("Suresh Gupta",      62, "Male",   "Ward A", (today - timedelta(days=7)).strftime("%Y-%m-%d"),  "Diabetic Ketoacidosis",    20, "admitted",    "AB+", "+91-9000000041"),
        ("Pooja Desai",       33, "Female", "Ward C", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Acute Cholecystitis",      24, "post-op",     "O-",  "+91-9000000042"),
        ("Rajiv Menon",       48, "Male",   "Ward B", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Acute Appendicitis",       25, "post-op",     "B+",  "+91-9000000043"),
        ("Sneha Joshi",       26, "Female", "Ward D", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Ectopic Pregnancy",        24, "post-op",     "A+",  "+91-9000000044"),
        ("Ashok Reddy",       71, "Male",   "Ward A", (today - timedelta(days=6)).strftime("%Y-%m-%d"),  "Alzheimer's Disease",      22, "admitted",    "O+",  "+91-9000000045"),
        
        # Hospital 4 - Fortis Healthcare (Patients 46-60)
        ("Ritu Sharma",       39, "Female", "Ward C", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Cardiothoracic Surgery",   26, "post-op",     "B-",  "+91-9000000046"),
        ("Vikram Singh",      56, "Male",   "Ward B", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Congenital Heart Disease", 26, "admitted",    "AB+", "+91-9000000047"),
        ("Anjali Nair",       31, "Female", "Ward A", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Gestational Diabetes",     27, "admitted",    "O+",  "+91-9000000048"),
        ("Sanjay Patel",      7,  "Male",   "Ward D", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Pediatric Appendicitis",   28, "post-op",     "A+",  "+91-9000000049"),
        ("Meera Kapoor",      54, "Female", "ICU",    (today).strftime("%Y-%m-%d"),                      "Acute Leukemia",           29, "critical",    "B+",  "+91-9000000050"),
        ("Rajesh Verma",      47, "Male",   "Ward C", (today - timedelta(days=5)).strftime("%Y-%m-%d"),  "Metastatic Cancer",        30, "admitted",    "O-",  "+91-9000000051"),
        ("Priya Menon",       42, "Female", "Ward B", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Systemic Lupus Erythematosus", 27, "admitted", "A-", "+91-9000000052"),
        ("Arun Joshi",        68, "Male",   "Ward A", (today - timedelta(days=6)).strftime("%Y-%m-%d"),  "Prostate Cancer",          30, "admitted",    "B+",  "+91-9000000053"),
        ("Divya Rao",         35, "Female", "Ward D", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Ovarian Cyst",             27, "admitted",    "AB-", "+91-9000000054"),
        ("Karthik Nair",      61, "Male",   "Ward C", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Chronic Obstructive Pulmonary Disease", 28, "admitted", "O+", "+91-9000000055"),
        ("Sneha Desai",       28, "Female", "Ward B", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Acute Gastroenteritis",    29, "admitted",    "A+",  "+91-9000000056"),
        ("Suresh Nambiar",    73, "Male",   "ICU",    (today).strftime("%Y-%m-%d"),                      "Acute Coronary Syndrome",  26, "critical",    "B-",  "+91-9000000057"),
        ("Pooja Sharma",      44, "Female", "Ward A", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Uterine Fibroids",         27, "admitted",    "AB+", "+91-9000000058"),
        ("Rajiv Gupta",       52, "Male",   "Ward D", (today - timedelta(days=5)).strftime("%Y-%m-%d"),  "Benign Prostatic Hyperplasia", 28, "admitted", "O+", "+91-9000000059"),
        ("Anjali Joshi",      37, "Female", "Ward C", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Endometriosis",            27, "admitted",    "B+",  "+91-9000000060"),
        
        # Hospital 5 - Max Healthcare (Patients 61-75)
        ("Vikram Rao",        64, "Male",   "Ward B", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Advanced Pancreatic Cancer", 31, "admitted",   "A+",  "+91-9000000061"),
        ("Priya Singh",       58, "Female", "Ward A", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "End-stage Liver Disease",  34, "admitted",    "O-",  "+91-9000000062"),
        ("Sanjay Menon",      75, "Male",   "ICU",    (today).strftime("%Y-%m-%d"),                      "Septic Shock",             31, "critical",    "B+",  "+91-9000000063"),
        ("Meera Patel",       49, "Female", "Ward D", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Metastatic Breast Cancer", 31, "admitted",    "AB-", "+91-9000000064"),
        ("Arun Kapoor",       81, "Male",   "Ward C", (today - timedelta(days=6)).strftime("%Y-%m-%d"),  "Dementia with Behavioral Issues", 32, "admitted", "O+", "+91-9000000065"),
        ("Divya Nair",        55, "Female", "Ward B", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Immunodeficiency Syndrome", 33, "admitted",    "A+",  "+91-9000000066"),
        ("Karthik Sharma",    67, "Male",   "Ward A", (today - timedelta(days=5)).strftime("%Y-%m-%d"),  "Hepatocellular Carcinoma", 34, "admitted",    "B-",  "+91-9000000067"),
        ("Sneha Verma",       42, "Female", "Ward D", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Autoimmune Hepatitis",     34, "admitted",    "AB+", "+91-9000000068"),
        ("Suresh Desai",      70, "Male",   "ICU",    (today).strftime("%Y-%m-%d"),                      "Multi-organ Failure",      31, "critical",    "O+",  "+91-9000000069"),
        ("Pooja Joshi",       51, "Female", "Ward C", (today - timedelta(days=4)).strftime("%Y-%m-%d"),  "Lymphoma - Stage 3",       31, "admitted",    "A-",  "+91-9000000070"),
        ("Rajiv Nambiar",     76, "Male",   "Ward B", (today - timedelta(days=3)).strftime("%Y-%m-%d"),  "Chronic Heart Failure",    32, "admitted",    "B+",  "+91-9000000071"),
        ("Anjali Rao",        46, "Female", "Ward A", (today - timedelta(days=1)).strftime("%Y-%m-%d"),  "Palliative Care - Terminal", 32, "admitted",   "O+",  "+91-9000000072"),
        ("Vikram Joshi",      68, "Male",   "Ward D", (today - timedelta(days=5)).strftime("%Y-%m-%d"),  "Glioblastoma",             31, "admitted",    "AB+", "+91-9000000073"),
        ("Priya Desai",       53, "Female", "Ward C", (today - timedelta(days=2)).strftime("%Y-%m-%d"),  "Renal Cell Carcinoma",     33, "admitted",    "B-",  "+91-9000000074"),
        ("Sanjay Sharma",     72, "Male",   "ICU",    (today).strftime("%Y-%m-%d"),                      "Acute Respiratory Distress Syndrome", 31, "critical", "O-", "+91-9000000075"),
    ]

    cursor.executemany(
        "INSERT INTO patients (name, age, gender, ward, admission_date, diagnosis, doctor_id, status, blood_group, contact) VALUES (?,?,?,?,?,?,?,?,?,?)",
        patients
    )
    conn.commit()
    print("✅ Patients seeded (75).")


def seed_beds(conn):
    cursor = conn.cursor()
    beds = []
    wards = {
        "Ward A": 15,
        "Ward B": 15,
        "Ward C": 15,
        "Ward D": 15,
        "ICU":    10,
    }

    cursor.execute("SELECT id, ward FROM patients WHERE status != 'discharged'")
    patients = cursor.fetchall()
    patient_ward_map = {}
    for pid, ward in patients:
        patient_ward_map.setdefault(ward, []).append(pid)

    for ward, count in wards.items():
        ward_patients = patient_ward_map.get(ward, [])
        for i in range(1, count + 1):
            bed_num = f"{ward[:1]}-{str(i).zfill(2)}"
            if ward_patients:
                pid = ward_patients.pop(0)
                beds.append((ward, bed_num, 1, pid))
            else:
                beds.append((ward, bed_num, 0, None))

    cursor.executemany(
        "INSERT INTO beds (ward, bed_number, is_occupied, patient_id) VALUES (?,?,?,?)",
        beds
    )
    conn.commit()
    print("✅ Beds seeded (70 total).")


def seed_appointments(conn):
    cursor = conn.cursor()
    today = datetime.today()
    times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30"]
    reasons = ["Follow-up", "Routine Checkup", "Post-op Review", "Lab Results Discussion", "Consultation", "Prescription Renewal", "Emergency Consultation", "Specialist Review"]
    statuses = ["scheduled", "scheduled", "scheduled", "completed", "cancelled"]

    appointments = []
    for i in range(1, 51):
        patient_id = random.randint(1, 75)
        doctor_id = random.randint(1, 35)
        days_offset = random.randint(-2, 5)
        date = (today + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        time = random.choice(times)
        reason = random.choice(reasons)
        status = "completed" if days_offset < 0 else random.choice(statuses)
        appointments.append((patient_id, doctor_id, date, time, reason, status))

    cursor.executemany(
        "INSERT INTO appointments (patient_id, doctor_id, date, time, reason, status) VALUES (?,?,?,?,?,?)",
        appointments
    )
    conn.commit()
    print("✅ Appointments seeded (50).")


def seed_hospital_stats(conn):
    cursor = conn.cursor()
    today = datetime.today()
    stats = []
    for i in range(6, -1, -1):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        stats.append((
            date,
            random.randint(8, 20),
            random.randint(4, 12),
            random.randint(3, 6),
            random.randint(2, 8),
            random.randint(80000, 200000),
        ))

    cursor.executemany(
        "INSERT INTO hospital_stats (date, total_admissions, total_discharges, icu_occupancy, emergency_cases, revenue) VALUES (?,?,?,?,?,?)",
        stats
    )
    conn.commit()
    print("✅ Hospital stats seeded (7 days).")


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️  Old DB removed.")

    conn = sqlite3.connect(DB_PATH)
    print(f"📦 Creating database at: {DB_PATH}\n")

    create_tables(conn)
    seed_doctors(conn)
    seed_patients(conn)
    seed_beds(conn)
    seed_appointments(conn)
    seed_hospital_stats(conn)

    conn.close()
    print(f"\n🏥 MedCore DB ready! → {DB_PATH}")


if __name__ == "__main__":
    main()