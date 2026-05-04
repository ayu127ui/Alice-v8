#!/usr/bin/env python3
"""
PROJECT-SPECULA: Complete Automated Setup
One-command installation for PPE Detection + Weapon Detection System
Handles: Environment setup, dependencies, models, database, configuration
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

class SpeculaAutoSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.models_dir = self.project_root / "models"
        self.env_file = self.project_root / ".env"
        self.db_file = self.project_root / "smart_cctv.db"
        self.logs = []
        
    def log(self, message, level="INFO"):
        """Log messages with formatting"""
        timestamp = __import__("time").strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_msg)
        print(log_msg)
    
    def success(self, msg):
        self.log(msg, "✓")
    
    def error(self, msg):
        self.log(msg, "✗")
    
    def warning(self, msg):
        self.log(msg, "⚠")
    
    def header(self, text):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {text:^66}")
        print("="*70)
    
    def section(self, text):
        """Print section header"""
        print(f"\n→ {text}")
        print("-" * len(f"→ {text}"))
    
    def run_cmd(self, cmd, description="", silent=False):
        """Run shell command safely"""
        try:
            if description and not silent:
                self.section(description)
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=300,
                cwd=str(self.project_root)
            )
            
            if result.returncode == 0:
                if result.stdout and not silent:
                    print(result.stdout[:200])
                return True
            else:
                if result.stderr:
                    self.error(f"Failed: {result.stderr[:300]}")
                return False
        except subprocess.TimeoutExpired:
            self.error(f"Command timeout: {cmd}")
            return False
        except Exception as e:
            self.error(f"Error: {e}")
            return False
    
    # ========================================================================
    # STEP 1: Check System Requirements
    # ========================================================================
    
    def check_requirements(self):
        """Verify Python version and git"""
        self.header("CHECKING SYSTEM REQUIREMENTS")
        
        # Check Python version
        version = sys.version_info
        if version.major < 3 or version.minor < 8:
            self.error(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        self.success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
        
        # Check git
        if self.run_cmd("git --version", silent=True):
            self.success("Git installed ✓")
        else:
            self.warning("Git not found (optional)")
        
        return True
    
    # ========================================================================
    # STEP 2: Create Project Structure
    # ========================================================================
    
    def create_directories(self):
        """Create required project directories"""
        self.header("CREATING PROJECT STRUCTURE")
        
        directories = [
            self.models_dir,
            self.project_root / "data" / "samples",
            self.project_root / "data" / "screenshots",
            self.project_root / "logs",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.success(f"Directory ready: {directory.name}/")
        
        return True
    
    # ========================================================================
    # STEP 3: Setup Environment
    # ========================================================================
    
    def setup_environment(self):
        """Create .env configuration file"""
        self.header("SETTING UP ENVIRONMENT CONFIGURATION")
        
        if self.env_file.exists():
            response = input("\n.env already exists. Overwrite? (y/n): ").lower()
            if response != 'y':
                self.warning("Keeping existing .env configuration")
                return True
        
        self.section("Configuring environment variables")
        
        # Collect configuration
        config = {
            "# === CAMERA CONFIGURATION ===": "",
            "CAMERA_SOURCE": "0",
            "THREAT_THRESHOLD": "0.55",
            
            "# === PPE DETECTION ===": "",
            "ENABLE_PPE_DETECTION": "True",
            "ENABLE_ADVANCED_MODELS": "True",
            "USE_HUGGINGFACE_MODELS": "True",
            "USE_KAGGLE_MODELS": "False",
            "REQUIRED_PPE": "helmet,safety_vest",
            "PPE_ALERT_COOLDOWN": "60",
            
            "# === DATABASE ===": "",
            "DATABASE_PATH": "smart_cctv.db",
            
            "# === ALERTS (OPTIONAL - leave blank to skip) ===": "",
            "TWILIO_ACCOUNT_SID": "",
            "TWILIO_AUTH_TOKEN": "",
            "TWILIO_FROM": "",
            "ALERT_SMS_TO": "",
            "SMTP_SERVER": "",
            "SMTP_PORT": "587",
            "SMTP_USER": "",
            "SMTP_PASS": "",
            "ALERT_EMAIL_TO": "",
            
            "# === DEBUG ===": "",
            "FLASK_ENV": "development",
            "DEBUG": "False",
        }
        
        # Write configuration
        with open(self.env_file, 'w') as f:
            for key, value in config.items():
                if key.startswith("#"):
                    f.write(f"\n{key}\n")
                else:
                    f.write(f"{key}={value}\n")
        
        self.success(f".env created with default configuration")
        self.log("📝 Edit .env to customize settings (camera URL, alerts, etc.)")
        
        return True
    
    # ========================================================================
    # STEP 4: Install Dependencies
    # ========================================================================
    
    def install_dependencies(self):
        """Install all Python dependencies"""
        self.header("INSTALLING DEPENDENCIES")
        
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            self.error("requirements.txt not found!")
            return False
        
        self.section("Installing Python packages")
        print("This may take 2-5 minutes on first run...")
        
        # Use absolute path and quote paths to handle spaces
        python_exe = f'"{sys.executable}"'
        req_path = str(req_file)
        cmd = f"{python_exe} -m pip install -r \"{req_path}\" --upgrade -q"
        
        if not self.run_cmd(cmd, silent=True):
            self.error("Failed to install dependencies")
            return False
        
        self.success("All Python packages installed ✓")
        return True
    
    # ========================================================================
    # STEP 5: Setup PyTorch
    # ========================================================================
    
    def setup_pytorch(self):
        """Setup PyTorch with appropriate device"""
        self.header("SETTING UP PYTORCH")
        
        self.section("Detecting GPU availability")
        
        try:
            python_exe = f"\"{sys.executable}\""
            result = subprocess.run(
                f"{python_exe} -c \"import torch; print(torch.cuda.is_available())\"",
                shell=True, capture_output=True, text=True, timeout=10,
                cwd=str(self.project_root)
            )
            
            has_gpu = "True" in result.stdout
            
            if has_gpu:
                self.success("GPU detected! Installing CUDA support...")
                cmd = f"{python_exe} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q"
                self.run_cmd(cmd, silent=True)
                self.success("PyTorch with CUDA installed ✓")
            else:
                self.log("No GPU detected - using CPU mode")
                self.log("For GPU support, install CUDA: https://pytorch.org")
            
            # Verify PyTorch
            result = subprocess.run(
                f"{python_exe} -c \"import torch; print(f'PyTorch {{torch.__version__}} - CUDA: {{torch.cuda.is_available()}}')\"",
                shell=True, capture_output=True, text=True, timeout=10,
                cwd=str(self.project_root)
            )
            self.success(f"PyTorch ready: {result.stdout.strip()}")
            
            return True
        except Exception as e:
            self.error(f"PyTorch setup failed: {e}")
            return False
    
    # ========================================================================
    # STEP 6: Download Models
    # ========================================================================
    
    def download_models(self):
        """Download required detection models"""
        self.header("DOWNLOADING DETECTION MODELS")
        
        self.section("Model download strategy")
        print("Models available from:")
        print("  1. Local (auto-download on first use)")
        print("  2. Hugging Face (high accuracy, recommended)")
        print("  3. Both")
        
        choice = input("\nSelect option (1-3, default=3): ").strip() or "3"
        
        # Download Hugging Face models
        if choice in ['2', '3']:
            self.section("Downloading from Hugging Face Hub")
            print("⏳ This may take 5-10 minutes (models are ~100MB each)")
            
            hf_models = {
                "ppe_detection_v8.pt": "keremberke/yolov8m-hard-hat-detection",
                "weapon_detection.pt": "keremberke/yolov8m-weapon-detection",
            }
            
            for local_name, hf_model in hf_models.items():
                output_path = self.models_dir / local_name
                
                if output_path.exists():
                    self.log(f"Model already exists: {local_name}")
                    continue
                
                self.log(f"Downloading {hf_model}...")
                cmd = f"{sys.executable} -c \"from huggingface_hub import hf_hub_download; hf_hub_download('{hf_model}', 'best.pt', local_dir='{self.models_dir}', local_dir_use_symlinks=False)\""
                
                if self.run_cmd(cmd, silent=True):
                    # Find and rename the model
                    for file in self.models_dir.glob("best.pt"):
                        file.rename(output_path)
                        self.success(f"✓ Downloaded: {local_name}")
                        break
        
        # Ensure base YOLOv8 models
        if choice in ['1', '3']:
            self.section("Preparing YOLOv8 base models")
            
            models_to_check = ["yolov8n.pt", "yolov8s.pt"]
            cmd = f"{sys.executable} -c \"from ultralytics import YOLO; [YOLO(m) for m in {models_to_check}]\""
            
            if self.run_cmd(cmd, silent=True):
                self.success("YOLOv8 models ready ✓")
        
        # Count available models
        model_count = len(list(self.models_dir.glob("*.pt")))
        self.success(f"Total models available: {model_count}")
        
        return True
    
    # ========================================================================
    # STEP 7: Setup Database
    # ========================================================================
    
    def setup_database(self):
        """Initialize database"""
        self.header("SETTING UP DATABASE")
        
        self.section("Initializing SQLite database")
        
        try:
            import sqlite3
            
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            
            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    labels TEXT,
                    score REAL,
                    image_path TEXT,
                    metadata TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.success(f"Database initialized: {self.db_file.name}")
            return True
        except Exception as e:
            self.error(f"Database setup failed: {e}")
            return False
    
    # ========================================================================
    # STEP 8: Verify Installation
    # ========================================================================
    
    def verify_installation(self):
        """Test that all components are working"""
        self.header("VERIFYING INSTALLATION")
        
        python_exe = f"\"{sys.executable}\""
        tests = [
            ("Python", f"{python_exe} --version"),
            ("OpenCV", f"{python_exe} -c \"import cv2; print(f'OpenCV {{cv2.__version__}}')\""),
            ("PyTorch", f"{python_exe} -c \"import torch; print(f'PyTorch {{torch.__version__}}')\""),
            ("YOLOv8", f"{python_exe} -c \"from ultralytics import YOLO; print('YOLOv8 OK')\""),
            ("Flask", f"{python_exe} -c \"import flask; print(f'Flask {{flask.__version__}}')\""),
            ("PPE Module", f"{python_exe} -c \"from app.detection.ppe_detector import PPEDetector; print('PPE Module OK')\""),
        ]
        
        passed = 0
        for test_name, cmd in tests:
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, 
                    text=True, timeout=10,
                    cwd=str(self.project_root)
                )
                
                if result.returncode == 0:
                    output = result.stdout.strip()
                    print(f"  ✓ {test_name}: {output}")
                    passed += 1
                else:
                    print(f"  ✗ {test_name}: Failed")
            except Exception as e:
                print(f"  ✗ {test_name}: {str(e)[:50]}")
        
        print(f"\n{passed}/{len(tests)} tests passed")
        
        if passed >= len(tests) - 1:
            self.success("Installation verified ✓")
            return True
        else:
            self.warning("Some tests failed - system may still work")
            return True
    
    # ========================================================================
    # STEP 9: Create Startup Script
    # ========================================================================
    
    def create_startup_scripts(self):
        """Create convenient startup scripts"""
        self.header("CREATING STARTUP SCRIPTS")
        
        # Windows batch script
        batch_script = self.project_root / "start.bat"
        batch_content = """@echo off
