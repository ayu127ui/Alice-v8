#!/usr/bin/env python3
"""
Quick Setup Script for Project-Specula with PPE Detection
Guides through installation, model download, and configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(text):
    print(f"\n→ {text}")

def run_command(cmd, description=""):
    """Run shell command and return success status"""
    if description:
        print_section(description)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout:
                print(result.stdout)
            print("✓ Success")
            return True
        else:
            print(f"✗ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print_header("ENVIRONMENT CONFIGURATION")
    
    env_file = ".env"
    
    if os.path.exists(env_file):
        response = input(f"\n{env_file} already exists. Overwrite? (y/n): ").lower()
        if response != 'y':
            print("Skipping environment setup")
            return
    
    print_section("Configuring environment variables")
    
    config = {
        "CAMERA_SOURCE": input("Camera source (0 for webcam, or RTSP URL) [default: 0]: ") or "0",
        "ENABLE_PPE_DETECTION": "True",
        "ENABLE_ADVANCED_MODELS": "True",
        "USE_HUGGINGFACE_MODELS": "True",
        "REQUIRED_PPE": "helmet,safety_vest",
        "THREAT_THRESHOLD": "0.55",
    }
    
    # Optional alert setup
    setup_alerts = input("\nSetup email/SMS alerts? (y/n): ").lower()
    if setup_alerts == 'y':
        config["TWILIO_ACCOUNT_SID"] = input("Twilio SID (or press Enter to skip): ") or ""
        config["TWILIO_AUTH_TOKEN"] = input("Twilio Token: ") or ""
        config["TWILIO_FROM"] = input("Twilio Phone Number: ") or ""
        config["ALERT_SMS_TO"] = input("Alert recipient phone: ") or ""
        config["SMTP_SERVER"] = input("SMTP Server (e.g., smtp.gmail.com): ") or ""
        config["SMTP_USER"] = input("SMTP User (Email): ") or ""
        config["SMTP_PASS"] = input("SMTP Password (App password for Gmail): ") or ""
        config["ALERT_EMAIL_TO"] = input("Alert recipient email: ") or ""
    
    # Write .env file
    with open(env_file, 'w') as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")
    
    print(f"✓ Configuration saved to {env_file}")

def install_dependencies():
    """Install Python dependencies"""
    print_header("INSTALLING DEPENDENCIES")
    
    if not os.path.exists("requirements.txt"):
        print("✗ requirements.txt not found!")
        return False
    
    print_section("Installing packages from requirements.txt")
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt --upgrade",
        "Installing Python packages..."
    )

def setup_pytorch():
    """Setup PyTorch with appropriate device support"""
    print_header("PYTORCH SETUP")
    
    gpu_support = input("\nSetup GPU support? (y/n): ").lower()
    
    if gpu_support == 'y':
        print_section("Installing PyTorch with CUDA support")
        cmd = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    else:
        print_section("Installing PyTorch CPU-only")
        cmd = f"{sys.executable} -m pip install torch torchvision torchaudio"
    
    return run_command(cmd, "Installing PyTorch...")

def download_models():
    """Download detection models"""
    print_header("MODEL DOWNLOAD")
    
    print_section("Available model sources:")
    print("  1. Local (YOLOv8 auto-download)")
    print("  2. Hugging Face (Recommended - high accuracy)")
    print("  3. Kaggle (Requires authentication)")
    print("  4. All of the above")
    
    choice = input("\nSelect model sources (1-4): ").strip()
    
    if choice in ['1', '4']:
        print_section("Downloading base YOLOv8 models")
        run_command(
            f"{sys.executable} -c \"from ultralytics import YOLO; "
            "[YOLO(f'yolov8{x}.pt') for x in ['n', 's', 'm']]\"",
            "Downloading YOLOv8 models..."
        )
    
    if choice in ['2', '4']:
        print_section("Downloading Hugging Face models")
        run_command(
            f"{sys.executable} download_advanced_models.py",
            "Downloading advanced models..."
        )
    
    if choice in ['3', '4']:
        print_section("Kaggle model download")
        print("Kaggle requires authentication:")
        print("  1. Go to: https://www.kaggle.com/settings/account")
        print("  2. Click 'Create New API Token'")
        print("  3. Place kaggle.json in ~/.kaggle/")
        input("Press Enter once Kaggle is configured...")

def test_installation():
    """Test if installation is working"""
    print_header("TESTING INSTALLATION")
    
    tests = [
        ("Python version", f"{sys.executable} --version"),
        ("OpenCV", f"{sys.executable} -c \"import cv2; print(cv2.__version__)\""),
        ("PyTorch", f"{sys.executable} -c \"import torch; print(f'PyTorch {{torch.__version__}}, CUDA: {{torch.cuda.is_available()}}')\""),
        ("YOLOv8", f"{sys.executable} -c \"from ultralytics import YOLO; print('YOLOv8 ready')\""),
        ("Flask", f"{sys.executable} -c \"import flask; print(flask.__version__)\""),
        ("PPE Detector", f"{sys.executable} -c \"from app.detection.ppe_detector import PPEDetector; print('PPE Detector ready')\""),
    ]
    
    results = []
    for test_name, cmd in tests:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ {test_name}: {result.stdout.strip()}")
                results.append(True)
            else:
                print(f"✗ {test_name}: {result.stderr.strip()}")
                results.append(False)
        except Exception as e:
            print(f"✗ {test_name}: {e}")
            results.append(False)
    
    return all(results)

def show_next_steps():
    """Display next steps"""
    print_header("SETUP COMPLETE!")
    
    print("""
Next steps:

1. Start the application:
   python -m app.run

2. Open in browser:
   http://localhost:5000

3. Check PPE detection:
   - Enable your camera or IP feed
   - Look for red boxes = Missing PPE
   - Look for green boxes = Detected PPE
   - Yellow text = Compliance %

4. Configure alerts:
   Edit .env file to enable SMS/Email notifications

5. Read documentation:
   - PPE_DETECTION_GUIDE.md - Complete PPE feature guide
   - README.md - Project overview
   - WEAPON_DETECTION_TRAINING.md - ML training guide

Quick Test:
   python -c "from app.detection.pipeline import DualYOLOPipeline; p = DualYOLOPipeline(enable_ppe=True); print('✓ PPE pipeline ready!')"

Support:
   - Check logs: app/web/db.py
   - Enable debug: Set FLASK_ENV=development
   - Model issues: download_advanced_models.py
    """)

def main():
    print_header("PROJECT-SPECULA SETUP WITH PPE DETECTION")
    
    print("""
This setup script will help you configure Project-Specula with:
  ✓ PPE (Personal Protective Equipment) Detection
  ✓ Advanced ML models from Kaggle & Hugging Face
  ✓ Real-time threat scoring
  ✓ Automatic alerts via SMS/Email
    """)
    
    proceed = input("\nProceed with setup? (y/n): ").lower()
    if proceed != 'y':
        print("Setup cancelled.")
        sys.exit(0)
    
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Setup PyTorch", setup_pytorch),
        ("Configure Environment", setup_environment),
        ("Download Models", download_models),
        ("Test Installation", test_installation),
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                retry = input(f"\n{step_name} failed. Continue anyway? (y/n): ").lower()
                if retry != 'y':
                    print("Setup aborted.")
                    sys.exit(1)
        except Exception as e:
            print(f"Error during {step_name}: {e}")
            sys.exit(1)
    
    show_next_steps()
    
    print_header("Happy Coding! 🚀")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
