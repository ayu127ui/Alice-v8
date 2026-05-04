# ⚡ Quick Reference: Configuration & Models

## 🎯 Threat Persistence Settings

### Environment Variables
```bash
# How long threat must persist before logging (seconds)
MIN_THREAT_DURATION=0.5

# How long PPE violation must persist before logging (seconds)
MIN_PPE_DURATION=1.0

# Minimum seconds between logging same threat
THREAT_LOG_COOLDOWN=2

# Minimum seconds between threat alerts
THREAT_ALERT_COOLDOWN=30

# Minimum seconds between PPE alerts
PPE_ALERT_COOLDOWN=60
```

### Frame Equivalents (at 30fps)
| Duration | Frames | Quality |
|----------|--------|---------|
| 0.2s | 6 | Very fast (false positives) |
| 0.3s | 9 | Fast |
| 0.5s | 15 | **Balanced (default)** |
| 1.0s | 30 | Strict |
| 2.0s | 60 | Very strict |
| 3.0s | 90 | Extreme |

---

## 📊 Model Categories

### 🎯 YOLOv8 Base (Speed-Accuracy)
```
Fast:     yolov8n.pt  (nano, edge)
↓
Balanced: yolov8s.pt  (small, **default**)
↓
Accurate: yolov8m.pt  (medium)
↓
Precise:  yolov8l.pt  (large)
↓
Expert:   yolov8x.pt  (xlarge, GPU)
```

### 🦺 PPE Detection
- `ppe_hardhat_v8m.pt` - Hard hat detection
- `ppe_safety_gear.pt` - Safety equipment
- `ppe_face_mask.pt` - Face masks
- `ppe_vest.pt` - Safety vests
- `ppe_hand_protection.pt` - Gloves

### 🔫 Weapon Detection
- `weapon_gun_yolov8l.pt` - General weapons (high precision)
- `weapon_gun_v8m.pt` - General weapons (balanced)
- `weapon_pistol.pt` - Handguns
- `weapon_knife.pt` - Blades
- `weapon_rifle.pt` - Rifles

### 🚨 Violence/Anomaly
- `violence_detection_v8l.pt` - Violence (high precision)
- `violence_detection_v8m.pt` - Violence (balanced)
- `crowd_anomaly.pt` - Crowd detection
- `fall_detection.pt` - Person falls
- `fight_detection.pt` - Fights/altercations

### 👥 Person Detection
- `person_yolov8l.pt` - Person detection (precise)
- `person_yolov8m.pt` - Person detection (balanced)
- `person_pose.pt` - Pose/skeleton
- `person_face.pt` - Face detection

---

## 🔧 Preset Configurations

### 🔐 High Security (Banks, Secure Facilities)
```env
MIN_THREAT_DURATION=0.3
MIN_PPE_DURATION=0.5
THREAT_THRESHOLD=0.70
THREAT_ALERT_COOLDOWN=15
PPE_ALERT_COOLDOWN=30
```

### ⚖️ Balanced (General Use - **RECOMMENDED**)
```env
MIN_THREAT_DURATION=0.5
MIN_PPE_DURATION=1.0
THREAT_THRESHOLD=0.55
THREAT_ALERT_COOLDOWN=30
PPE_ALERT_COOLDOWN=60
```

### 🏭 Busy Environments (Factories, Malls)
```env
MIN_THREAT_DURATION=1.5
MIN_PPE_DURATION=3.0
THREAT_THRESHOLD=0.65
THREAT_ALERT_COOLDOWN=60
PPE_ALERT_COOLDOWN=120
```

### 📱 Low-Power Devices
```env
CAMERA_SOURCE=0
# Use smaller models
MIN_THREAT_DURATION=1.0
THREAT_THRESHOLD=0.60
```

---

## 📥 Download Commands

```bash
# Download ALL models (30-60 min, 10-15GB)
python download_advanced_models.py

# Download specific category
python -c "from download_advanced_models import download_weapon_detection_models; download_weapon_detection_models()"

# Check if models exist
ls models/
```

---

## 🚀 Launch Commands

```bash
# Start the system
python start.py

# Or directly:
python app/run.py

# With custom camera:
CAMERA_SOURCE=rtsp://192.168.1.100/stream python start.py

# With custom threshold:
THREAT_THRESHOLD=0.60 python start.py
```

---

## 📊 Console Output Examples

### Threat Detected & Logged
```
🚨 THREAT LOGGED: ['gun'] (score: 0.87, frames: 15)
⚠️  THREAT ALERT SENT
```

### Threat Disappeared
```
✓ Threat cleared (was present for 45 frames / 1.5s)
```

### PPE Violation Logged
```
⛑️  PPE VIOLATION LOGGED: ['helmet'] (frames: 30)
⚠️  PPE ALERT SENT
```

