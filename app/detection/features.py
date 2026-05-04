import numpy as np
import cv2

WEAPON_CLASSES = {"knife", "gun", "pistol", "rifle", "firearm", "sword", "axe"}  # Comprehensive weapon classes
PERSON_CLASSES = {"person"}

def motion_magnitude(prev_gray, gray):
    if prev_gray is None:
        return 0.0
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    mag, _ = cv2.cartToPolar(flow[...,0], flow[...,1])
    return float(np.clip(np.mean(mag) / 5.0, 0.0, 1.0))  # normalize

def extract_features(dets, frame, prev_gray):
    # Separate weapon detections with high confidence
    weapon_dets = [d for d in dets if d.get("label", "").lower() in WEAPON_CLASSES]
    
    # Boost confidence for weapon detections
    weapon_conf = sum(d["conf"] for d in weapon_dets)
    
    # Count weapons (threat increases with multiple weapons)
    weapon_count = len(weapon_dets)
    
    people_count = sum(1 for d in dets if d["label"] in PERSON_CLASSES)
    avg_conf = np.mean([d["conf"] for d in dets]) if dets else 0.0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    motion = motion_magnitude(prev_gray, gray)
    
    # spatial density: fraction of frame covered
    h, w = frame.shape[:2]
    area = sum((d["bbox"][2]-d["bbox"][0]) * (d["bbox"][3]-d["bbox"][1]) for d in dets)
    density = float(np.clip(area / (w*h), 0.0, 1.0))
    
    # Enhanced features with weapon count
    feats = np.array([weapon_conf, people_count, avg_conf, motion, density, weapon_count], dtype=np.float32)
    return feats, gray
