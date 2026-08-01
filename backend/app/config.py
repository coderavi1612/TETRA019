import os

# Base directory of the app package
APP_DIR: str = os.path.dirname(os.path.abspath(__file__))

# Manually load .env file from the backend folder if present
env_path = os.path.join(os.path.dirname(APP_DIR), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                try:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")
                except Exception:
                    pass

class Settings:
    # Base directory of the app package
    APP_DIR: str = APP_DIR
    
    # Path where uploaded documents will be saved
    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR", 
        os.path.join(APP_DIR, "uploads")
    )
    
    # Path where parsed outputs and manifest will be saved
    OUTPUT_DIR: str = os.getenv(
        "OUTPUT_DIR", 
        os.path.join(APP_DIR, "outputs")
    )
    
    # Allowed CORS origins, comma-separated in environment variables
    CORS_ORIGINS: list[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "*").split(",") 
        if origin.strip()
    ]

    # Database & Supabase Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    SUPABASE_SECRET_KEY: str = os.getenv("SUPABASE_SECRET_KEY", "")
    SUPABASE_JWKS_URL: str = os.getenv("SUPABASE_JWKS_URL", "")

settings = Settings()