cls
echo.
echo ========================================
echo   PROJECT-SPECULA: Starting Application
echo ========================================
echo.
python -m app.run
pause
"""
        
        with open(batch_script, 'w') as f:
            f.write(batch_content)
        self.success("Created: start.bat (Windows)")
        
        # Linux/Mac shell script
        shell_script = self.project_root / "start.sh"
        shell_content = """#!/bin/bash
clear
echo "========================================"
echo "  PROJECT-SPECULA: Starting Application"
echo "========================================"
echo ""
python -m app.run
"""
        
        with open(shell_script, 'w') as f:
            f.write(shell_content)
        os.chmod(shell_script, 0o755)
        self.success("Created: start.sh (Linux/Mac)")
        
        # Python startup script
        py_script = self.project_root / "start.py"
        py_content = """#!/usr/bin/env python3
\"\"\"Quick start script for Project-Specula\"\"\"
import os
import sys
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("\\n" + "="*50)
print("  PROJECT-SPECULA: Starting Application")
print("="*50 + "\\n")

try:
    subprocess.run([sys.executable, "-m", "app.run"], check=True)
except KeyboardInterrupt:
    print("\\n\\nApplication stopped.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
"""
        
        with open(py_script, 'w') as f:
            f.write(py_content)
        os.chmod(py_script, 0o755)
        self.success("Created: start.py (Cross-platform)")
        
        return True
    
    # ========================================================================
    # MAIN: Run Complete Setup
    # ========================================================================
    
    def run_complete_setup(self):
        """Execute all setup steps"""
        self.header("PROJECT-SPECULA: COMPLETE AUTOMATED SETUP")
        
        print("""
This script will automatically:
  ✓ Check system requirements
  ✓ Create project structure
  ✓ Setup environment
  ✓ Install dependencies
  ✓ Setup PyTorch
  ✓ Download models
  ✓ Initialize database
  ✓ Verify installation
  ✓ Create startup scripts

Total time: ~5-10 minutes (depending on internet speed)
        """)
        
        input("Press Enter to start setup...")
        
        steps = [
            ("Checking System", self.check_requirements),
            ("Creating Directories", self.create_directories),
            ("Configuring Environment", self.setup_environment),
            ("Installing Dependencies", self.install_dependencies),
            ("Setting Up PyTorch", self.setup_pytorch),
            ("Downloading Models", self.download_models),
            ("Initializing Database", self.setup_database),
            ("Verifying Installation", self.verify_installation),
            ("Creating Startup Scripts", self.create_startup_scripts),
        ]
        
        completed = 0
        for step_name, step_func in steps:
            try:
                print(f"\n[{completed+1}/{len(steps)}] {step_name}...")
                
                if not step_func():
                    retry = input(f"\n{step_name} failed. Continue anyway? (y/n): ").lower()
                    if retry != 'y':
                        self.error("Setup aborted")
                        return False
                
                completed += 1
            except KeyboardInterrupt:
                self.error("\nSetup interrupted by user")
                return False
            except Exception as e:
                self.error(f"Unexpected error: {e}")
                retry = input("Continue anyway? (y/n): ").lower()
                if retry != 'y':
                    return False
        
        return True
    
    def show_next_steps(self):
        """Display next steps and how to run the app"""
        self.header("SETUP COMPLETE! ✓")
        
        print("""
Your Project-Specula is ready to use!

🚀 TO START THE APPLICATION:

  Option 1 - Windows:
    Double-click: start.bat
    Or in terminal: start.bat

  Option 2 - Linux/Mac:
    ./start.sh
    Or: python start.py

  Option 3 - All platforms:
    python start.py
    Or: python -m app.run

📱 ACCESS THE WEB DASHBOARD:
    http://localhost:5000

⚙️  CONFIGURE SETTINGS:
    1. Edit .env file in project root
    2. Set CAMERA_SOURCE (0 for webcam, or RTSP URL)
    3. Configure alerts (optional)
    4. Customize PPE requirements

📖 DOCUMENTATION:
    - PPE_DETECTION_GUIDE.md - Full feature guide
    - EXAMPLES_PPE_INTEGRATION.py - Code examples
    - README.md - Project overview

🎯 QUICK TEST:
    1. Start the app: python start.py
    2. Open: http://localhost:5000
    3. Enable camera: /video route
    4. Check logs: /logs route
    5. Trigger SOS: /sos route

📊 DATABASE:
    Events logged to: smart_cctv.db
    View logs in web dashboard

💾 FOLDER STRUCTURE:
    models/           - Detection models
    data/screenshots/ - Alert screenshots
    logs/             - Application logs
    .env              - Configuration file

⚠️  FIRST TIME:
    - App will download base YOLOv8 models on first run
    - Internet connection required for model downloads
    - Models cached locally for future runs

❓ NEED HELP?
    - Check PPE_DETECTION_GUIDE.md
    - Review EXAMPLES_PPE_INTEGRATION.py
    - Check app logs for errors
    - Edit .env for configuration

🎉 YOU'RE ALL SET!

Start using Project-Specula with PPE Detection now!
        """)
        
        # Save setup log
        log_file = self.project_root / "setup_log.txt"
        with open(log_file, 'w') as f:
            f.write("Project-Specula Setup Log\n")
            f.write(f"Date: {__import__('datetime').datetime.now()}\n")
            f.write("="*70 + "\n\n")
            for log in self.logs:
                f.write(log + "\n")
        
        print(f"\n📝 Setup log saved to: setup_log.txt")


def main():
    try:
        setup = SpeculaAutoSetup()
        
        if setup.run_complete_setup():
            setup.show_next_steps()
            return 0
        else:
            print("\n❌ Setup failed or was cancelled")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
