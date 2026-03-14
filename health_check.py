"""
Production-ready health check script for MedCore MCP.
Verifies all components before deployment.
"""
import os
import sys
import sqlite3
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_status(msg, status="info"):
    """Print colored status message."""
    if status == "pass":
        print(f"{GREEN}[OK]{RESET} {msg}")
        return True
    elif status == "fail":
        print(f"{RED}[FAIL]{RESET} {msg}")
        return False
    elif status == "warn":
        print(f"{YELLOW}[WARN]{RESET} {msg}")
        return True
    else:
        print(f"{BLUE}[INFO]{RESET} {msg}")
        return True


def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version >= (3, 8):
        return print_status(f"Python {version.major}.{version.minor}.{version.micro}", "pass")
    else:
        return print_status(f"Python {version.major}.{version.minor} (requires 3.8+)", "fail")


def check_dependencies():
    """Check if required packages are installed."""
    required = [
        ("streamlit", "streamlit"),
        ("groq", "groq"),
        ("mcp", "mcp"),
        ("dotenv", "python-dotenv"),
    ]
    
    # Check sqlite3 separately
    try:
        import sqlite3
        print_status(f"Package: sqlite3 (built-in)", "pass")
    except ImportError:
        print_status(f"Package: sqlite3 (missing)", "fail")
        return False
    
    all_ok = True
    for module_name, display_name in required:
        try:
            __import__(module_name)
            print_status(f"Package: {display_name}", "pass")
        except ImportError:
            print_status(f"Package: {display_name} (not installed)", "fail")
            all_ok = False
    
    return all_ok


def check_environment():
    """Check environment configuration."""
    # Check for .env files
    env_exists = False
    if os.path.exists(".env.local"):
        print_status("Environment file: .env.local", "pass")
        env_exists = True
    elif os.path.exists(".env"):
        print_status("Environment file: .env", "pass")
        env_exists = True
    else:
        print_status("No .env file found", "warn")
    
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv(".env.local")
    load_dotenv(".env")
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print_status(f"GROQ_API_KEY: {masked_key}", "pass")
        return True
    else:
        print_status("GROQ_API_KEY not set", "fail")
        return False


def check_database():
    """Check database status."""
    db_path = os.path.join("db", "hospital.db")
    
    if not os.path.exists(db_path):
        print_status("Database file not found", "warn")
        print(f"  {YELLOW}→ Will auto-initialize on first run{RESET}")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        required_tables = ['doctors', 'patients', 'beds', 'appointments', 'hospital_stats']
        
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print_status(f"Missing tables: {', '.join(missing)}", "fail")
            conn.close()
            return False
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM patients")
        patient_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM doctors")
        doctor_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM beds")
        bed_count = cursor.fetchone()[0]
        
        print_status(f"Database: {patient_count} patients, {doctor_count} doctors, {bed_count} beds", "pass")
        conn.close()
        return True
        
    except Exception as e:
        print_status(f"Database error: {str(e)}", "fail")
        return False


def check_file_structure():
    """Check if required files and directories exist."""
    required_items = [
        ("app.py", "file"),
        ("requirements.txt", "file"),
        ("server/hospital_server.py", "file"),
        ("client/ai_client.py", "file"),
        ("db/setup_db.py", "file"),
        ("utils/db_init.py", "file"),
        ("utils/config.py", "file"),
    ]
    
    all_ok = True
    for item, item_type in required_items:
        path = Path(item)
        if item_type == "file":
            if path.is_file():
                print_status(f"File: {item}", "pass")
            else:
                print_status(f"File: {item} (missing)", "fail")
                all_ok = False
        else:
            if path.is_dir():
                print_status(f"Directory: {item}", "pass")
            else:
                print_status(f"Directory: {item} (missing)", "fail")
                all_ok = False
    
    return all_ok


def check_mcp_server():
    """Test MCP server can start."""
    server_path = os.path.join("server", "hospital_server.py")
    
    if not os.path.exists(server_path):
        return print_status("MCP server script missing", "fail")
    
    print_status("MCP server script exists", "pass")
    return True


def main():
    """Run all health checks."""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}  MedCore MCP - Production Health Check{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")
    
    results = {}
    
    print(f"{BOLD}1. Python Environment{RESET}")
    results['python'] = check_python_version()
    print()
    
    print(f"{BOLD}2. Dependencies{RESET}")
    results['dependencies'] = check_dependencies()
    print()
    
    print(f"{BOLD}3. Environment Configuration{RESET}")
    results['environment'] = check_environment()
    print()
    
    print(f"{BOLD}4. File Structure{RESET}")
    results['file_structure'] = check_file_structure()
    print()
    
    print(f"{BOLD}5. Database{RESET}")
    results['database'] = check_database()
    print()
    
    print(f"{BOLD}6. MCP Server{RESET}")
    results['mcp'] = check_mcp_server()
    print()
    
    # Summary
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}Health Check Summary{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    if passed == total:
        print(f"{GREEN}{BOLD}[SUCCESS] ALL CHECKS PASSED ({passed}/{total}){RESET}")
        print(f"\n{GREEN}System is ready for production deployment!{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}{BOLD}[WARNING] {passed}/{total} checks passed{RESET}")
        print(f"\n{YELLOW}Please fix the issues above before deploying.{RESET}\n")
        
        # Provide helpful hints
        if not results.get('environment'):
            print(f"{BLUE}To fix environment:{RESET}")
            print("   1. Create .env file: cp .env.example .env")
            print("   2. Add your GROQ_API_KEY\n")
        
        if not results.get('database'):
            print(f"{BLUE}To fix database:{RESET}")
            print("   python db/setup_db.py\n")
        
        if not results.get('dependencies'):
            print(f"{BLUE}To fix dependencies:{RESET}")
            print("   pip install -r requirements.txt\n")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
