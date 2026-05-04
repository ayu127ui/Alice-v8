from ultralytics import YOLO
import numpy as np
import cv2

class YOLOModel:
    def __init__(self, model_path, conf=0.35, iou=0.45):
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou

    def predict(self, frame):
        results = self.model.predict(source=frame, conf=self.conf, iou=self.iou, verbose=False)
        dets = []
        for r in results:
            for b in r.boxes:
                cls_id = int(b.cls)
                label = r.names[cls_id]
                conf = float(b.conf)
                x1, y1, x2, y2 = map(int, b.xyxy[0])
                dets.append({"label": label, "conf": conf, "bbox": (x1, y1, x2, y2)})
        return dets

class WeaponDetector:
    """Specialized weapon detection with advanced accuracy for guns and knives"""
    def __init__(self, model_path, conf=0.45, iou=0.5):
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        self.weapon_classes = {"knife", "gun", "sword", "axe", "firearm", "pistol", "rifle"}
        self.false_positives = {"scissors", "fork", "spoon", "stick", "cane", "umbrella", "bat"}
        
    def _is_knife_shape(self, bbox, frame):
        """Verify knife detection by analyzing object shape characteristics"""
        x1, y1, x2, y2 = bbox
        height = y2 - y1
        width = x2 - x1
        aspect_ratio = height / (width + 1e-5)
        
        # Knives typically have high aspect ratio (long and thin)
        # Scissors have similar blade area but different curvature
        return aspect_ratio > 2.0
    
    def _is_gun_shape(self, bbox):
        """Verify gun detection by analyzing object shape"""
        x1, y1, x2, y2 = bbox
        height = y2 - y1
        width = x2 - x1
        aspect_ratio = height / (width + 1e-5)
        
        # Guns typically have aspect ratio between 0.5-1.5 (wider, compact)
        return 0.3 < aspect_ratio < 2.0
        
    def predict(self, frame):
        results = self.model.predict(source=frame, conf=self.conf, iou=self.iou, verbose=False)
        dets = []
        for r in results:
            for b in r.boxes:
                cls_id = int(b.cls)
                label = r.names[cls_id].lower()
                conf = float(b.conf)
                x1, y1, x2, y2 = map(int, b.xyxy[0])
                bbox = (x1, y1, x2, y2)
                
                # Filter out false positives
                if label in self.false_positives:
                    continue
                
                # Enhanced weapon detection with shape verification
                if label == "knife":
                    # High confidence + shape verification for knives
                    if conf >= 0.45 and self._is_knife_shape(bbox, frame):
                        dets.append({"label": "knife", "conf": min(conf * 1.1, 1.0), "bbox": bbox, "weapon": True})
                    elif conf >= 0.60:  # Very high confidence, no shape check needed
                        dets.append({"label": "knife", "conf": conf, "bbox": bbox, "weapon": True})
                        
                elif label in ["gun", "pistol", "rifle", "firearm"]:
                    # Enhanced gun detection
                    if conf >= 0.50 and self._is_gun_shape(bbox):
                        dets.append({"label": label, "conf": min(conf * 1.15, 1.0), "bbox": bbox, "weapon": True})
                    elif conf >= 0.65:  # Very high confidence
                        dets.append({"label": label, "conf": conf, "bbox": bbox, "weapon": True})
                        
                elif label in ["sword", "axe"]:
                    if conf >= 0.45:
                        dets.append({"label": label, "conf": conf, "bbox": bbox, "weapon": True})
                        
                else:
                    # Non-weapon objects
                    if conf >= self.conf:  # Standard threshold
                        dets.append({"label": label, "conf": conf, "bbox": bbox, "weapon": False})
        
        return dets
