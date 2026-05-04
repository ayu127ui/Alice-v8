import cv2
import os
import numpy as np
from app.detection.models import YOLOModel, WeaponDetector
from app.detection.ppe_detector import PPEDetector
from app.detection.features import extract_features, WEAPON_CLASSES
from app.detection.fusion import MLPSynthesizer

class DualYOLOPipeline:
    """Enhanced detection pipeline with weapon + PPE detection from multiple model sources"""
    
    def __init__(self, enable_ppe: bool = True, use_advanced_models: bool = True):
        """
        Initialize pipeline with base and specialized models
        
        Args:
            enable_ppe: Enable PPE detection
            use_advanced_models: Use Kaggle/HF models if available
        """
        # Two complementary models (speed + accuracy)
        self.fast = YOLOModel("models/yolov8n.pt", conf=0.35, iou=0.45)
        self.accurate = WeaponDetector("models/yolov8s.pt", conf=0.45, iou=0.5)
        
        # Initialize PPE detector if enabled
        self.enable_ppe = enable_ppe
        self.ppe_detector = None
        if enable_ppe:
            ppe_model_path = self._get_best_ppe_model()
            if ppe_model_path and os.path.exists(ppe_model_path):
                self.ppe_detector = PPEDetector(ppe_model_path, conf=0.4, iou=0.5)
            else:
                print("⚠ PPE model not found. Using default YOLOv8s")
                self.ppe_detector = PPEDetector("models/yolov8s.pt", conf=0.4, iou=0.5)
        
        # Advanced weapon detection if available
        self.weapon_detector_advanced = None
        if use_advanced_models:
            weapon_model = self._get_best_weapon_model()
            if weapon_model and os.path.exists(weapon_model):
                try:
                    self.weapon_detector_advanced = YOLOModel(weapon_model, conf=0.4, iou=0.5)
                except:
                    pass
        
        # Fusion and feature extraction
        self.fuser = MLPSynthesizer()
        self.prev_gray = None

    def _get_best_ppe_model(self) -> str:
        """Get best available PPE model (priority: Kaggle > HF > Local)"""
        priority_models = [
            "models/ppe_detection_advanced.pt",
            "models/ppe_detection_v8.pt",
            "models/kaggle_ppe_safety/best.pt",
            "models/kaggle_ppe_hardhat/best.pt",
        ]
        for model in priority_models:
            if os.path.exists(model):
                print(f"✓ Using PPE model: {model}")
                return model
        return None

    def _get_best_weapon_model(self) -> str:
        """Get best available weapon model"""
        priority_models = [
            "models/weapon_detection.pt",
            "models/gun_detection.pt",
        ]
        for model in priority_models:
            if os.path.exists(model):
                print(f"✓ Using advanced weapon model: {model}")
                return model
        return None

    def _ensemble(self, dets_a, dets_b, dets_c=None):
        """Merge detections from multiple sources with confidence weighting"""
        # Combine all detections
        all_dets = dets_a + dets_b
        if dets_c:
            all_dets += dets_c
        
        # Remove duplicates with NMS
        if all_dets:
            all_dets = self._nms_detections(all_dets)
        
        return all_dets

    def _nms_detections(self, dets, iou_threshold=0.5):
        """Non-Maximum Suppression for overlapping detections"""
        if not dets:
            return dets
        
        # Sort by confidence
        dets = sorted(dets, key=lambda x: x["conf"], reverse=True)
        
        keep = []
        remove_indices = set()
        
        for i, det1 in enumerate(dets):
            if i in remove_indices:
                continue
            
            keep.append(det1)
            x1_1, y1_1, x2_1, y2_1 = det1["bbox"]
            area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
            
            for j in range(i + 1, len(dets)):
                if j in remove_indices:
                    continue
                
                det2 = dets[j]
                x1_2, y1_2, x2_2, y2_2 = det2["bbox"]
                
                # Calculate IoU
                x1_int = max(x1_1, x1_2)
                y1_int = max(y1_1, y1_2)
                x2_int = min(x2_1, x2_2)
                y2_int = min(y2_1, y2_2)
                
                if x2_int > x1_int and y2_int > y1_int:
                    inter_area = (x2_int - x1_int) * (y2_int - y1_int)
                    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
                    union_area = area1 + area2 - inter_area
                    iou = inter_area / union_area if union_area > 0 else 0
                    
                    if iou > iou_threshold:
                        remove_indices.add(j)
        
        return keep

    def _draw(self, frame, dets, score, ppe_dets=None, ppe_violations=None):
        """Draw all detections and violations on frame"""
        # Draw weapon detections
        for d in dets:
            x1, y1, x2, y2 = d["bbox"]
            label = d["label"]
            conf = d["conf"]
            is_weapon = label in WEAPON_CLASSES
            
            # Red for weapons, green for persons
            color = (0, 0, 255) if is_weapon else (0, 200, 0)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Draw PPE detections
        if ppe_dets:
            for ppe in ppe_dets:
                x1, y1, x2, y2 = ppe["bbox"]
                label = ppe["label"]
                conf = ppe["conf"]
                
                # Cyan for PPE
                color = (255, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Draw PPE violations
        if ppe_violations:
            for violation in ppe_violations:
                if not violation["all_required_met"]:
                    x1, y1, x2, y2 = violation["person_bbox"]
                    missing = ", ".join(violation["missing_ppe"][:1])
                    compliance_pct = int(violation["compliance_score"] * 100)
                    
                    # Red box for violations
                    color = (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                    text = f"No {missing} ({compliance_pct}%)"
                    cv2.putText(frame, text, (x1, y1 - 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw threat score
        threat_color = (0, 0, 255) if score > 0.6 else (0, 255, 255) if score > 0.3 else (0, 255, 0)
        cv2.putText(frame, f"Threat: {score:.2f}", (18, 28),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, threat_color, 2)
        
        return frame

    def process(self, frame):
        """
        Process frame with all detection models
        
        Returns:
            {
                "dets": weapon/person detections,
                "ppe_dets": PPE detections,
                "ppe_violations": PPE compliance violations,
                "score": overall threat score,
                "overlay": annotated frame,
                "labels": unique detection labels
            }
        """
        # Weapon detection
        dets_fast = self.fast.predict(frame)
        dets_acc = self.accurate.predict(frame)
        dets_adv = self.weapon_detector_advanced.predict(frame) if self.weapon_detector_advanced else []
        
        # Ensemble all weapon detections
        dets = self._ensemble(dets_fast, dets_acc, dets_adv)
        
        # PPE detection
        ppe_dets = []
        ppe_violations = []
        if self.enable_ppe and self.ppe_detector:
            ppe_dets = self.ppe_detector.predict(frame)
            
            # Check PPE compliance for persons
            for det in dets:
                if det["label"] == "person":
                    compliance = self.ppe_detector.check_compliance(
                        det["bbox"], ppe_dets, frame.shape[0], frame.shape[1]
                    )
                    compliance["person_bbox"] = det["bbox"]
                    ppe_violations.append(compliance)
        
        # Extract features
        features, gray = extract_features(dets, frame, self.prev_gray)
        self.prev_gray = gray
        
        # Calculate threat score
        score = self.fuser.score(features)
        
        # Add PPE violation threat
        if ppe_violations:
            ppe_threat = self.ppe_detector.get_ppe_threat_score(ppe_violations)
            score = min(score + ppe_threat * 0.3, 1.0)  # PPE threat adds up to 30%
        
        labels = sorted(set(d["label"] for d in dets))
        overlay = self._draw(frame.copy(), dets, score, ppe_dets, ppe_violations)
        
        return {
            "dets": dets,
            "ppe_dets": ppe_dets,
            "ppe_violations": ppe_violations,
            "score": score,
            "overlay": overlay,
            "labels": labels
        }
 