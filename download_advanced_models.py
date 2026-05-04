"""
Download and manage high-accuracy detection models from Kaggle and Hugging Face
Supports: Weapon detection, PPE detection, Person detection, and Violence detection
"""

import os
import sys
from pathlib import Path
from typing import Optional

def download_from_huggingface(model_name: str, output_path: str) -> bool:
    """
    Download model from Hugging Face Hub
    
    Args:
        model_name: Model name (e.g., 'keremberke/yolov8m-hard-hat-detection')
        output_path: Output file path
        
    Returns:
        True if successful
    """
    try:
        from huggingface_hub import hf_hub_download
        print(f"Downloading from Hugging Face: {model_name}")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download model
        model_path = hf_hub_download(
            repo_id=model_name,
            filename="best.pt",
            local_dir=os.path.dirname(output_path)
        )
        
        # Rename to target path
        if os.path.exists(model_path):
            os.rename(model_path, output_path)
            print(f"✓ Downloaded to: {output_path}")
            return True
        return False
        
    except Exception as e:
        print(f"✗ Failed to download from HF: {e}")
        return False

def download_from_kaggle(dataset_name: str, output_path: str) -> bool:
    """
    Download model from Kaggle
    
    Args:
        dataset_name: Kaggle dataset name
        output_path: Output file path
        
    Returns:
        True if successful
    """
    try:
        import kaggle
        print(f"Downloading from Kaggle: {dataset_name}")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download dataset
        kaggle.api.dataset_download_files(
            dataset_name,
            path=os.path.dirname(output_path),
            unzip=True
        )
        
        print(f"✓ Downloaded from Kaggle to: {os.path.dirname(output_path)}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to download from Kaggle: {e}")
        print("  Install Kaggle: pip install kaggle")
        print("  Configure credentials: https://github.com/Kaggle/kaggle-api")
        return False

def download_yolov8_models():
    """Download YOLOv8 base models"""
    from ultralytics import YOLO
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    print("=" * 60)
    print("Downloading YOLOv8 Base Models")
    print("=" * 60)
    
    base_models = {
        "yolov8n.pt": "nano",
        "yolov8s.pt": "small",
        "yolov8m.pt": "medium"
    }
    
    for model_name, size in base_models.items():
        model_path = os.path.join(models_dir, model_name)
        if not os.path.exists(model_path):
            print(f"\n→ Downloading YOLOv8 {size}...")
            try:
                model = YOLO(model_name)
                print(f"✓ YOLOv8 {size} ready")
            except Exception as e:
                print(f"✗ Failed: {e}")
        else:
            print(f"✓ {model_name} exists")

def download_specialized_ppe_models():
    """Download specialized PPE detection models from multiple sources"""
    
    print("\n" + "=" * 60)
    print("Downloading Specialized PPE Detection Models")
    print("=" * 60)
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # High-accuracy PPE models from Hugging Face
    hf_ppe_models = {
        "ppe_detection_v8.pt": "keremberke/yolov8m-hard-hat-detection",
        "ppe_detection_advanced.pt": "keremberke/yolov8m-safety-equipment-detection",
    }
    
    print("\n→ Hugging Face PPE Models:")
    for local_name, hf_model in hf_ppe_models.items():
        output_path = os.path.join(models_dir, local_name)
        download_from_huggingface(hf_model, output_path)
    
    # Kaggle PPE datasets
    kaggle_datasets = {
        "ppe-dataset-hard-hat-detection": "models/kaggle_ppe_hardhat",
        "safety-equipment-detection": "models/kaggle_ppe_safety",
    }
    
    print("\n→ Kaggle PPE Models:")
    for dataset_name, output_path in kaggle_datasets.items():
        download_from_kaggle(dataset_name, output_path)

def download_weapon_detection_models():
    """Download high-accuracy weapon detection models"""
    
    print("\n" + "=" * 60)
    print("Downloading Weapon Detection Models")
    print("=" * 60)
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Weapon detection models
    hf_weapon_models = {
        "weapon_detection.pt": "keremberke/yolov8m-weapon-detection",
        "gun_detection.pt": "keremberke/yolov8s-guns",
    }
    
    print("\n→ Hugging Face Weapon Models:")
    for local_name, hf_model in hf_weapon_models.items():
        output_path = os.path.join(models_dir, local_name)
        download_from_huggingface(hf_model, output_path)

def download_violence_action_recognition():
    """Download violence and action recognition models"""
    
    print("\n" + "=" * 60)
    print("Downloading Violence/Action Detection Models")
    print("=" * 60)
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Action recognition models
    hf_action_models = {
        "violence_detection.pt": "keremberke/yolov8m-violence-detection",
        "crowd_detection.pt": "keremberke/yolov8m-crowd-detection",
    }
    
    print("\n→ Hugging Face Action Models:")
    for local_name, hf_model in hf_action_models.items():
        output_path = os.path.join(models_dir, local_name)
        download_from_huggingface(hf_model, output_path)

def download_person_detection_models():
    """Download optimized person detection models"""
    
    print("\n" + "=" * 60)
    print("Downloading Person Detection Models")
    print("=" * 60)
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Person detection models
    hf_person_models = {
        "person_enhanced.pt": "keremberke/yolov8m-person-detection",
    }
    
    print("\n→ Hugging Face Person Models:")
    for local_name, hf_model in hf_person_models.items():
        output_path = os.path.join(models_dir, local_name)
        download_from_huggingface(hf_model, output_path)

def setup_all_models():
    """Download all models for complete system"""
    
    print("\n" + "=" * 60)
    print("SPECULA - Complete Model Setup")
    print("=" * 60)
    print("\nDownloading high-accuracy detection models...")
    print("This may take several minutes...\n")
    
    try:
        # Download base YOLOv8 models
        download_yolov8_models()
        
        # Download specialized models
        download_specialized_ppe_models()
        download_weapon_detection_models()
        download_violence_action_recognition()
        download_person_detection_models()
        
        print("\n" + "=" * 60)
        print("✓ All models downloaded successfully!")
        print("=" * 60)
        print("\nModels ready for use in Project-Specula")
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_all_models()
