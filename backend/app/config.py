import os

class Settings:
    # Base directory of the app package
    APP_DIR: str = os.path.dirname(os.path.abspath(__file__))
    
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

settings = Settings()
