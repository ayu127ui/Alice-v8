import cv2
import time
from app.detection.pipeline import DualYOLOPipeline
from app.detection.threat_scorer import ThreatScorer
from app.web.db import LogStore

pipeline = DualYOLOPipeline()
scorer = ThreatScorer()
logger = LogStore()

def get_camera_source(src):
    try:
        return int(src)
    except ValueError:
        return src  # IP cam URL

def frames(camera_source, threat_threshold):
    cap = cv2.VideoCapture(get_camera_source(camera_source))
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera source")

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.05)
            continue

        result = pipeline.process(frame)
        dets = result['dets']
        score = scorer.score_frame(dets)
        overlay = result['overlay']
        labels = result['labels']

        if score >= threat_threshold:
            logger.log_event(labels, score, overlay)

        ret, buffer = cv2.imencode('.jpg', overlay)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
