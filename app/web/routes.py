from flask import Blueprint, render_template, Response, current_app, send_file, request, jsonify
from app.web.stream import Streamer
from app.web.db import LogStore
from app.web.alerts import AlertManager
import os
import base64

web_bp = Blueprint("web", __name__)
_logger = LogStore()
_alerter = AlertManager()
_streamer = None

@web_bp.route("/")
def index():
    return render_template("index.html")

@web_bp.route("/video")
def video():
    global _streamer
    if _streamer is None:
        _streamer = Streamer(current_app.config["CAMERA_SOURCE"],
                             current_app.config["THREAT_THRESHOLD"])
    return Response(_streamer.frame_generator(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@web_bp.route("/logs")
def logs():
    events = _logger.get_events(limit=50)
    return render_template("logs.html", events=events)

@web_bp.route("/sos")
def sos():
    _alerter.send_manual_sos("Manual SOS triggered from dashboard.")
    return render_template("sos_confirmation.html")

@web_bp.route("/screenshot/<int:event_id>")
def get_screenshot(event_id):
    image_path = _logger.get_image_path(event_id)
    if image_path:
        # Convert to absolute path
        if not os.path.isabs(image_path):
            image_path = os.path.abspath(image_path)
        
        print(f"[DEBUG] Serving screenshot: {image_path}")
        print(f"[DEBUG] File exists: {os.path.exists(image_path)}")
        
        if os.path.exists(image_path):
            try:
                return send_file(image_path, mimetype="image/jpeg")
            except Exception as e:
                print(f"[ERROR] Failed to send file: {e}")
                return f"Error serving file: {e}", 500
    
    print(f"[DEBUG] Screenshot not found for event_id: {event_id}")
    return "Screenshot not found", 404

@web_bp.route("/screenshot-base64/<int:event_id>")
def get_screenshot_base64(event_id):
    """Serve screenshot as base64 encoded data URI"""
    image_path = _logger.get_image_path(event_id)
    if image_path:
        if not os.path.isabs(image_path):
            image_path = os.path.abspath(image_path)
        
        print(f"[DEBUG] Serving base64 screenshot: {image_path}")
        
        if os.path.exists(image_path):
            try:
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                return jsonify({"image": f"data:image/jpeg;base64,{image_data}"})
            except Exception as e:
                print(f"[ERROR] Failed to encode image: {e}")
                return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Screenshot not found"}), 404

@web_bp.route("/send-alert", methods=["POST"])
def send_alert():
    data = request.get_json()
    event_id = data.get("event_id")
    labels = data.get("labels")
    score = data.get("score")
    image_path = _logger.get_image_path(event_id)
    
    success = _alerter.send_alert_with_screenshot(labels, score, image_path)
    return jsonify({"message": "Alert sent successfully!" if success else "Alert send failed."}), 200 if success else 500
