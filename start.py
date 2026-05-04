#!/usr/bin/env python3
"""Quick start script for Project-Specula"""
import os
import sys
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*50)
print("  PROJECT-SPECULA: Starting Application")
print("="*50 + "\n")

try:
    subprocess.run([sys.executable, "-m", "app.run"], check=True)
except KeyboardInterrupt:
    print("\n\nApplication stopped.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
