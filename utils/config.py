"""Environment configuration manager with production-safe defaults."""

import os
from dotenv import load_dotenv


def _to_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _to_int(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"WARNING: Invalid {name}={raw!r}. Using default {default}.")
        return default


class Config:
    """Application configuration with safe defaults."""

    def __init__(self):
        self.PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # App configuration is needed before key resolution.
        self.ENV = os.getenv("ENVIRONMENT", "production").strip().lower()
        self.DEBUG = _to_bool(os.getenv("DEBUG"), default=False)

        # Load environment files without overriding platform-provided secrets.
        self._load_env_files()

        # Provider/model configuration
        self.GROQ_API_KEY = self._get_groq_key()
        self.MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")

        # Database configuration
        default_db_path = os.path.join(self.PROJECT_ROOT, "db", "hospital.db")
        self.DB_PATH = os.getenv("DB_PATH", default_db_path)
        self.DB_AUTO_INIT = _to_bool(os.getenv("DB_AUTO_INIT"), default=True)

        # MCP Server configuration
        self.MCP_TIMEOUT = _to_int("MCP_TIMEOUT", 30)
        self.MCP_MAX_RETRIES = _to_int("MCP_MAX_RETRIES", 3)

    def _load_env_files(self):
        """Load environment variables from project root env files if present."""
        env_local = os.path.join(self.PROJECT_ROOT, ".env.local")
        env_file = os.path.join(self.PROJECT_ROOT, ".env")

        if os.path.exists(env_local):
            load_dotenv(env_local, override=False)
        if os.path.exists(env_file):
            load_dotenv(env_file, override=False)

    def _get_groq_key(self):
        """Get Groq API key and surface clear guidance if missing."""
        key = os.getenv("GROQ_API_KEY")
        if key:
            return key

        message = (
            "GROQ_API_KEY is not set. Configure it in environment variables "
            "or in .env/.env.local."
        )
        if self.ENV == "development":
            raise ValueError(message)

        print(f"WARNING: {message}")
        return None

    def is_configured(self):
        """Check if the app is properly configured."""
        return self.GROQ_API_KEY is not None

    def validate(self):
        """Validate configuration and return list of issues."""
        issues = []

        if not self.GROQ_API_KEY:
            issues.append("GROQ_API_KEY is not set")

        db_dir = os.path.dirname(os.path.abspath(self.DB_PATH))
        if not os.path.exists(db_dir):
            issues.append(f"Database directory does not exist: {db_dir}")

        return issues


# Global config instance
config = Config()


if __name__ == "__main__":
    print("🔧 Configuration Check")
    print("=" * 60)
    print(f"Environment: {config.ENV}")
    print(f"Debug Mode: {config.DEBUG}")
    print(f"Model: {config.MODEL}")
    print(f"API Key Configured: {'✓' if config.GROQ_API_KEY else '✗'}")
    print(f"Database Path: {config.DB_PATH}")
    print(f"MCP Timeout: {config.MCP_TIMEOUT}s")
    print(f"MCP Max Retries: {config.MCP_MAX_RETRIES}")
    print()
    
    issues = config.validate()
    if issues:
        print("⚠ Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration is valid!")