### PPE Compliance Restored
```
✓ PPE compliance restored (violation was present for 60 frames / 2.0s)
```

---

## 🔍 Debugging

### Check Persistent Frames
```python
from app.web.stream import Streamer
streamer = Streamer("0", 0.55)
print(f"Threat frames: {streamer.threat_frame_count}")
print(f"Min threat frames: {streamer.min_threat_frames}")
print(f"PPE frames: {streamer.ppe_violation_frame_count}")
```

### Test Model Download
```bash
python -c "
from download_advanced_models import download_from_huggingface
download_from_huggingface('keremberke/yolov8m-weapon-detection', 'models/test.pt')
"
```

### View Logged Events
```python
from app.web.db import LogStore
logger = LogStore()
events = logger.get_events(limit=10)
for e in events:
    print(f\"{e['timestamp']}: {e['labels']} (score: {e['score']})\")
```

---

## ❌ Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Threats not logged | `MIN_THREAT_DURATION=0.2` |
| Too many false alerts | `THREAT_THRESHOLD=0.65` |
| Too many PPE logs | `MIN_PPE_DURATION=2.0` |
| Slow detection | Use `yolov8n.pt` or `yolov8s.pt` |
| High CPU | Disable PPE or use smaller model |
| Models not found | Run `python download_advanced_models.py` |
| Out of memory | Use smaller models (nano/small) |
| Alerts not sending | Check `THREAT_ALERT_COOLDOWN` |

---

## 📈 Storage Estimates

| Duration | Threats/Hour | Screenshots | Size |
|----------|-------------|-------------|------|
| 0.3s | 10 | 10-20 | ~5MB |
| 0.5s | 10 | 10-30 | ~7MB |
| 1.0s | 10 | 10-20 | ~5MB |
| 2.0s | 10 | 10-15 | ~3MB |

**Total:** ~20MB/day (vs 100MB/day before)

---

## 🎨 Model Selection Guide

### For Maximum Speed
```
yolov8n.pt (nano)
↓
Best for: Edge devices, real-time web
Trade-off: Lower accuracy (~80%)
```

### For Best Balance (⭐ RECOMMENDED)
```
yolov8s.pt (small)
↓
Best for: General surveillance
Trade-off: Perfect speed/accuracy mix
```

### For High Accuracy
```
yolov8m.pt or yolov8l.pt
↓
Best for: Critical security
Trade-off: Slower, needs good GPU
```

### For Maximum Precision
```
yolov8x.pt (xlarge)
↓
Best for: Expert analysis
Trade-off: Slow, requires GPU with 6GB+ VRAM
```

---

## 📋 Checklist for Setup

- [ ] Download models: `python download_advanced_models.py`
- [ ] Copy `.env.example` to `.env` (if exists)
- [ ] Edit `.env` with persistence settings
- [ ] Test camera: `CAMERA_SOURCE=0` (or your camera)
- [ ] Start system: `python start.py`
- [ ] Open browser: `http://localhost:5000`
- [ ] Test detection with object
- [ ] Check console for logs
- [ ] Verify screenshots saved
- [ ] Verify alerts sent (SMS/Email)

---

## 📞 Quick Help

**Full Documentation:** `THREAT_PERSISTENCE_GUIDE.md`  
**Quick Start:** `QUICKSTART_ENHANCED.md`  
**Implementation:** `IMPLEMENTATION_SUMMARY.md`  

---

## 💾 File Locations

```
project-alice-v8/
├── models/                          # Model directory
│   ├── yolov8n.pt                  # Nano model
│   ├── yolov8s.pt                  # Small model
│   ├── ppe_*.pt                     # PPE models
│   ├── weapon_*.pt                  # Weapon models
│   └── ...
├── data/
│   └── screenshots/                # Logged screenshots
├── app/
│   ├── web/
│   │   ├── stream.py               # ✅ UPDATED (persistence)
│   │   ├── routes.py               # ✅ UPDATED
│   │   └── db.py
│   ├── config.py                   # ✅ UPDATED
│   └── detection/
└── download_advanced_models.py      # ✅ UPDATED (19+ models)
```

---

## 🔑 Key Parameters Summary

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| `MIN_THREAT_DURATION` | 0.5s | 0.1-5.0s | Threat detection persistence |
| `MIN_PPE_DURATION` | 1.0s | 0.3-5.0s | PPE violation persistence |
| `THREAT_THRESHOLD` | 0.55 | 0.3-0.9 | Detection confidence |
| `THREAT_ALERT_COOLDOWN` | 30s | 10-120s | Alert rate limiting |
| `PPE_ALERT_COOLDOWN` | 60s | 30-180s | PPE alert rate limiting |

---

**Last Updated:** 2026-05-04  
**Status:** ✅ Production Ready
