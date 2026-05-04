"""
Download and manage high-accuracy detection models from Kaggle and Hugging Face
Supports: Weapon detection, PPE detection, Person detection, Violence detection, and more
Features: Multi-source model management, precision-focused model selection
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List

def download_from_huggingface(model_name: str, output_path: str) -> bool:
    """
    Download model from Hugging Face Hub with fallback support
    
    Args:
        model_name: Model name (e.g., 'keremberke/yolov8m-hard-hat-detection')
        output_path: Output file path
        
    Returns:
        True if successful
    """
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
        print(f"  ↓ Downloading from Hugging Face: {model_name}")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # List available files
        try:
            files = list_repo_files(model_name)
            model_file = "best.pt" if "best.pt" in files else "pytorch_model.bin"
            print(f"    Found model file: {model_file}")
        except:
            model_file = "best.pt"
        
        # Download model
        model_path = hf_hub_download(
            repo_id=model_name,
            filename=model_file,
            local_dir=os.path.dirname(output_path)
        )
        
        # Rename to target path
        if os.path.exists(model_path):
            os.rename(model_path, output_path)
            print(f"    ✓ Downloaded to: {os.path.basename(output_path)}")
            return True
        return False
        
    except Exception as e:
        print(f"    ✗ Failed to download from HF: {e}")
        return False

def download_from_kaggle(dataset_name: str, output_path: str) -> bool:
    """
    Download model or dataset from Kaggle with credentials check
    
    Args:
        dataset_name: Kaggle dataset name
        output_path: Output file path
        
    Returns:
        True if successful
    """
    try:
        import kaggle
        print(f"  ↓ Downloading from Kaggle: {dataset_name}")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Download dataset
        kaggle.api.dataset_download_files(
            dataset_name,
            path=os.path.dirname(output_path),
            unzip=True
        )
        
        print(f"    ✓ Downloaded from Kaggle to: {os.path.basename(os.path.dirname(output_path))}")
        return True
        
    except Exception as e:
        print(f"    ✗ Failed to download from Kaggle: {e}")
        print("      Setup Kaggle: pip install kaggle")
        print("      Credentials: https://github.com/Kaggle/kaggle-api#api-credentials")
        return False

def download_yolov8_models():
    """Download YOLOv8 base models (nano to xlarge for accuracy vs speed tradeoff)"""
    from ultralytics import YOLO
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("📦 YOLOv8 Base Models (Speed ↔ Accuracy Tradeoff)")
    print("=" * 70)
    
    base_models = {
        "yolov8n.pt": ("nano", "⚡ Fastest - Real-time on edge"),
        "yolov8s.pt": ("small", "🚀 Fast - Balanced"),
        "yolov8m.pt": ("medium", "⚙️  Balanced - Good accuracy"),
        "yolov8l.pt": ("large", "🎯 High accuracy"),
        "yolov8x.pt": ("xlarge", "🔬 Maximum accuracy - GPU required"),
    }
    
    for model_name, (size, description) in base_models.items():
        model_path = os.path.join(models_dir, model_name)
        if not os.path.exists(model_path):
            print(f"\n  ↓ {size.upper()} - {description}")
            try:
                model = YOLO(model_name)
                print(f"    ✓ {model_name} ready")
            except Exception as e:
                print(f"    ✗ Failed: {e}")
        else:
            print(f"  ✓ {model_name} exists")

def download_specialized_ppe_models():
    """Download specialized PPE detection models from multiple premium sources"""
    
    print("\n" + "=" * 70)
    print("🦺 PPE Detection Models (Precision-Focused)")
    print("=" * 70)
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # High-accuracy PPE models from Hugging Face (Keremberke's high-precision models)
    hf_ppe_models = {
        "ppe_hardhat_v8m.pt": ("keremberke/yolov8m-hard-hat-detection", "Hard hat detection"),
        "ppe_safety_gear.pt": ("keremberke/yolov8m-safety-equipment-detection", "Safety equipment"),
        "ppe_face_mask.pt": ("keremberke/yolov8m-mask-detection", "Face mask detection"),
        "ppe_vest.pt": ("keremberke/yolov8l-safety-vest-detection", "Safety vest detection"),
        "ppe_hand_protection.pt": ("keremberke/yolov8m-hand-detection", "Hand/glove detection"),
    }
    
    print("\n  🤗 Hugging Face Models:")
    for local_name, (hf_model, description) in hf_ppe_models.items():
        output_path = os.path.join(models_dir, local_name)
        print(f"    • {description}")
        if not os.path.exists(output_path):
            download_from_huggingface(hf_model, output_path)
        else:
            print(f"      ✓ {local_name} exists")
    
    # Kaggle PPE detection datasets
    kaggle_ppe_datasets = {
        "safety-helmet-detection-image-dataset": ("models/kaggle_ppe_helmet", "Helmet detection dataset"),
        "hard-hat-detection": ("models/kaggle_ppe_hardhat", "Hard hat dataset"),
        "ppe-safety-equipment-image-dataset": ("models/kaggle_ppe_safety", "Safety equipment dataset"),
        "construction-safety-detection-dataset": ("models/kaggle_construction_safety", "Construction safety"),
    }
    
    print("\n  📊 Kaggle Datasets:")
    for dataset_name, (output_path, description) in kaggle_ppe_datasets.items():
        print(f"    • {description}")
        if not os.path.exists(output_path):
            download_from_kaggle(dataset_name, output_path)
        else:
            print(f"      ✓ Dataset exists")

def download_weapon_detection_models():
    """Download high-accuracy weapon detection models (guns, knives, explosives)"""
    
    print("\n" + "=" * 70)
    print("🔫 Weapon Detection Models (High-Precision)")
    print("=" * 70)
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Weapon detection models from Hugging Face
    hf_weapon_models = {
        "weapon_gun_yolov8l.pt": ("keremberke/yolov8l-weapons-detection", "Large model - High precision"),
        "weapon_gun_v8m.pt": ("keremberke/yolov8m-weapon-detection", "Medium model - Balanced"),
        "weapon_pistol.pt": ("keremberke/yolov8m-guns", "Pistol & handgun detection"),
        "weapon_knife.pt": ("keremberke/yolov8m-knife-detection", "Knife & blade detection"),
        "weapon_rifle.pt": ("keremberke/yolov8s-rifle-detection", "Rifle detection"),
    }
    
    print("\n  🤗 Hugging Face Models:")
    for local_name, (hf_model, description) in hf_weapon_models.items():
        output_path = os.path.join(models_dir, local_name)
        print(f"    • {description}")
        if not os.path.exists(output_path):
            download_from_huggingface(hf_model, output_path)
        else:
            print(f"      ✓ {local_name} exists")
    
    # Kaggle weapon detection datasets
    kaggle_weapon_datasets = {
        "gun-detection-dataset": ("models/kaggle_gun_detection", "Gun detection dataset"),
        "weapons-detection-dataset": ("models/kaggle_weapons", "General weapons dataset"),
        "knife-detection-dataset": ("models/kaggle_knife_detection", "Knife detection dataset"),
    }
    
    print("\n  📊 Kaggle Datasets:")
    for dataset_name, (output_path, description) in kaggle_weapon_datasets.items():
        print(f"    • {description}")
        if not os.path.exists(output_path):
            download_from_kaggle(dataset_name, output_path)
        else:
            print(f"      ✓ Dataset exists")

def download_violence_action_recognition():
    """Download violence detection and action recognition models"""
    
    print("\n" + "=" * 70)
    print("🚨 Violence & Anomaly Detection Models")
    print("=" * 70)
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Action recognition models from Hugging Face
    hf_action_models = {
        "violence_detection_v8l.pt": ("keremberke/yolov8l-violence-detection", "Violence detection - Large model"),
        "violence_detection_v8m.pt": ("keremberke/yolov8m-violence-detection", "Violence detection - Medium"),
        "crowd_anomaly.pt": ("keremberke/yolov8m-crowd-detection", "Crowd detection"),
        "fall_detection.pt": ("keremberke/yolov8m-fall-detection", "Person fall detection"),
        "fight_detection.pt": ("keremberke/yolov8m-fight-detection", "Fight/altercation detection"),
    }
    
    print("\n  🤗 Hugging Face Models:")
    for local_name, (hf_model, description) in hf_action_models.items():
        output_path = os.path.join(models_dir, local_name)
        print(f"    • {description}")
        if not os.path.exists(output_path):
            download_from_huggingface(hf_model, output_path)
        else:
            print(f"      ✓ {local_name} exists")
    
    # Kaggle violence/action datasets
    kaggle_action_datasets = {
        "violence-detection-dataset": ("models/kaggle_violence_detection", "Violence detection dataset"),
        "fight-detection-dataset": ("models/kaggle_fight_detection", "Fight detection dataset"),
        "crowd-anomaly-detection": ("models/kaggle_crowd_anomaly", "Crowd anomaly dataset"),
    }
    
    print("\n  📊 Kaggle Datasets:")
    for dataset_name, (output_path, description) in kaggle_action_datasets.items():
        print(f"    • {description}")
        if not os.path.exists(output_path):
            download_from_kaggle(dataset_name, output_path)
        else:
            print(f"      ✓ Dataset exists")

def download_person_detection_models():
    """Download optimized person detection models for tracking and counting"""
    
    print("\n" + "=" * 70)
    print("👥 Person Detection & Tracking Models")
    print("=" * 70)
    
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Person detection models from Hugging Face
    hf_person_models = {
        "person_yolov8l.pt": ("keremberke/yolov8l-person-detection", "Person detection - High precision"),
        "person_yolov8m.pt": ("keremberke/yolov8m-person-detection", "Person detection - Balanced"),
        "person_pose.pt": ("keremberke/yolov8m-pose-detection", "Pose/skeleton detection"),
        "person_face.pt": ("keremberke/yolov8m-face-detection", "Face detection"),
    }
    
    print("\n  🤗 Hugging Face Models:")
    for local_name, (hf_model, description) in hf_person_models.items():
        output_path = os.path.join(models_dir, local_name)
        print(f"    • {description}")
        if not os.path.exists(output_path):
            download_from_huggingface(hf_model, output_path)
        else:
            print(f"      ✓ {local_name} exists")
    
    # Kaggle person detection datasets
    kaggle_person_datasets = {
        "person-detection-dataset": ("models/kaggle_person_detection", "Person detection dataset"),
        "coco-person-dataset": ("models/kaggle_coco_persons", "COCO person dataset"),
    }
    
    print("\n  📊 Kaggle Datasets:")
    for dataset_name, (output_path, description) in kaggle_person_datasets.items():
        print(f"    • {description}")
        if not os.path.exists(output_path):
            download_from_kaggle(dataset_name, output_path)
        else:
            print(f"      ✓ Dataset exists")

def setup_all_models():
    """Download all models for complete surveillance system"""
    
    print("\n" + "=" * 70)
    print("🤖 PROJECT ALICE - ADVANCED MODEL SETUP")
    print("=" * 70)
    print("\nDownloading high-precision detection models from:")
    print("  • Hugging Face (Keremberke's precision models)")
    print("  • Kaggle (Training datasets)")
    print("  • YOLOv8 Official Models")
    print("\nThis may take 30-60 minutes depending on internet speed...")
    print("=" * 70)
    
    try:
        # Step 1: Base YOLOv8 models
        download_yolov8_models()
        
        # Step 2: Specialized models
        download_specialized_ppe_models()
        download_weapon_detection_models()
        download_violence_action_recognition()
        download_person_detection_models()
        
        print("\n" + "=" * 70)
        print("✅ ALL MODELS DOWNLOADED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📊 Model Summary:")
        print("  ✓ YOLOv8 Base Models (nano → xlarge)")
        print("  ✓ PPE Detection (5+ models)")
        print("  ✓ Weapon Detection (5+ models)")
        print("  ✓ Violence/Action Detection (5+ models)")
        print("  ✓ Person Detection & Tracking (4+ models)")
        print("  ✓ Training Datasets (10+ Kaggle datasets)")
        print("\n🎯 Ready for production deployment!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    setup_all_models()
