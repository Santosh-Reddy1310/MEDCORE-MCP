# MedCore Hospital Server - Tools Guide

## Overview
The hospital server provides 12 MCP tools for querying hospital data across 5 hospitals with 75 patients and 35 doctors.

## Available Tools

### 1. **get_all_patients**
Get all patients with optional filtering.
- **Parameters:**
  - `ward` (optional): Ward A, Ward B, Ward C, Ward D, ICU
  - `status` (optional): admitted, critical, post-op, discharged
  - `limit` (optional): Max results (default: 50)
- **Returns:** List of patients with doctor info

### 2. **get_patient_by_id**
Get detailed information for a specific patient.
- **Parameters:**
  - `patient_id` (required): Patient ID (1-75)
- **Returns:** Patient details including doctor name and specialization

### 3. **search_patient**
Search patients by name or diagnosis.
- **Parameters:**
  - `query` (required): Name or diagnosis keyword
- **Returns:** Matching patients with count

### 4. **get_all_doctors**
Get all doctors with optional filtering.
- **Parameters:**
  - `specialization` (optional): e.g., Cardiology, Oncology, Neurology
  - `department` (optional): e.g., Cardiology, Surgery, Emergency
  - `available_only` (optional): Boolean to show only available doctors
- **Returns:** List of doctors with experience and contact info

### 5. **get_available_doctors**
Get all currently available doctors.
- **Parameters:** None
- **Returns:** Available doctors sorted by specialization

### 6. **get_doctor_by_id**
Get detailed information for a specific doctor.
- **Parameters:**
  - `doctor_id` (required): Doctor ID (1-35)
- **Returns:** Doctor details including specialization and experience

### 7. **get_bed_availability**
Get bed occupancy status.
- **Parameters:**
  - `ward` (optional): Specific ward name
- **Returns:** 
  - If ward specified: Detailed bed list with occupancy
  - If no ward: Summary by ward with occupancy rates

### 8. **get_appointments**
Get appointments with optional filtering.
- **Parameters:**
  - `date` (optional): YYYY-MM-DD format
  - `status` (optional): scheduled, completed, cancelled
  - `limit` (optional): Max results (default: 50)
- **Returns:** Appointments with patient and doctor names

### 9. **get_hospital_stats**
Get comprehensive hospital statistics.
- **Parameters:** None
- **Returns:**
  - Active patients count
  - Critical patients count
  - Bed occupancy metrics
  - ICU status
  - Available doctors
  - 7-day trend data

### 10. **get_patients_by_doctor**
Get all patients assigned to a specific doctor.
- **Parameters:**
  - `doctor_id` (required): Doctor ID
- **Returns:** List of non-discharged patients with count

### 11. **get_critical_patients**
Get all critical patients in the hospital.
- **Parameters:** None
- **Returns:** Critical patients with doctor info and admission dates

### 12. **get_ward_summary**
Get summary of all wards.
- **Parameters:** None
- **Returns:** Ward-wise statistics including:
  - Total beds
  - Occupied beds
  - Patient count
  - Occupancy rate
  - Patient statuses

## Example Queries

### Get all critical patients
```
Tool: get_critical_patients
Parameters: {}
```

### Get cardiology doctors
```
Tool: get_all_doctors
Parameters: {"specialization": "Cardiology"}
```

### Get patients in ICU
```
Tool: get_all_patients
Parameters: {"ward": "ICU"}
```

### Search for cancer patients
```
Tool: search_patient
Parameters: {"query": "Cancer"}
```

### Get bed availability for Ward A
```
Tool: get_bed_availability
Parameters: {"ward": "Ward A"}
```

### Get appointments for today
```
Tool: get_appointments
Parameters: {"date": "2024-03-08", "status": "scheduled"}
```

### Get patients under Dr. Arjun Mehta (ID: 1)
```
Tool: get_patients_by_doctor
Parameters: {"doctor_id": 1}
```

## Database Schema

### Patients Table
- id, name, age, gender, ward, admission_date, diagnosis, doctor_id, status, blood_group, contact

### Doctors Table
- id, name, specialization, department, available, contact, experience_years

### Beds Table
- id, ward, bed_number, is_occupied, patient_id

### Appointments Table
- id, patient_id, doctor_id, date, time, reason, status

### Hospital Stats Table
- id, date, total_admissions, total_discharges, icu_occupancy, emergency_cases, revenue

## Data Distribution

- **5 Hospitals** with distributed patient load
- **35 Doctors** across 20+ specializations
- **75 Patients** with diverse conditions
- **70 Beds** across 5 wards per hospital
- **50 Appointments** with various statuses
- **7 Days** of historical statistics
