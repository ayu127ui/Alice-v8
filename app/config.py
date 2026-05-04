import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Camera Configuration
    CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")
    THREAT_THRESHOLD = float(os.getenv("THREAT_THRESHOLD", "0.55"))
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "smart_cctv.db")
    
    # Detection Features
    ENABLE_PPE_DETECTION = os.getenv("ENABLE_PPE_DETECTION", "True").lower() == "true"
    ENABLE_ADVANCED_MODELS = os.getenv("ENABLE_ADVANCED_MODELS", "True").lower() == "true"
    USE_KAGGLE_MODELS = os.getenv("USE_KAGGLE_MODELS", "False").lower() == "true"
    USE_HUGGINGFACE_MODELS = os.getenv("USE_HUGGINGFACE_MODELS", "True").lower() == "true"
    
    # PPE Configuration
    REQUIRED_PPE = os.getenv("REQUIRED_PPE", "helmet,safety_vest").split(",")
    PPE_ALERT_COOLDOWN = int(os.getenv("PPE_ALERT_COOLDOWN", "60"))
    
    # Alert Configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM = os.getenv("TWILIO_FROM")
    ALERT_SMS_TO = os.getenv("ALERT_SMS_TO")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")
    
    # Model Sources
    MODEL_SOURCES = {
        "ppe": os.getenv("PPE_MODEL_SOURCE", "huggingface"),  # local, huggingface, kaggle
        "weapon": os.getenv("WEAPON_MODEL_SOURCE", "local"),
        "person": os.getenv("PERSON_MODEL_SOURCE", "local"),
    }

