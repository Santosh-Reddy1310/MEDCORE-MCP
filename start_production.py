"""
Quick start script for production deployment.
Runs all initialization checks and starts the application.
"""
import os
import sys
import subprocess


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd, description):
    """Run a command and check for errors."""
    print(f"→ {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"✗ Failed: {result.stderr}")
        return False
    
    print(f"✓ {description} completed")
    return True


def main():
    """Run production startup sequence."""
    print_header("MedCore MCP - Production Startup")
    
    # Step 1: Check environment
    print("Step 1: Checking environment configuration...")
    has_env_file = os.path.exists(".env") or os.path.exists(".env.local")
    has_env_var = bool(os.getenv("GROQ_API_KEY"))
    if not has_env_file and not has_env_var:
        print("✗ No API key configuration found!")
        print("\n📝 Configure one of the following:")
        print("   1. .env or .env.local file with GROQ_API_KEY")
        print("   2. Platform environment variable: GROQ_API_KEY")
        print("   3. Secret manager injection during deployment\n")
        return 1
    print("✓ Environment configuration detected\n")
    
    # Step 2: Run health check
    print("Step 2: Running system health check...")
    if not run_command(f"{sys.executable} health_check.py", "Health check"):
        print("\n⚠ System not ready. Please fix the issues above.\n")
        return 1
    
    # Step 3: Initialize database if needed
    print("\nStep 3: Verifying database...")
    db_path = os.path.join("db", "hospital.db")
    if not os.path.exists(db_path):
        print("→ Database not found, initializing...")
        if not run_command(f"{sys.executable} db/setup_db.py", "Database initialization"):
            return 1
    else:
        print("✓ Database exists\n")
    
    # Step 4: Ready to launch
    print_header("✅ System Ready for Production")
    
    print("🚀 Application is configured and ready to launch!")
    streamlit_cmd = f"{sys.executable} -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true"
    print("\nStart the application with:")
    print(f"   {streamlit_cmd}")
    print("\nOr to run in background:")
    print(f"   nohup {streamlit_cmd} &  # Linux/Mac")
    print(f'   start "" {streamlit_cmd}   # Windows')
    
    print("\n📊 Monitoring:")
    print("   - Health check: python health_check.py")
    print("   - Database stats: python utils/db_init.py")
    print("   - Config check: python utils/config.py")
    
    print("\n📚 Documentation:")
    print("   - DEPLOYMENT.md - Full deployment guide")
    print("   - README.md - Project overview")
    
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
