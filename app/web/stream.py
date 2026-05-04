import cv2
import time
import json
from app.detection.pipeline import DualYOLOPipeline
from app.web.db import LogStore
from app.web.alerts import AlertManager

class Streamer:
    """Enhanced streamer with PPE detection support"""
    
    def __init__(self, camera_source, threat_threshold, enable_ppe=True):
        self.source = self._parse_source(camera_source)
        self.threshold = threat_threshold
        self.enable_ppe = enable_ppe
        self.pipeline = DualYOLOPipeline(enable_ppe=enable_ppe)
        self.logger = LogStore()
        self.alerter = AlertManager()
        self._last_alert_ts = 0
        self._last_ppe_alert_ts = 0
        self.ppe_alert_cooldown = 60  # PPE alerts every 60 seconds max

    def _parse_source(self, src):
        try:
            return int(src)
        except ValueError:
            return src  # RTSP/http URL

    def frame_generator(self):
        """Generate video stream with detection overlays"""
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera source: {self.source}")

        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.02)
                continue

            # Process frame with all detections
            result = self.pipeline.process(frame)
            
            score = result["score"]
            overlay = result["overlay"]
            labels = result["labels"]
            ppe_violations = result.get("ppe_violations", [])
            ppe_dets = result.get("ppe_dets", [])

            # Log weapon/threat detections
            if score >= self.threshold:
                event_data = {
                    "type": "threat",
                    "score": score,
                    "labels": labels,
                    "weapons_detected": [d["label"] for d in result["dets"] 
                                        if d["label"] in ["knife", "gun", "sword", "firearm", "pistol", "rifle", "axe"]]
                }
                self.logger.log_event(labels, score, overlay)
                
                now = time.time()
                if now - self._last_alert_ts > 30:  # Rate-limit threats
                    self.alerter.send_auto_alert(score, labels)
                    self._last_alert_ts = now

            # Log PPE violations
            if self.enable_ppe and ppe_violations:
                critical_violations = [v for v in ppe_violations if not v["all_required_met"]]
                
                if critical_violations:
                    # Calculate PPE compliance score
                    avg_compliance = sum(v["compliance_score"] for v in critical_violations) / len(critical_violations)
                    
                    event_data = {
                        "type": "ppe_violation",
                        "violations_count": len(critical_violations),
                        "missing_ppe": list(set(
                            ppe for v in critical_violations 
                            for ppe in v["missing_ppe"]
                        )),
                        "avg_compliance": avg_compliance
                    }
                    
                    # Log PPE violations
                    self.logger.log_event(
                        ["PPE_VIOLATION"] + event_data["missing_ppe"],
                        avg_compliance,
                        overlay
                    )
                    
                    # Send PPE violation alert
                    now = time.time()
                    if now - self._last_ppe_alert_ts > self.ppe_alert_cooldown:
                        self.alerter.send_ppe_alert(event_data)
                        self._last_ppe_alert_ts = now

            ret, buf = cv2.imencode(".jpg", overlay)
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")
