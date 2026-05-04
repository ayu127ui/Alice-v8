import cv2
import time
import json
from app.detection.pipeline import DualYOLOPipeline
from app.web.db import LogStore
from app.web.alerts import AlertManager

class Streamer:
    """Enhanced streamer with threat persistence tracking and smart logging"""
    
    def __init__(self, camera_source, threat_threshold, enable_ppe=True, 
                 min_threat_duration=0.5, min_ppe_duration=1.0):
        """
        Initialize streamer with threat persistence tracking
        
        Args:
            camera_source: Video source (webcam index or RTSP URL)
            threat_threshold: Confidence threshold for threats
            enable_ppe: Enable PPE detection
            min_threat_duration: Minimum seconds threat must persist to log (default 0.5s)
            min_ppe_duration: Minimum seconds PPE violation must persist to log (default 1.0s)
        """
        self.source = self._parse_source(camera_source)
        self.threshold = threat_threshold
        self.enable_ppe = enable_ppe
        self.pipeline = DualYOLOPipeline(enable_ppe=enable_ppe)
        self.logger = LogStore()
        self.alerter = AlertManager()
        
        # Threat persistence tracking
        self.threat_frame_count = 0  # Consecutive frames with threat
        self.ppe_violation_frame_count = 0  # Consecutive frames with PPE violation
        self.min_threat_frames = int(min_threat_duration * 30)  # ~30 FPS assumed
        self.min_ppe_frames = int(min_ppe_duration * 30)
        
        # Last logged times (for alert rate limiting)
        self._last_alert_ts = 0
        self._last_ppe_alert_ts = 0
        self._last_threat_log_ts = 0  # Time of last threat log
        self._last_ppe_log_ts = 0     # Time of last PPE log
        
        # Alert cooldowns
        self.alert_cooldown = 30  # Threat alerts every 30 seconds max
        self.ppe_alert_cooldown = 60  # PPE alerts every 60 seconds max
        self.log_cooldown = 2  # Don't log same threat more than every 2 seconds
        
        print(f"✓ Streamer initialized")
        print(f"  Threat persistence: {min_threat_duration}s ({self.min_threat_frames} frames)")
        print(f"  PPE persistence: {min_ppe_duration}s ({self.min_ppe_frames} frames)")
        print(f"  Alert cooldown: {self.alert_cooldown}s | Log cooldown: {self.log_cooldown}s")

    def _parse_source(self, src):
        try:
            return int(src)
        except ValueError:
            return src  # RTSP/http URL

    def frame_generator(self):
        """Generate video stream with detection overlays and smart threat logging"""
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera source: {self.source}")

        frame_count = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.02)
                continue

            frame_count += 1
            
            # Process frame with all detections
            result = self.pipeline.process(frame)
            
            score = result["score"]
            overlay = result["overlay"]
            labels = result["labels"]
            ppe_violations = result.get("ppe_violations", [])
            ppe_dets = result.get("ppe_dets", [])

            # ============ THREAT DETECTION LOGGING ============
            if score >= self.threshold:
                # Increment threat persistence counter
                self.threat_frame_count += 1
                
                # Log threat only when persistence threshold is reached
                if self.threat_frame_count == self.min_threat_frames:
                    now = time.time()
                    # Rate-limit logging to avoid duplicate entries
                    if now - self._last_threat_log_ts > self.log_cooldown:
                        event_data = {
                            "type": "threat",
                            "score": score,
                            "labels": labels,
                            "persistence_frames": self.threat_frame_count,
                            "weapons_detected": [d["label"] for d in result["dets"] 
                                                if d["label"] in ["knife", "gun", "sword", "firearm", "pistol", "rifle", "axe"]]
                        }
                        self.logger.log_event(labels, score, overlay)
                        self._last_threat_log_ts = now
                        
                        print(f"🚨 THREAT LOGGED: {labels} (score: {score:.2f}, frames: {self.threat_frame_count})")
                
                # Send alert when threat becomes persistent
                if self.threat_frame_count == self.min_threat_frames:
                    now = time.time()
                    if now - self._last_alert_ts > self.alert_cooldown:
                        self.alerter.send_auto_alert(score, labels)
                        self._last_alert_ts = now
                        print(f"⚠️  THREAT ALERT SENT")
            else:
                # Reset threat counter when threat disappears
                if self.threat_frame_count > 0:
                    print(f"✓ Threat cleared (was present for {self.threat_frame_count} frames / {self.threat_frame_count/30:.2f}s)")
                self.threat_frame_count = 0

            # ============ PPE VIOLATION LOGGING ============
            if self.enable_ppe and ppe_violations:
                critical_violations = [v for v in ppe_violations if not v["all_required_met"]]
                
                if critical_violations:
                    # Increment PPE violation counter
                    self.ppe_violation_frame_count += 1
                    
                    # Calculate PPE compliance score
                    avg_compliance = sum(v["compliance_score"] for v in critical_violations) / len(critical_violations)
                    
                    # Log PPE violations only when persistence threshold is reached
                    if self.ppe_violation_frame_count == self.min_ppe_frames:
                        now = time.time()
                        # Rate-limit logging
                        if now - self._last_ppe_log_ts > self.log_cooldown:
                            event_data = {
                                "type": "ppe_violation",
                                "violations_count": len(critical_violations),
                                "missing_ppe": list(set(
                                    ppe for v in critical_violations 
                                    for ppe in v["missing_ppe"]
                                )),
                                "avg_compliance": avg_compliance,
                                "persistence_frames": self.ppe_violation_frame_count
                            }
                            
                            # Log PPE violations
                            self.logger.log_event(
                                ["PPE_VIOLATION"] + event_data["missing_ppe"],
                                avg_compliance,
                                overlay
                            )
                            self._last_ppe_log_ts = now
                            
                            print(f"⛑️  PPE VIOLATION LOGGED: {event_data['missing_ppe']} (frames: {self.ppe_violation_frame_count})")
                    
                    # Send PPE alert when violation becomes persistent
                    if self.ppe_violation_frame_count == self.min_ppe_frames:
                        now = time.time()
                        if now - self._last_ppe_alert_ts > self.ppe_alert_cooldown:
                            self.alerter.send_ppe_alert(event_data)
                            self._last_ppe_alert_ts = now
                            print(f"⚠️  PPE ALERT SENT")
                else:
                    # Reset PPE counter when violations disappear
                    if self.ppe_violation_frame_count > 0:
                        print(f"✓ PPE compliance restored (violation was present for {self.ppe_violation_frame_count} frames / {self.ppe_violation_frame_count/30:.2f}s)")
                    self.ppe_violation_frame_count = 0
            else:
                # Reset PPE counter when no violations
                if self.ppe_violation_frame_count > 0 and self.enable_ppe:
                    print(f"✓ PPE compliance restored (violation was present for {self.ppe_violation_frame_count} frames / {self.ppe_violation_frame_count/30:.2f}s)")
                self.ppe_violation_frame_count = 0

            ret, buf = cv2.imencode(".jpg", overlay)
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")
