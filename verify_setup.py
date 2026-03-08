#!/usr/bin/env python3
"""
MedCore Setup Verification Script
Checks all components are properly configured
"""

import os
import sys
import sqlite3
from pathlib import Path

def check_env_file():
    """Check if .env.local exists and has GROQ_API_KEY key"""
    print("🔍 Checking .env.local...")
    env_path = Path(".env.local")
    
    if not env_path.exists():
        print("  ❌ .env.local not found")
        return False
    
    with open(env_path) as f:
        content = f.read()
        if "GROQ_API_KEY" not in content:
            print("  ❌ GROQ_API_KEY not found in .env.local")
            return False
        if "gsk_" not in content:
            print("  ⚠️  GROQ_API_KEY value looks invalid (should start with 'gsk_')")
            return False
    
    print("  ✅ .env.local configured correctly")
    return True


def check_database():
    """Check if database exists and has data"""
    print("\n🔍 Checking database...")
    db_path = Path("db/hospital.db")
    
    if not db_path.exists():
        print("  ❌ Database not found at db/hospital.db")
        print("     Run: python db/setup_db.py")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ["doctors", "patients", "beds", "appointments", "hospital_stats"]
        
        for table in required_tables:
            if table not in tables:
                print(f"  ❌ Table '{table}' not found")
                return False
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM doctors")
        doctors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM patients")
        patients = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM beds")
        beds = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM appointments")
        appointments = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  ✅ Database OK")
        print(f"     - Doctors: {doctors}")
        print(f"     - Patients: {patients}")
        print(f"     - Beds: {beds}")
        print(f"     - Appointments: {appointments}")
        
        if doctors < 30 or patients < 70 or beds < 60:
            print("  ⚠️  Data count seems low, consider re-running setup")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")
    required = ["groq", "streamlit", "mcp", "dotenv"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n  Install missing packages:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def check_files():
    """Check if all required files exist"""
    print("\n🔍 Checking project files...")
    required_files = [
        "app.py",
        "requirements.txt",
        "db/setup_db.py",
        "server/hospital_server.py",
        "client/ai_client.py",
    ]
    
    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} not found")
            all_exist = False
    
    return all_exist


def check_groq_api():
    """Check if Groq API key can be loaded"""
    print("\n🔍 Checking Groq API configuration...")
    try:
        from dotenv import load_dotenv
        load_dotenv(".env.local")
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            print("  ❌ GROQ_API_KEY not loaded from environment")
            return False
        
        if not api_key.startswith("gsk_"):
            print("  ❌ GROQ_API_KEY format invalid (should start with 'gsk_')")
            return False
        
        print(f"  ✅ GROQ_API_KEY loaded: {api_key[:20]}...")
        return True
    except Exception as e:
        print(f"  ❌ Error loading GROQ_API_KEY: {e}")
        return False


def check_mcp_server():
    """Check if MCP server can be imported"""
    print("\n🔍 Checking MCP server...")
    try:
        sys.path.insert(0, "server")
        # Just check if the file is valid Python
        with open("server/hospital_server.py") as f:
            compile(f.read(), "hospital_server.py", "exec")
        print("  ✅ MCP server syntax OK")
        return True
    except Exception as e:
        print(f"  ❌ MCP server error: {e}")
        return False


def main():
    """Run all checks"""
    print("=" * 50)
    print("🏥 MedCore Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Environment", check_env_file),
        ("Dependencies", check_dependencies),
        ("Project Files", check_files),
        ("Database", check_database),
        ("Groq API", check_groq_api),
        ("MCP Server", check_mcp_server),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Ready to run:")
        print("   streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
